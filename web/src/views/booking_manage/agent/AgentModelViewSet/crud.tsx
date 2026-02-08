import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import { CreateFlow } from '/@/views/plugins/bs-workflow/api/process'; // Import CreateFlow
import { ElMessageBox, ElMessage } from 'element-plus';
import { useUserInfo } from '/@/stores/userInfo';

//此处为crudOptions配置
export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context?: any }): CreateCrudOptionsRet {
	const userStore = useUserInfo();
	// 获取代理商列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑代理商
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 处理日期字段，确保提交纯日期格式
		if (form.established_date && typeof form.established_date === 'string') {
			form.established_date = form.established_date.split(' ')[0];
		}
		if (form.contract_start_date && typeof form.contract_start_date === 'string') {
			form.contract_start_date = form.contract_start_date.split(' ')[0];
		}
		if (form.contract_end_date && typeof form.contract_end_date === 'string') {
			form.contract_end_date = form.contract_end_date.split(' ')[0];
		}

		return await api.UpdateObj(form);
	};

	// 删除代理商
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加代理商
	const addRequest = async ({ form }: AddReq) => {
		// 处理日期字段
		if (form.established_date && typeof form.established_date === 'string') {
			form.established_date = form.established_date.split(' ')[0];
		}
		if (form.contract_start_date && typeof form.contract_start_date === 'string') {
			form.contract_start_date = form.contract_start_date.split(' ')[0];
		}
		if (form.contract_end_date && typeof form.contract_end_date === 'string') {
			form.contract_end_date = form.contract_end_date.split(' ')[0];
		}

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
			form: {
				col: { span: 12 }, // 左右各占50%宽度（每列50%）
				labelWidth: '180px', // 统一label宽度（适应最长的label）
				labelAlign: 'left', // label文字左对齐
				wrapper: {
					is: 'el-dialog',
					width: '1300px', // 增加对话框宽度以适应更宽的label
					closeOnClickModal: false,
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('AgentModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('AgentModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 260,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('AgentModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('AgentModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('AgentModelViewSet:Delete'),
					},
					startFlow: {
						text: '发起流程',
						type: 'text',
						order: 4,
						show: true, // 隐藏发起流程按钮
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
									title: `代理商流程-${row.company_name}`,
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
				// 序号列
				_index: getIndexColumnConfig(crudExpose),
				
				// 代理商编码
				agent_code: {
					title: '代理商编码',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '代理商编码必填' }],
						component: {
							placeholder: '请输入代理商编码，如：AG-20250101-0001',
						},
						helper: '留空将自动生成',
					},
				},

				// 公司名称
				company_name: {
					title: '公司名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 200,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '公司名称必填' }],
						component: {
							placeholder: '请输入代理商公司全称',
						},
					},
				},

				// 统一社会信用代码
				credit_code: {
					title: '统一社会信用代码',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 180,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入统一社会信用代码（18位）',
							maxlength: 18,
						},
					},
				},

				// 法定代表人
				legal_person: {
					title: '法定代表人',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入法人姓名',
						},
					},
				},

				// 注册资本
				registered_capital: {
					title: '注册资本(万元)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}万元` : '-';
						},
					},
					form: {
						component: {
							placeholder: '请输入注册资本',
							precision: 2,
						},
					},
				},

				// 成立日期
				established_date: {
					title: '成立日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 120,
						show: false,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择成立日期',
						},
					},
				},

				// 公司地址
				company_address: {
					title: '公司地址',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 200,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入详细地址',
						},
					},
				},

				// 联系电话
				contact_phone: {
					title: '联系电话',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 130,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入主要联系电话',
						},
					},
				},

				// 联系邮箱
				contact_email: {
					title: '联系邮箱',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 180,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入主要联系邮箱',
						},
					},
				},

				// 合作等级
				cooperation_level: {
					title: '合作等级',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: 'A级' },
							{ value: 2, label: 'B级' },
							{ value: 3, label: 'C级' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段cooperation_level_display显示
					},
					form: {
						rules: [{ required: true, message: '合作等级必填' }],
						value: 3, // 默认值：C级
						component: {
							placeholder: '请选择合作等级',
						},
					},
				},

				// 合作等级显示字段
				cooperation_level_display: {
					title: '合作等级',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},

				// 合同开始日期
				contract_start_date: {
					title: '合同开始日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择合同开始日期',
						},
					},
				},

				// 合同结束日期
				contract_end_date: {
					title: '合同结束日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择合同结束日期',
						},
					},
				},

				// 结算方式
				settlement_type: {
					title: '结算方式',
					type: 'dict-select',
					search: { show: false },
					dict: dict({
						data: [
							{ value: 1, label: '月结' },
							{ value: 2, label: '季结' },
							{ value: 3, label: '年结' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段settlement_type_display显示
					},
					form: {
						component: {
							placeholder: '请选择结算方式',
						},
					},
				},

				// 结算方式显示字段
				settlement_type_display: {
					title: '结算方式',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
						show: false,
					},
					form: { show: false },
				},

				// 开户银行
				bank_name: {
					title: '开户银行',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入结算银行名称',
						},
					},
				},

				// 银行账号
				bank_account: {
					title: '银行账号',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入结算账号',
						},
					},
				},

				// 业务负责人
				business_manager: {
					title: '业务负责人',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入广告公司侧对接人',
						},
					},
				},

				// 备注
				remark: {
					title: '备注',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入备注',
							rows: 4,
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
						show: false,
						formatter: (context: any) => {
							const value = context.value;
							return value ? '是' : '否';
						},
					},
					form: { show: false },
				},

				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					search: { show: false },
					column: {
						show: false,
						align: 'center',
						width: 160,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
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
						show: false,
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

