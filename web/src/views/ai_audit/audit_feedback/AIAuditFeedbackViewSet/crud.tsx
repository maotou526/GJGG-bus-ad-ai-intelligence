import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { auth } from '/@/utils/authFunction';
import { ElMessage, ElMessageBox } from 'element-plus';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

// 此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 获取AI审核反馈列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑AI审核反馈
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	// 删除AI审核反馈
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加AI审核反馈
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
						show: auth('AIAuditFeedbackViewSet:Create'),
					},
					export: {
						text: '导出',
						title: '导出数据',
						type: 'default',
						show: auth('AIAuditFeedbackViewSet:Export'),
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
						show: auth('AIAuditFeedbackViewSet:Retrieve'),
					},
					edit: {
						show: auth('AIAuditFeedbackViewSet:Update'),
					},
					remove: {
						show: auth('AIAuditFeedbackViewSet:Delete'),
					},
				},
			},
			columns: {
				// 序号列（跨页连续编号）
				_index: getIndexColumnConfig(crudExpose),

				// AI审核记录ID
				audit_log_id: {
					title: 'AI审核记录ID',
					type: 'number',
					search: {
						show: true,
						component: {
							placeholder: '请输入AI审核记录ID',
						},
					},
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '请输入AI审核记录ID' }],
						component: {
							placeholder: '请输入AI审核记录ID',
						},
					},
				},

				// 审核员ID
				reviewer_id: {
					title: '审核员ID',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						show: false,
					},
					form: {
						rules: [{ required: true, message: '请输入审核员ID' }],
						component: {
							placeholder: '请输入审核员ID',
						},
					},
				},

				// 审核员姓名
				reviewer_name: {
					title: '审核员',
					type: 'text',
					search: {
						show: true,
						component: {
							placeholder: '请输入审核员姓名',
						},
					},
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '审核员姓名（冗余字段）',
						},
					},
				},

				// 人工判定结果
				manual_conclusion: {
					title: '人工判定',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '同意AI判定', value: 1, color: 'success' },
							{ label: '部分同意', value: 2, color: 'warning' },
							{ label: '完全不同意', value: 3, color: 'danger' },
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
						rules: [{ required: true, message: '请选择人工判定结果' }],
						component: {
							placeholder: '请选择人工判定结果',
						},
					},
				},

				// 最终审核结果
				final_result: {
					title: '最终结果',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '通过', value: 1, color: 'success' },
							{ label: '驳回修改', value: 2, color: 'warning' },
							{ label: '转法务审核', value: 3, color: 'danger' },
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
						rules: [{ required: true, message: '请选择最终审核结果' }],
						component: {
							placeholder: '请选择最终审核结果',
						},
					},
				},

				// AI判定准确性
				ai_accuracy: {
					title: 'AI准确性',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '非常准确', value: 1, color: 'success' },
							{ label: '基本准确', value: 2, color: 'primary' },
							{ label: '不太准确', value: 3, color: 'warning' },
							{ label: '完全错误', value: 4, color: 'danger' },
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
						component: {
							placeholder: '请选择AI判定准确性',
						},
					},
				},

				// 误判项（JSON字段）
				false_detections: {
					title: '误判项',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						show: false,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) return '-';
							try {
								const jsonValue = typeof value === 'string' ? JSON.parse(value) : value;
								return Array.isArray(jsonValue) ? jsonValue.join(', ') : JSON.stringify(jsonValue);
							} catch (e) {
								return value;
							}
						},
					},
					form: {
						component: {
							rows: 3,
							placeholder: 'AI误报的检测项（JSON格式）',
						},
					},
				},

				// 漏检项（JSON字段）
				missed_detections: {
					title: '漏检项',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						show: false,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) return '-';
							try {
								const jsonValue = typeof value === 'string' ? JSON.parse(value) : value;
								return Array.isArray(jsonValue) ? jsonValue.join(', ') : JSON.stringify(jsonValue);
							} catch (e) {
								return value;
							}
						},
					},
					form: {
						component: {
							rows: 3,
							placeholder: 'AI未检测到的违规项（JSON格式）',
						},
					},
				},

				// 反馈说明
				feedback_text: {
					title: '反馈说明',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 250,
						formatter: (context: any) => {
							const value = context.value;
							if (!value) return '-';
							return value.length > 50 ? value.substring(0, 50) + '...' : value;
						},
					},
					form: {
						component: {
							rows: 4,
							placeholder: '请输入详细反馈意见',
						},
					},
				},

				// 反馈时间
				feedback_time: {
					title: '反馈时间',
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
