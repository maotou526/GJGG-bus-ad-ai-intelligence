import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref } from 'vue';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 代理商API前缀
const agentApiPrefix = '/api/AgentModelViewSet/';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 代理商列表
	const agentList: Ref<any[]> = ref([]);

	// 加载代理商列表
	const loadAgentList = async () => {
		try {
			const res = await request({
				url: agentApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				agentList.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: `${item.agent_code || ''} ${item.company_name || ''}`.trim() || `代理商ID:${item.id}`,
				}));
			}
		} catch (error) {
			console.error('加载代理商列表失败:', error);
		}
	};

	// 获取客户列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑客户
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 处理日期字段，确保提交纯日期格式
		if (form.first_cooperation_date && typeof form.first_cooperation_date === 'string') {
			form.first_cooperation_date = form.first_cooperation_date.split(' ')[0];
		}
		if (form.last_cooperation_date && typeof form.last_cooperation_date === 'string') {
			form.last_cooperation_date = form.last_cooperation_date.split(' ')[0];
		}

		return await api.UpdateObj(form);
	};

	// 删除客户
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加客户
	const addRequest = async ({ form }: AddReq) => {
		// 处理日期字段
		if (form.first_cooperation_date && typeof form.first_cooperation_date === 'string') {
			form.first_cooperation_date = form.first_cooperation_date.split(' ')[0];
		}
		if (form.last_cooperation_date && typeof form.last_cooperation_date === 'string') {
			form.last_cooperation_date = form.last_cooperation_date.split(' ')[0];
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
						show: auth('CustomerModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('CustomerModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 200,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('CustomerModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('CustomerModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 3,
						show: auth('CustomerModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),
				
				// 客户编码
				customer_code: {
					title: '客户编码',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '客户编码必填' }],
						component: {
							placeholder: '请输入客户编码，如：CU-20250101-0001',
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
							placeholder: '请输入客户公司全称',
						},
					},
				},

				// 数据归属代理商
				agent_id: {
					title: '数据归属代理商',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (agentList.value.length === 0) {
								await loadAgentList();
							}
							// 添加"自营客户"选项（值为null）
							return [
								{ value: null, label: '自营客户' },
								...agentList.value,
							];
						},
					}),
					column: {
						minWidth: 200,
						sortable: 'custom',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '自营客户';
							}
							// 从agentList中查找对应的label
							const agent = agentList.value.find((item: any) => item.value === value);
							return agent ? agent.label : `代理商ID:${value}`;
						},
					},
					form: {
						component: {
							placeholder: '请选择代理商（留空为自营客户）',
							filterable: true,
							clearable: true,
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

				// 行业分类
				industry: {
					title: '行业分类',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '快消' },
							{ value: 2, label: '金融' },
							{ value: 3, label: '地产' },
							{ value: 4, label: '互联网' },
							{ value: 5, label: '其他' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段industry_display显示
					},
					form: {
						component: {
							placeholder: '请选择行业分类',
						},
					},
				},

				// 行业分类显示字段
				industry_display: {
					title: '行业分类',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
						show: true,
					},
					form: { show: false },
				},

				// 行业标签
				industry_tags: {
					title: '行业标签',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入行业标签，多个标签用逗号分隔，如：食品,饮料',
						},
					},
				},

				// 联系人姓名
				contact_name: {
					title: '联系人姓名',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: true,
					},
					form: {
						component: {
							placeholder: '请输入主要联系人',
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
						show: true,
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

				// 客户等级
				customer_level: {
					title: '客户等级',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '重点客户' },
							{ value: 2, label: '普通客户' },
							{ value: 3, label: '潜在客户' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段customer_level_display显示
					},
					form: {
						component: {
							placeholder: '请选择客户等级',
						},
					},
				},

				// 客户等级显示字段
				customer_level_display: {
					title: '客户等级',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
						show: true,
					},
					form: { show: false },
				},

				// 状态
				status: {
					title: '状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '活跃' },
							{ value: 2, label: '休眠' },
							{ value: 3, label: '流失' },
						],
					}),
					column: {
						minWidth: 100,
						sortable: 'custom',
						align: 'left',
						show: false, // 隐藏，使用计算字段status_display显示
					},
					form: {
						rules: [{ required: true, message: '状态必填' }],
						value: 1, // 默认值：活跃
						component: {
							placeholder: '请选择状态',
						},
					},
				},

				// 状态显示字段
				status_display: {
					title: '状态',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
						show: true,
					},
					form: { show: false },
				},

				// 首次合作时间
				first_cooperation_date: {
					title: '首次合作时间',
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
							placeholder: '请选择首次合作时间',
						},
					},
				},

				// 最近合作时间
				last_cooperation_date: {
					title: '最近合作时间',
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
							placeholder: '请选择最近合作时间',
						},
					},
				},

				// 累计合作金额
				total_amount: {
					title: '累计合作金额(元)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						align: 'right',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							return `¥${Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
						},
					},
					form: {
						component: {
							placeholder: '请输入累计合作金额',
							precision: 2,
						},
					},
				},

				// 累计合作次数
				cooperation_count: {
					title: '累计合作次数',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						align: 'right',
						show: true,
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}次` : '0次';
						},
					},
					form: {
						component: {
							placeholder: '请输入累计合作次数',
							precision: 0,
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

