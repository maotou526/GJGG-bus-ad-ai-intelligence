import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig, getCompanySelectorConfig } from '/@/utils/commonCrud';
import { CreateFlow } from '/@/views/plugins/bs-workflow/api/process'; // Import CreateFlow
import { ElMessageBox, ElMessage } from 'element-plus';
import { useUserInfo } from '/@/stores/userInfo';

//此处为crudOptions配置
export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context?: any }): CreateCrudOptionsRet {
    const userStore = useUserInfo();
	// 获取线路列表
	const pageRequest = async (query: any) => {
		// 设置默认排序：按照所属公司、车队、线路名称进行排序
		if (!query.ordering) {
			query.ordering = 'company_name,branch,line_name';
		}
		return await api.GetList(query);
	};

	// 编辑线路
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		return await api.UpdateObj(form);
	};

	// 删除线路
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加线路
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	return {
		crudOptions: {
			...listPageDefMultiLineCfg,
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			// 搜索配置
			// search: {
			// 	container: {
			// 		collapse: true, //是否展开，你布局组件中定义的props
			// 		action: {
			// 			label: '操作', //查询按钮前缀
			// 			col: { span: 4 }, //查询按钮所占格子宽度
			// 		},
			// 		col: { span: 4 }, // 默认列宽度配置
			// 		collapseButton: {
			// 			//展开按钮配置
			// 			// fs-button 属性
			// 		},
			// 	},
			// },
			form: {
				col: { span: 12 },
				labelWidth: '80px',
				wrapper: {
					is: 'el-dialog',
					width: '800px',
					closeOnClickModal: false, // 禁用点击空白处关闭弹窗
				},
			},
			actionbar: {
				buttons: {
					export: {
						// 注释编号:django-vue3-admin-crud210716:注意这个auth里面的值，最好是使用index.vue文件里面的name值并加上请求动作的单词
						show: auth('RoadlineModelViewSet:Export'),
						text: '导出', //按钮文字
						title: '导出', //鼠标停留显示的信息
						click() {
							return exportRequest(crudExpose.getSearchFormData());
							// return exportRequest(crudExpose!.getSearchFormData())    // 注意这个crudExpose!.getSearchFormData()，一些低版本的环境是需要添加!的
						},
					},
					add: {
						show: auth('RoadlineModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width: 260,
				buttons: {
					detail: {
						text: '线路详情',
						type: 'text',
						order: 1,
						show: true,
						click: ({ row }: { row: any }) => {
							// 调用 index.vue 中的 openDetailDialog 方法，传入线路信息
							if (context?.openDetailDialog) {
								context.openDetailDialog(row);
							}
						}
					},
					view: {
						type: 'text',
						order: 2,
						show: auth('RoadlineModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 3,
						show: auth('RoadlineModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 6,
						show: auth('RoadlineModelViewSet:Delete'),
					},
                    viewForm: {
                        text: '表单预览',
                        type: 'text',
                        order: 4,
                        show: true,
                        click: ({ row }: { row: any }) => {
                            // 调用 index.vue 中的 openFormDialog 方法，传入 id
                            if (context?.openFormDialog) {
                                context.openFormDialog(row.id);
                            }
                        }
                    },
                    startFlow: {
                        text: '发起流程',
                        type: 'text',
                        order: 5,
                        show: false, // 隐藏发起流程按钮
                        click: async ({ row }) => {
                            try {
                                await ElMessageBox.confirm('是否确认发起流程?', '提示', {
                                    confirmButtonText: '确定',
                                    cancelButtonText: '取消',
                                    type: 'warning',
                                });

                                const loading = ElMessage.success({
                                    message: '流程发起中...',
                                    duration: 0,
                                });

                                const postData = {
                                    schemeCode: "Test0129", // Adapted scheme code
                                    processId: row.id,
                                    title: `线路流程-${row.line_name}`,
                                    level: "0",
                                    auditors: null,
                                    createUserId: userStore.userInfos.id,
                                };

                                await CreateFlow(postData).then((res: any) => {
                                    loading.close();
                                    if (res.code === 2000) {
                                        ElMessage.success(res.msg || '流程发起成功');
                                        crudExpose.doRefresh();
                                    } else {
                                        ElMessage.error(res.msg || '流程发起失败');
                                    }
                                }).catch((err: any) => {
                                      loading.close();
                                      // ElMessage.error('请求失败');
                                });

                            } catch (e) {
                                // Cancelled
                            }
                        }
                    }
				},
			},
			columns: {
				// 序号列（跨页连续编号）
				_index: getIndexColumnConfig(crudExpose),
			// 所属公司
			company_belong_id: {
				...getCompanySelectorConfig({
					crudExpose,
					onChange: async (value: any, row: any, context: any, crudExpose: any) => {
						if (context?.form) {
							if (value && row) {
								context.form.company_code = row?.encode ?? '';
								context.form.company_name = row?.shortname ?? '';
							} else {
								context.form.company_code = '';
								context.form.company_name = '';
							}
						}
					},
				}),
				search: { show: true },
			},
				// 车队
				branch: {
					title: '车队',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 140,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入车队',
						},
					},
				},
				// 线路名称
				line_name: {
					title: '线路名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 100,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '线路名称必填' }],
						component: {
							placeholder: '请输入线路名称',
						},
					},
				},
				// 企业线路编码
				normal_code: {
					title: '企业线路编码',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入企业线路编码',
						},
					},
				},
				// 行业线路编号
				ygc_code: {
					title: '行业线路编号',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入行业线路编号',
						},
					},
				},
				// 线路长度
				line_length: {
					title: '线路长度(km)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 110,
						sortable: 'custom',
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}km` : '-';
						},
					},
					form: {
						component: {
							placeholder: '请输入线路长度',
							precision: 2,
						},
					},
				},
				// 线路类型
				line_type: {
					title: '线路类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 0, label: '普通' },
							{ value: 1, label: '挂牌线' },
							{ value: 2, label: '区间' },
							{ value: 3, label: '同名区间' },
							{ value: 4, label: '定班线' },
							{ value: 5, label: '定制公交' },
							{ value: 6, label: '高峰线' },
							{ value: 7, label: '夜宵线' },
							{ value: 8, label: '低谷定班线' },
						],
					}),
					column: {
						minWidth: 120,
						// sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请选择线路类型',
						},
					},
				},
				// 售票方式
				sell_type: {
					title: '售票方式',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '无人售票' },
							{ value: 2, label: '有人售票' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请选择售票方式',
						},
					},
				},
				// 票价类型
				ticket_price_type: {
					title: '票价类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '单一票价' },
							{ value: 2, label: '多级票价' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请选择票价类型',
						},
					},
				},
				// 票价
				ticket_price: {
					title: '票价(元)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
						formatter: (context: any) => {
							const value = context.value;
							return value ? `¥${value}` : '-';
						},
					},
					form: {
						component: {
							placeholder: '请输入票价',
							precision: 2,
						},
					},
				},
				// 运营时段分类
				yy_type: {
					title: '运营时段分类',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '全日线' },
							{ value: 2, label: '高峰线' },
							{ value: 3, label: '夜宵线' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请选择运营时段分类',
						},
					},
				},
				// 挂牌类型
				listing_type: {
					title: '挂牌类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '无挂牌' },
							{ value: 2, label: '全日挂牌' },
							{ value: 3, label: '高峰挂牌' },
						],
					}),
					column: {
						minWidth: 140,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请选择挂牌类型',
						},
					},
				},
				// 定班类型
				schedule_type: {
					title: '定班类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '无定班' },
							{ value: 2, label: '定班线' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请选择定班类型',
						},
					},
				},
				// 启用状态
				enabled_mark: {
					title: '启用状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '启用' },
							{ value: 0, label: '禁用' },
						],
					}),
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请选择启用状态',
						},
					},
				},
				// 线路状态
				line_status: {
					title: '线路状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: '正常运营', label: '正常运营' },
							{ value: '停运', label: '停运' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: false,
					},
					form: {
						component: {
							placeholder: '请选择线路状态',
						},
					},
				},
				// 配车数
				bus_count: {
					title: '配车数',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入配车数',
							min: 0,
							precision: 0,
						},
					},
				},
				// 广告车辆数
				ad_bus_count: {
					title: '广告车辆数',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入广告车辆数',
							min: 0,
							precision: 0,
						},
					},
				},
				// 覆盖人群
				covered_population: {
					title: '覆盖人群',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 150,
						show: false, // 默认隐藏列
					},
					form: {
						component: {
							placeholder: '请输入覆盖人群，如：白领, 学生',
							rows: 3,
							maxLength: 500,
						},
					},
				},
				// 是否启用显示字段
				is_enabled: {
					title: '是否启用',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						show: false, // 隐藏列
						formatter: (context: any) => {
							const value = context.value;
							return value ? '是' : '否';
						},
					},
					form: { show: false }, // 表单中不显示
				},
				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					search: { show: false },
					column: {
						align: 'center',
						width: 160,
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
						align: 'center',
						width: 160,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						show: false,
					},
				},
			},
		},
	};
}
