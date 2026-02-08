# -*- coding: utf-8 -*-
import datetime
import re
from urllib.parse import quote

from django.db import transaction
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter, quote_sheetname
from openpyxl.worksheet.table import Table, TableStyleInfo
from rest_framework.decorators import action
from rest_framework.request import Request

from dvadmin.utils.import_export import import_to_data
from dvadmin.utils.json_response import DetailResponse, SuccessResponse
from dvadmin.utils.request_util import get_verbose_name
from dvadmin.system.tasks import async_export_data
from dvadmin.system.models import DownloadCenter


class ImportSerializerMixin:
    """
    自定义导入模板、导入功能
    """

    # 导入字段
    import_field_dict = {}
    # 导入序列化器
    import_serializer_class = None
    # 表格表头最大宽度，默认50个字符
    export_column_width = 50

    def is_number(self,num):
        try:
            float(num)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(num)
            return True
        except (TypeError, ValueError):
            pass
        return False

    def get_string_len(self, string):
        """
        获取字符串最大长度
        :param string:
        :return:
        """
        length = 4
        if string is None:
            return length
        if self.is_number(string):
            return length
        for char in string:
            length += 2.1 if ord(char) > 256 else 1
        return round(length, 1) if length <= self.export_column_width else self.export_column_width

    @action(methods=['get','post'],detail=False)
    @transaction.atomic  # Django 事务,防止出错
    def import_data(self, request: Request, *args, **kwargs):
        """
        导入模板
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        # 允许业务方单独配置“模板字段”，用于让模板/批量更新导出与列表展示列保持一致
        template_field_dict = getattr(self, "template_field_dict", None) or self.import_field_dict
        assert template_field_dict, "'%s' 请配置对应的导出模板字段。" % self.__class__.__name__
        # 导出模板
        if request.method == "GET":
            # 示例数据
            queryset = self.filter_queryset(self.get_queryset())
            # 导出excel 表
            response = HttpResponse(content_type="application/msexcel")
            response["Access-Control-Expose-Headers"] = f"Content-Disposition"
            response[
                "Content-Disposition"
            ] = f'attachment;filename={quote(str(f"导入{get_verbose_name(queryset)}模板.xlsx"))}'
            wb = Workbook()
            ws1 = wb.create_sheet("data", 1)
            ws1.sheet_state = "hidden"
            ws = wb.active
            row = get_column_letter(len(template_field_dict) + 1)
            column = 10
            header_data = [
                "序号",
            ]
            validation_data_dict = {}
            for index, ele in enumerate(template_field_dict.values()):
                if isinstance(ele, dict):
                    header_data.append(ele.get("title"))
                    choices = ele.get("choices", {})
                    if choices.get("data"):
                        data_list = []
                        data_list.extend(choices.get("data").keys())
                        validation_data_dict[ele.get("title")] = data_list
                    elif choices.get("queryset") and choices.get("values_name"):
                        data_list = choices.get("queryset").values_list(choices.get("values_name"), flat=True)
                        validation_data_dict[ele.get("title")] = list(data_list)
                    else:
                        continue
                    column_letter = get_column_letter(len(validation_data_dict))
                    dv = DataValidation(
                        type="list",
                        formula1=f"{quote_sheetname('data')}!${column_letter}$2:${column_letter}${len(validation_data_dict[ele.get('title')]) + 1}",
                        allow_blank=True,
                    )
                    ws.add_data_validation(dv)
                    dv.add(f"{get_column_letter(index + 2)}2:{get_column_letter(index + 2)}1048576")
                else:
                    header_data.append(ele)
            # 添加数据列
            ws1.append(list(validation_data_dict.keys()))
            for index, validation_data in enumerate(validation_data_dict.values()):
                for inx, ele in enumerate(validation_data):
                    ws1[f"{get_column_letter(index + 1)}{inx + 2}"] = ele
            # 插入导出模板正式数据
            df_len_max = [self.get_string_len(ele) for ele in header_data]
            ws.append(header_data)
            # 　更新列宽
            for index, width in enumerate(df_len_max):
                ws.column_dimensions[get_column_letter(index + 1)].width = width
            tab = Table(displayName="Table1", ref=f"A1:{row}{column}")  # 名称管理器
            style = TableStyleInfo(
                name="TableStyleLight11",
                showFirstColumn=True,
                showLastColumn=True,
                showRowStripes=True,
                showColumnStripes=True,
            )
            tab.tableStyleInfo = style
            ws.add_table(tab)
            wb.save(response)
            return response
        else:
            # 从excel中组织对应的数据结构，然后使用序列化器保存
            queryset = self.filter_queryset(self.get_queryset())
            # 获取多对多字段
            m2m_fields = [
                ele.name
                for ele in queryset.model._meta.get_fields()
                if hasattr(ele, "many_to_many") and ele.many_to_many == True
            ]
            import_field_dict = {'id':'更新主键(勿改)',**template_field_dict}
            data = import_to_data(request.data.get("url"), import_field_dict, m2m_fields)
            
            # 收集验证失败的数据
            failed_data = []
            success_count = 0
            
            for index, ele in enumerate(data, start=2):  # Excel行号从2开始（第1行是表头）
                filter_dic = {'id':ele.get('id')}
                instance = filter_dic and queryset.filter(**filter_dic).first()
                serializer = self.import_serializer_class(instance, data=ele, request=request)
                
                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    success_count += 1
                except Exception as e:
                    # 收集验证失败的数据和错误原因
                    error_msg = str(e)
                    # 如果是DRF验证错误，提取更友好的错误信息
                    if hasattr(e, 'detail'):
                        if isinstance(e.detail, dict):
                            error_list = []
                            for field, errors in e.detail.items():
                                if isinstance(errors, list):
                                    # 提取ErrorDetail对象中的字符串部分
                                    error_messages = []
                                    for err in errors:
                                        if hasattr(err, 'string'):
                                            # ErrorDetail对象，提取string属性
                                            error_messages.append(str(err.string))
                                        else:
                                            error_messages.append(str(err))
                                    if error_messages:
                                        # 如果是 non_field_errors，不显示字段名，只显示错误信息
                                        if field == 'non_field_errors':
                                            error_list.extend(error_messages)
                                        else:
                                            error_list.extend([f"{field}: {msg}" for msg in error_messages])
                                else:
                                    # 单个错误，可能是ErrorDetail对象
                                    if hasattr(errors, 'string'):
                                        # 如果是 non_field_errors，不显示字段名，只显示错误信息
                                        if field == 'non_field_errors':
                                            error_list.append(errors.string)
                                        else:
                                            error_list.append(f"{field}: {errors.string}")
                                    else:
                                        # 如果是 non_field_errors，不显示字段名，只显示错误信息
                                        if field == 'non_field_errors':
                                            error_list.append(str(errors))
                                        else:
                                            error_list.append(f"{field}: {errors}")
                            error_msg = "; ".join(error_list) if error_list else str(e)
                        elif isinstance(e.detail, list):
                            # 如果是列表形式的错误（如ValidationError直接抛出）
                            error_messages = []
                            for err in e.detail:
                                if hasattr(err, 'string'):
                                    # ErrorDetail对象，提取string属性
                                    error_messages.append(str(err.string))
                                else:
                                    error_messages.append(str(err))
                            error_msg = "; ".join(error_messages) if error_messages else str(e)
                        else:
                            # 单个ErrorDetail对象或其他类型
                            if hasattr(e.detail, 'string'):
                                error_msg = str(e.detail.string)
                            else:
                                error_msg = str(e.detail)
                    # 如果错误信息中包含ErrorDetail的字符串表示，尝试提取纯文本
                    # 处理类似 "[ErrorDetail(string='错误信息', code='invalid')]" 的情况
                    if 'ErrorDetail' in error_msg and 'string=' in error_msg:
                        # 使用正则表达式提取 string='...' 中的内容
                        matches = re.findall(r"string='([^']*)'", error_msg)
                        if matches:
                            error_msg = "; ".join(matches)
                    
                    failed_row = ele.copy()
                    failed_row['错误原因'] = error_msg
                    failed_row['行号'] = index
                    failed_data.append(failed_row)
            
            # 如果有验证失败的数据，生成错误报告Excel并返回
            if failed_data:
                # 生成错误报告Excel
                response = HttpResponse(content_type="application/msexcel")
                response["Access-Control-Expose-Headers"] = f"Content-Disposition"
                response["Content-Disposition"] = f'attachment;filename={quote(str(f"导入失败数据报告.xlsx"))}'
                wb = Workbook()
                ws = wb.active
                
                # 构建表头（包含原始字段和错误原因列）
                header_data = ["行号"]
                for key in import_field_dict.keys():
                    if isinstance(import_field_dict[key], dict):
                        header_data.append(import_field_dict[key].get('title', key))
                    else:
                        header_data.append(import_field_dict[key])
                header_data.append("错误原因")
                ws.append(header_data)
                
                # 填充失败数据
                for failed_row in failed_data:
                    row_data = [failed_row.get('行号', '')]
                    for key in import_field_dict.keys():
                        row_data.append(failed_row.get(key, ''))
                    row_data.append(failed_row.get('错误原因', ''))
                    ws.append(row_data)
                
                # 设置列宽
                for index, width in enumerate([self.get_string_len(str(h)) for h in header_data]):
                    ws.column_dimensions[get_column_letter(index + 1)].width = width
                
                wb.save(response)
                # 返回Excel文件，状态码400表示有错误
                response.status_code = 400
                return response
            
            return DetailResponse(msg=f"导入成功！共导入 {success_count} 条数据。")

    @action(methods=['get'],detail=False)
    def update_template(self,request):
        queryset = self.filter_queryset(self.get_queryset())
        template_field_dict = getattr(self, "template_field_dict", None) or self.import_field_dict
        template_serializer_class = getattr(self, "template_serializer_class", None) or self.import_serializer_class
        assert template_field_dict, "'%s' 请配置对应的导入模板字段。" % self.__class__.__name__
        assert template_serializer_class, "'%s' 请配置对应的导入序列化器。" % self.__class__.__name__
        data = template_serializer_class(queryset, many=True, request=request).data
        # 导出excel 表
        response = HttpResponse(content_type="application/msexcel")
        response["Access-Control-Expose-Headers"] = f"Content-Disposition"
        response["content-disposition"] = f'attachment;filename={quote(str(f"导出{get_verbose_name(queryset)}.xlsx"))}'
        wb = Workbook()
        ws1 = wb.create_sheet("data", 1)
        ws1.sheet_state = "hidden"
        ws = wb.active
        import_field_dict = {}
        header_data = ["序号","更新主键(勿改)"]
        hidden_header = ["#","id"]
        #----设置选项----
        validation_data_dict = {}
        # 反向映射：用于把序列化器里的值（如 0/1）转换成中文（如 禁用/启用）
        reverse_choice_map = {}
        for index, item in enumerate(template_field_dict.items()):
            items = list(item)
            key = items[0]
            value = items[1]
            if isinstance(value, dict):
                header_data.append(value.get("title"))
                hidden_header.append(key)  # 使用字段名匹配序列化器数据
                choices = value.get("choices", {})
                if choices.get("data"):
                    data_list = []
                    data_list.extend(choices.get("data").keys())
                    validation_data_dict[value.get("title")] = data_list
                    # data 结构是 {label: value}，这里转成 {value: label} 用于导出显示
                    reverse_choice_map[key] = {v: k for k, v in choices.get("data").items()}
                elif choices.get("queryset") and choices.get("values_name"):
                    data_list = choices.get("queryset").values_list(choices.get("values_name"), flat=True)
                    validation_data_dict[value.get("title")] = list(data_list)
                else:
                    continue
                column_letter = get_column_letter(len(validation_data_dict))
                dv = DataValidation(
                    type="list",
                    formula1=f"{quote_sheetname('data')}!${column_letter}$2:${column_letter}${len(validation_data_dict[value.get('title')]) + 1}",
                    allow_blank=True,
                )
                ws.add_data_validation(dv)
                dv.add(f"{get_column_letter(index + 3)}2:{get_column_letter(index + 3)}1048576")
            else:
                header_data.append(value)
                hidden_header.append(key)
        # 添加数据列
        ws1.append(list(validation_data_dict.keys()))
        for index, validation_data in enumerate(validation_data_dict.values()):
            for inx, ele in enumerate(validation_data):
                ws1[f"{get_column_letter(index + 1)}{inx + 2}"] = ele
        #--------
        df_len_max = [self.get_string_len(ele) for ele in header_data]
        row = get_column_letter(len(hidden_header) + 1)
        column = 1
        ws.append(header_data)
        for index, results in enumerate(data):
            results_list = []
            for h_index, h_item in enumerate(hidden_header):
                for key, val in results.items():
                    if key == h_item:
                        if val is None or val == "":
                            results_list.append("")
                        elif isinstance(val,list):
                            results_list.append(str(val))
                        else:
                            # 如果该字段有 choices.data，导出时优先显示中文 label
                            if h_item in reverse_choice_map:
                                # 先尝试直接匹配（支持整数和字符串）
                                mapped = reverse_choice_map[h_item].get(val, None)
                                # 如果是字符串数字，尝试转换为整数再匹配
                                if mapped is None and isinstance(val, str) and val.isdigit():
                                    mapped = reverse_choice_map[h_item].get(int(val), None)
                                # 如果是整数，也尝试字符串形式匹配
                                if mapped is None and isinstance(val, int):
                                    mapped = reverse_choice_map[h_item].get(str(val), None)
                                # 如果匹配成功，使用中文 label；否则使用原值
                                if mapped is not None:
                                    results_list.append(mapped)
                                else:
                                    results_list.append(val)
                            else:
                                results_list.append(val)
                        # 计算最大列宽度
                        if isinstance(val,str):
                            result_column_width = self.get_string_len(val)
                            if h_index != 0 and result_column_width > df_len_max[h_index]:
                                df_len_max[h_index] = result_column_width
            ws.append([index+1,*results_list])
            column += 1
        # 　更新列宽
        for index, width in enumerate(df_len_max):
            ws.column_dimensions[get_column_letter(index + 1)].width = width
        tab = Table(displayName="Table", ref=f"A1:{row}{column}")  # 名称管理器
        style = TableStyleInfo(
            name="TableStyleLight11",
            showFirstColumn=True,
            showLastColumn=True,
            showRowStripes=True,
            showColumnStripes=True,
        )
        tab.tableStyleInfo = style
        ws.add_table(tab)
        wb.save(response)
        return response


class ExportSerializerMixin:
    """
    自定义导出功能
    """

    # 导出字段
    export_field_label = []
    # 导出序列化器
    export_serializer_class = None
    # 表格表头最大宽度，默认50个字符
    export_column_width = 50

    def is_number(self,num):
        try:
            float(num)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(num)
            return True
        except (TypeError, ValueError):
            pass
        return False

    def get_string_len(self, string):
        """
        获取字符串最大长度
        :param string:
        :return:
        """
        length = 4
        if string is None:
            return length
        if self.is_number(string):
            return length
        for char in string:
            length += 2.1 if ord(char) > 256 else 1
        return round(length, 1) if length <= self.export_column_width else self.export_column_width

    @action(methods=['get'],detail=False)
    def export_data(self, request: Request, *args, **kwargs):
        """
        导出功能
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        queryset = self.filter_queryset(self.get_queryset())
        assert self.export_field_label, "'%s' 请配置对应的导出模板字段。" % self.__class__.__name__
        assert self.export_serializer_class, "'%s' 请配置对应的导出序列化器。" % self.__class__.__name__
        data = self.export_serializer_class(queryset, many=True, request=request).data
        try:
            async_export_data.delay(
                data,
                str(f"导出{get_verbose_name(queryset)}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"),
                DownloadCenter.objects.create(creator=request.user, task_name=f'{get_verbose_name(queryset)}数据导出任务', dept_belong_id=request.user.dept_id).pk,
                self.export_field_label
            )
            return SuccessResponse(msg="导入任务已创建，请前往‘下载中心’等待下载")
        except:
            pass
        # 导出excel 表
        response = HttpResponse(content_type="application/msexcel")
        response["Access-Control-Expose-Headers"] = f"Content-Disposition"
        response["content-disposition"] = f'attachment;filename={quote(str(f"导出{get_verbose_name(queryset)}.xlsx"))}'
        wb = Workbook()
        ws = wb.active
        header_data = ["序号", *self.export_field_label.values()]
        hidden_header = ["#", *self.export_field_label.keys()]
        df_len_max = [self.get_string_len(ele) for ele in header_data]
        row = get_column_letter(len(self.export_field_label) + 1)
        column = 1
        ws.append(header_data)
        for index, results in enumerate(data):
            results_list = []
            for h_index, h_item in enumerate(hidden_header):
                for key,val in results.items():
                    if key == h_item:
                        if val is None or val=="":
                            results_list.append("")
                        else:
                            results_list.append(val)
                        # 计算最大列宽度
                        result_column_width = self.get_string_len(val)
                        if h_index !=0 and result_column_width > df_len_max[h_index]:
                            df_len_max[h_index] = result_column_width
            ws.append([index + 1, *results_list])
            column += 1
        # 　更新列宽
        for index, width in enumerate(df_len_max):
            ws.column_dimensions[get_column_letter(index + 1)].width = width
        tab = Table(displayName="Table", ref=f"A1:{row}{column}")  # 名称管理器
        style = TableStyleInfo(
            name="TableStyleLight11",
            showFirstColumn=True,
            showLastColumn=True,
            showRowStripes=True,
            showColumnStripes=True,
        )
        tab.tableStyleInfo = style
        ws.add_table(tab)
        wb.save(response)
        return response
