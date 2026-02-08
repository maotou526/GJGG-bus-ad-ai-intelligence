import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ElMessage, ElMessageBox } from 'element-plus';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 获取日期列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑日期
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	// 删除日期
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加日期
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	// 初始化年度数据
	const initYearData = async () => {
		try {
			await ElMessageBox.prompt('请输入要初始化的年份（留空则初始化当前年份）', '初始化年度数据', {
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				inputPattern: /^\d{4}$|^$/,
				inputErrorMessage: '请输入4位数字的年份，或留空使用当前年份',
			}).then(async ({ value }) => {
				const year = value ? parseInt(value) : undefined;
				const res = await api.InitYear(year);
				ElMessage.success(res.msg || '初始化成功');
				crudExpose.doRefresh();
			});
		} catch (error) {
			// 用户取消操作
		}
	};

	return {
		crudOptions: {
			...listPageDefSingleLineCfg,
			request: {
				pageRequest,
			},
			// 搜索配置
			// search: {
			// 	container: {
			// 		collapse: true,
			// 		action: {
			// 			label: '操作',
			// 			col: { span: 4 },
			// 		},
			// 		col: { span: 4 },
			// 		collapseButton: {},
			// 	},
			// },
			actionbar: {
				buttons: {
					initYear: {
						text: '初始化年度',
						title: '初始化年度数据',
						type: 'primary',
						show: auth('BaseDateModelViewSet:Create'),
						click() {
							return initYearData();
						},
					},
					add: {
						show: false,
					},
				},
			},
			rowHandle: {
				show: false,
			},
			columns: {
			// 序号列（跨页连续编号）
			_index: getIndexColumnConfig(crudExpose),
			// 日期
			date: {
				title: '日期',
				type: 'date',
				search: { 
					show: true,
					component: {
						valueFormat: 'YYYY-MM-DD',
					},
				},
				column: {
					minWidth: 120,
					sortable: 'custom',
				},
				form: {
					show: false,
					component: {
						valueFormat: 'YYYY-MM-DD',
					},
				},
			},
			// 当月
			month: {
				title: '当月',
				type: 'number',
				search: { 
					show: true,
					component: {
						min: 1,
						max: 12,
						placeholder: '请输入月份(1-12)',
					},
				},
				column: {
					minWidth: 80,
					sortable: 'custom',
					formatter: (context: any) => {
						const value = context.value;
						return value ? `${value}月` : '-';
					},
				},
				form: {
					show: false,
				},
			},
				// 当月天数
				count: {
					title: '当月天数',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}天` : '-';
						},
					},
					form: {
						show: false,
					},
				},
				// 星期显示
				week_display: {
					title: '星期',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align:'left',
					},
					form: { show: false },
				},
				// 日期类型
				date_type: {
					title: '日期类型',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '工作日', value: 0, color: 'success' },
							{ label: '休息日', value: 1, color: 'warning' },
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
						show: false,
					},
				},
				// 名称
				name: {
					title: '名称',
					type: 'input',
					search: { 
						show: true,
						component: {
							placeholder: '请输入名称',
						},
					},
					column: {
						minWidth: 120,
						sortable: 'custom',
						formatter: (context: any) => {
							const value = context.value;
							return value || '-';
						},
					},
					form: {
						show: false,
					},
				},
				// 是否上班
				is_work: {
					title: '是否上班',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '休息日', value: 0, color: 'warning' },
							{ label: '上班(工作日)', value: 1, color: 'success' },
						],
					}),
					valueBuilder: ({ row, value }: any) => {
						const v = value ?? row.is_work;
						const val = v === true || v === 'true' || v === '1' ? 1
							: v === false || v === 'false' || v === '0' ? 0
							: typeof v === 'string' ? Number(v) : v;
						row.is_work = val;
						return val;
					},
					column: {
						minWidth: 100,
						sortable: 'custom',
						component: {
							name: 'fs-dict-select',
							color: 'auto',
						},
					},
					form: {
						show: false,
					},
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
						show:false,
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
						show:false,
					},
					form: {
						show: false,
					},
				},
			},
		},
	};
}

