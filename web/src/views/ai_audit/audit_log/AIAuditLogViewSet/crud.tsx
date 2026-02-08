import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { auth } from '/@/utils/authFunction';
import { ElMessage, ElMessageBox } from 'element-plus';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 此处为crudOptions配置
export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context: any }): CreateCrudOptionsRet {

	// 获取AI审核记录列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑AI审核记录
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	// 删除AI审核记录
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加AI审核记录
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	return {
		crudOptions: {
			...listPageDefSingleLineCfg,
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			actionbar: {
				buttons: {
					add: {
						text: '上传并审核',
						title: '上传文件并触发AI审核',
						type: 'primary',
						icon: 'Upload',
						show: auth('AIAuditLogViewSet:Create'),
						click() {
							// 打开上传抽屉
							context.openUploadDrawer();
						},
					},
					export: {
						text: '导出',
						title: '导出数据',
						type: 'default',
						show: auth('AIAuditLogViewSet:Export'),
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
				},
			},
			rowHandle: {
				width: 200,
				fixed: 'right',
				buttons: {
					view: {
						show: auth('AIAuditLogViewSet:Retrieve'),
					},
					edit: {
						show: auth('AIAuditLogViewSet:Update'),
					},
					remove: {
						show: auth('AIAuditLogViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列（跨页连续编号）
				_index: getIndexColumnConfig(crudExpose),

				// 审核编号
				audit_no: {
					title: '审核编号',
					type: 'text',
					search: {
						show: true,
						component: {
							placeholder: '请输入审核编号',
						},
					},
					column: {
						minWidth: 180,
						sortable: 'custom',
					},
					form: {
						show: false, // 自动生成，不需要手动填写
					},
				},

				// 审核来源
				audit_source: {
					title: '审核来源',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '关联订单审核', value: 1, color: 'primary' },
							{ label: '独立审核', value: 2, color: 'success' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						component: {
							name: 'fs-dict-select',
							color: 'auto',
						},
					},
					form: {
						rules: [{ required: true, message: '请选择审核来源' }],
						component: {
							placeholder: '请选择审核来源',
						},
					},
				},

				// 文件名称
				file_name: {
					title: '文件名称',
					type: 'text',
					search: {
						show: true,
						component: {
							placeholder: '请输入文件名称',
						},
					},
					column: {
						minWidth: 200,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入文件名称',
						},
					},
				},

				// 文件路径
				file_path: {
					title: '文件路径',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 250,
						show: false,
					},
					form: {
						rules: [{ required: true, message: '请输入文件路径' }],
						component: {
							placeholder: '请输入文件路径',
						},
					},
				},

				// 审核类型
				audit_type: {
					title: '审核类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '画面内容审核', value: 1, color: 'primary' },
							{ label: '证明文件审核', value: 2, color: 'warning' },
							{ label: '综合审核', value: 3, color: 'success' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						component: {
							name: 'fs-dict-select',
							color: 'auto',
						},
					},
					form: {
						rules: [{ required: true, message: '请选择审核类型' }],
						component: {
							placeholder: '请选择审核类型',
						},
					},
				},

				// AI判定结果
				ai_conclusion: {
					title: 'AI判定结果',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '通过', value: 1, color: 'success' },
							{ label: '疑似违规', value: 2, color: 'warning' },
							{ label: '明确违规', value: 3, color: 'danger' },
							{ label: '审核失败', value: 4, color: 'info' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
						component: {
							name: 'fs-dict-select',
							color: 'auto',
						},
					},
					form: {
						rules: [{ required: true, message: '请选择AI判定结果' }],
						component: {
							placeholder: '请选择AI判定结果',
						},
					},
				},

				// 综合风险等级
				risk_level: {
					title: '风险等级',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '无风险', value: 1, color: 'success' },
							{ label: '低风险', value: 2, color: 'primary' },
							{ label: '中风险', value: 3, color: 'warning' },
							{ label: '高风险', value: 4, color: 'danger' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						component: {
							name: 'fs-dict-select',
							color: 'auto',
						},
					},
					form: {
						component: {
							placeholder: '请选择风险等级',
						},
					},
				},

				// 综合置信度
				confidence_score: {
					title: '置信度',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}%` : '-';
						},
					},
					form: {
						component: {
							min: 0,
							max: 100,
							placeholder: '请输入置信度(0-100)',
						},
					},
				},

				// 是否需人工复核
				need_manual_review: {
					title: '需人工复核',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '否', value: false, color: 'success' },
							{ label: '是', value: true, color: 'warning' },
						],
					}),
					column: {
						minWidth: 110,
						sortable: 'custom',
						component: {
							name: 'fs-dict-select',
							color: 'auto',
						},
					},
					form: {
						value: false,
						component: {
							placeholder: '是否需要人工复核',
						},
					},
				},

				// AI审核总结
				summary: {
					title: 'AI审核总结',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 300,
						sortable: false,
						component: {
							ellipsis: true,
							showOverflowTooltip: true,
						},
					},
					form: {
						component: {
							rows: 5,
							placeholder: 'AI审核的综合总结说明',
							readonly: true,
						},
					},
					valueResolve({ value }) {
						// 在详情/编辑页面显示完整内容
						return value || '-';
					},
				},

				// 调用平台
				platform: {
					title: '调用平台',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 130,
						show: false,
					},
					form: {
						value: '阿里百炼',
						component: {
							disabled: true,
						},
					},
				},

				// 请求时间
				request_time: {
					title: '请求时间',
					type: 'datetime',
					search: {
						show: true,
						component: {
							type: 'datetimerange',
							valueFormat: 'YYYY-MM-DD HH:mm:ss',
						},
					},
					column: {
						minWidth: 160,
						sortable: 'custom',
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						show: false, // 自动生成
					},
				},

				// 响应时间
				response_time: {
					title: '响应时间',
					type: 'datetime',
					search: { show: false },
					column: {
						minWidth: 160,
						sortable: 'custom',
						show: false,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						show: false,
					},
				},

				// 耗时(秒)
				duration_seconds: {
					title: '耗时(秒)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}s` : '-';
						},
					},
					form: {
						show: false, // 自动计算
					},
				},

				// 错误信息
				error_message: {
					title: '错误信息',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						show: false,
					},
					form: {
						component: {
							rows: 3,
							placeholder: '审核失败时的错误信息',
						},
					},
				},

				// 关联材料ID
				material_id: {
					title: '关联材料ID',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						show: false,
					},
					form: {
						component: {
							placeholder: '关联订单审核时填写',
						},
					},
				},

				// 上刊订单ID
				order_id: {
					title: '上刊订单ID',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						show: false,
					},
					form: {
						component: {
							placeholder: '关联订单审核时填写',
						},
					},
				},

				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					search: { show: false },
					column: {
						minWidth: 160,
						sortable: 'custom',
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
						show: false,
					},
					form: {
						show: false,
					},
				},

				// 更新时间
				update_datetime: {
					title: '更新时间',
					type: 'datetime',
					search: { show: false },
					column: {
						minWidth: 160,
						sortable: 'custom',
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
						show: false,
					},
					form: {
						show: false,
					},
				},

				// 创建人
				creator_name: {
					title: '创建人',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						show: false,
					},
					form: {
						show: false,
					},
				},
			},
		},
	};
}
