import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from '../api/scheme';
import { auth } from '/@/utils/authFunction';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

//此处为crudOptions配置
export default function ({
	crudExpose,
	onAdd,
	onEdit,
	onPreview
}: {
	crudExpose: CrudExpose;
	onAdd?: () => void;
	onEdit?: (row: any) => void;
	onPreview?: (row: any) => void;
}): CreateCrudOptionsRet {
	// 获取模板列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑模板
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}
		return await api.UpdateObj(form);
	};

	// 删除模板
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加模板
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
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
			search: {
				collapsed: false,
			},
			form: {
				col: { span: 12 },
				labelWidth: '120px',
				wrapper: {
					is: 'el-dialog',
					width: '90%',
					closeOnClickModal: false, // 禁用点击空白处关闭弹窗
					fullscreen: true, // 全屏显示
				},
				// 禁用 fastcrud 的默认表单，我们使用自定义的 SchemeWizard
				display: 'none',
			},
			actionbar: {
				buttons: {
					add: {
						show: auth('WorkflowScheme:Create'),
						text: '新增',
						click: () => {
							// 调用传入的回调函数打开表单对话框
							onAdd?.();
						},
					},
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width: 250,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: false, // 暂时隐藏查看
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('WorkflowScheme:Update'),
						text: '编辑',
						click: ({ row }: any) => {
							// 调用传入的回调函数打开表单对话框
							onEdit?.(row);
						},
					},
					remove: {
						type: 'text',
						order: 5,
						show: auth('WorkflowScheme:Delete'),
						text: '删除',
					},
					// 自定义按钮：预览
					preview: {
						type: 'text',
						order: 3,
						show: auth('WorkflowScheme:Retrieve'),
						text: '预览',
						click: ({ row }: any) => {
							onPreview?.(row);
						},
					},
					// 自定义按钮：停用
					disableBtn: {
						text: '停用',
						type: 'text',
						order: 4,
						show: ({ row }: any) => {
							// 只有正式且已启用的才显示停用按钮
							return Number(row.type) !== 2 && Number(row.enabled_mark) === 1 && auth('WorkflowScheme:Update');
						},
						click: async ({ row }: any) => {
							const { ElMessageBox, ElMessage } = await import('element-plus');
							await ElMessageBox.confirm(
								'是否确认停用该流程模板？',
								'提示',
								{
									confirmButtonText: '确定',
									cancelButtonText: '取消',
									type: 'warning',
								}
							);

							await api.DisableScheme(row.id);
							ElMessage.success('停用成功');
							crudExpose.doRefresh();
						},
					},
					// 自定义按钮：启用
					enableBtn: {
						text: '启用',
						type: 'text',
						order: 4,
						show: ({ row }: any) => {
							// 只有正式且已停用的才显示启用按钮
							return Number(row.type) !== 2 && Number(row.enabled_mark) === 0 && auth('WorkflowScheme:Update');
						},
						click: async ({ row }: any) => {
							const { ElMessageBox, ElMessage } = await import('element-plus');
							await ElMessageBox.confirm(
								'是否确认启用该流程模板？',
								'提示',
								{
									confirmButtonText: '确定',
									cancelButtonText: '取消',
									type: 'warning',
								}
							);

							await api.EnableScheme(row.id);
							ElMessage.success('启用成功');
							crudExpose.doRefresh();
						},
					},
				},
			},
			columns: {
				// 序号列（跨页连续编号）
				_index: getIndexColumnConfig(crudExpose),
				// 模板编号
				code: {
					title: '编号',
					type: 'input',
					search: {
						show: true,
						component: {
							placeholder: '请输入编号',
						},
					},
					column: {
						minWidth: 150,
						sortable: 'custom',
					},
					form: {
						show: false, // 使用自定义编辑页面
					},
				},
				// 模板名称
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
						minWidth: 180,
						sortable: 'custom',
					},
					form: {
						show: false, // 使用自定义编辑页面
					},
				},
				// 分类
				category: {
					title: '分类',
					type: 'dict-select',
					search: { show: false },
					dict: dict({
						// TODO: 从数据字典加载分类 FlowSort
						data: [
							{ value: 'default', label: '默认分类' },
						],
					}),
					column: {
						minWidth: 120,
						align: 'center',
						show: false,
					},
					form: {
						show: false, // 使用自定义编辑页面
					},
				},
				// 状态
				enabled_mark: {
					title: '状态',
					type: 'dict-select',
					search: { show: false },
					column: {
						minWidth: 100,
						align: 'left',
						sortable: 'custom',
						cellRender: ({ row }: any) => {
							// 草稿状态优先显示
							if (Number(row.type) === 2) {
								return <el-tag type="warning">草稿</el-tag>;
							}
							if (Number(row.enabled_mark) === 1) {
								return <el-tag type="success">正常</el-tag>;
							}
							return <el-tag type="info">禁用</el-tag>;
						},
					},
					form: {
						show: false, // 使用自定义编辑页面
					},
				},
				// 类型（正式/草稿）
				type: {
					title: '类型',
					type: 'dict-select',
					search: { show: false },
					dict: dict({
						data: [
							{ value: 1, label: '正式', color: 'success' },
							{ value: 2, label: '草稿', color: 'warning' },
						],
					}),
					column: {
						show: false, // 默认隐藏，状态字段会显示草稿
					},
					form: {
						show: false, // 使用自定义编辑页面
					},
				},
				// 我的任务（是否允许发起）
				mark: {
					title: '允许发起',
					type: 'dict-radio',
					search: { show: false },
					dict: dict({
						data: [
							{ value: 1, label: '允许发起' },
							{ value: 2, label: '不允许发起' },
						],
					}),
					column: {
						show: false,
					},
					form: {
						show: false, // 使用自定义编辑页面
					},
				},
				// 移动端显示
				is_in_app: {
					title: '移动端显示',
					type: 'dict-radio',
					search: { show: false },
					dict: dict({
						data: [
							{ value: 1, label: '显示' },
							{ value: 2, label: '不显示' },
						],
					}),
					column: {
						show: false,
					},
					form: {
						show: false, // 使用自定义编辑页面
					},
				},
				// 创建人
				creator_name: {
					title: '创建人',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						align: 'left',
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
						sortable: 'custom',
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						show: false,
					},
				},
				// 备注
				description: {
					title: '备注',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 200,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: {
						show: false, // 使用自定义编辑页面
					},
				},
			},
		},
	};
}
