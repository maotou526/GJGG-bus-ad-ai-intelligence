import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ElMessageBox, ElMessage, ElLoading } from 'element-plus';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 获取区属列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑区属
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		return await api.UpdateObj(form);
	};

	// 删除区属
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加区属
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	// 从高德地图生成区属数据（苏州市及下级县级市、街道）
	const handleGenerate = async () => {
		try {
			// 1. 警告确认
			await ElMessageBox.confirm(
				'将会根据高德API生成最新的苏州市的区属数据。该操作会删除数据库中所有的区属信息并重新生成苏州市及下级县级市、街道数据，是否继续？',
				'生成区属数据',
				{
					confirmButtonText: '确定生成',
					cancelButtonText: '取消',
					type: 'warning',
				}
			);

			// 2. 显示加载
			const loading = ElLoading.service({
				lock: true,
				text: '正在从高德地图获取苏州市区属数据，请稍候...',
				background: 'rgba(0, 0, 0, 0.7)',
			});

			// 3. 调用API（无需传参，后端已固定为苏州市）
			const response = await api.generateFromAmap({});

			loading.close();

			// 4. 成功提示
			ElMessage.success({
				message: response.msg || '生成成功',
				duration: 3000,
			});

			// 5. 刷新列表
			crudExpose.doRefresh();
		} catch (error: any) {
			if (error !== 'cancel') {
				ElMessage.error(error.msg || '生成失败');
			}
		}
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
				labelWidth: '100px',
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
						show: auth('DistrictModelViewSet:Export'),
						text: '导出', //按钮文字
						title: '导出', //鼠标停留显示的信息
						click() {
							return exportRequest(crudExpose.getSearchFormData());
							// return exportRequest(crudExpose!.getSearchFormData())    // 注意这个crudExpose!.getSearchFormData()，一些低版本的环境是需要添加!的
						},
					},
				generate: {
					show: auth('DistrictModelViewSet:Create'),
					text: '生成区属数据',
					type: 'warning',
					icon: 'RefreshRight',
					title: '从高德地图生成区属数据',
					click: handleGenerate,
				},
					add: {
						show: auth('DistrictModelViewSet:Create'),
					},
				},
			},
		rowHandle: {
			//固定右侧
			fixed: 'right',
			width: 150,
			buttons: {
				view: {
					type: 'text',
					order: 1,
					show: auth('DistrictModelViewSet:Retrieve'),
				},
				edit: {
					type: 'text',
					order: 2,
					show: auth('DistrictModelViewSet:Update'),
				},
				enable: {
					show: false, // 隐藏启用按钮
				},
				disable: {
					show: false, // 隐藏禁用按钮
				},
				remove: {
					show: false, // 隐藏删除按钮
				},
			},
		},
			columns: {
			// 序号列（跨页连续编号）
			_index: getIndexColumnConfig(crudExpose),
			// 区属名称
			name: {
				title: '区属名称',
				type: 'input',
				search: { show: true },
				column: {
					minWidth: 170,
					sortable: 'custom',
					align: 'left',
				},
					form: {
						rules: [{ required: true, message: '区属名称必填' }],
						component: {
							placeholder: '请输入区属名称',
						},
					},
				},
			// 区属类型
			type: {
				title: '区属类型',
				type: 'dict-select',
				search: { show: true },
				dict: dict({
					data: [
						{ value: '市', label: '市' },
						{ value: '区', label: '区' },
						{ value: '街道', label: '街道' },
					],
				}),
				column: {
					minWidth: 120,
					sortable: 'custom',
					align: 'left',
					show: false, // 隐藏原始字段，使用显示字段
				},
					form: {
						rules: [{ required: true, message: '区属类型必填' }],
						component: {
							placeholder: '请选择区属类型',
						},
					},
				},
			// 区属类型显示字段
			type_display: {
				title: '区属类型',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 100,
					sortable: false,
					align: 'left',
				},
					form: { show: false }, // 表单中不显示
				},
		// 父级区属ID
		parent_id: {
			title: '父级区属ID',
			type: 'input',
			search: { show: false }, // 搜索栏不显示ID，改用名字搜索
			column: {
				minWidth: 120,
				sortable: 'custom',
				align: 'left',
				show: false, // 隐藏原始字段，使用显示字段
			},
				form: {
					component: {
						placeholder: '请输入父级区属ID',
					},
					helper: '留空表示顶级区属',
				},
			},
		// 父级区属名称显示字段
		parent_name: {
			title: '父级区属',
			type: 'input',
			search: { 
				show: true,
				component: {
					placeholder: '请输入父级区属名称（支持模糊搜索）',
					clearable: true,
				},
			},
			column: {
				minWidth: 150,
				sortable: false,
				align: 'left',
				formatter: (context: any) => {
					const value = context.value;
					return value || '-';
				},
			},
			form: { show: false },
		},
			// 是否有子级
			has_children: {
				title: '有子级',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 80,
					sortable: false,
					align: 'left',
					formatter: (context: any) => {
						const value = context.value;
						return value ? '是' : '否';
					},
				},
					form: { show: false }, // 表单中不显示
				},
		// 中心点坐标
		center_coord: {
			title: '中心点坐标',
			type: 'input',
			search: { show: false },
			column: {
				minWidth: 180,
				sortable: false,
				align: 'left',
				show: false, // 隐藏列
				formatter: (context: any) => {
					const value = context.value;
					return value || '-';
				},
			},
					form: {
						component: {
							placeholder: '请输入中心点坐标，格式：经度,纬度',
						},
						helper: '格式：经度,纬度，例如：121.1234,31.5678',
					},
				},
			// 围栏坐标
			fence: {
				title: '围栏坐标',
				type: 'textarea',
				search: { show: false },
				column: {
					minWidth: 200,
					sortable: false,
					align: 'left',
					show: false, // 默认隐藏，数据量较大
					formatter: (context: any) => {
						const value = context.value;
						if (!value) return '-';
						// 只显示前50个字符
						return value.length > 50 ? value.substring(0, 50) + '...' : value;
					},
				},
					form: {
						col: { span: 24 }, // 占满整行
						component: {
							placeholder: '请输入围栏坐标串，格式：经度1,纬度1;经度2,纬度2;...',
							rows: 4,
						},
						helper: '格式：经度1,纬度1;经度2,纬度2;经度3,纬度3（至少3个坐标点）',
					},
				},
		// 启用状态
		enabled_mark: {
			title: '启用状态',
			type: 'dict-select',
			search: { show: false }, // 隐藏搜索
			dict: dict({
				data: [
					{ value: 1, label: '启用', color: 'success' },
					{ value: 0, label: '禁用', color: 'danger' },
				],
			}),
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,  // 隐藏列
				component: {
					name: 'fs-dict-tag',
				},
			},
			form: {
				value: 1, // 默认启用
				component: {
					placeholder: '请选择启用状态',
				},
			},
		},
			// 描述
			description: {
				title: '描述',
				type: 'textarea',
				search: { show: false },
				column: {
					minWidth: 200,
					sortable: false,
					align: 'left',
					show: false, // 默认隐藏
					formatter: (context: any) => {
						const value = context.value;
						if (!value) return '-';
						// 只显示前30个字符
						return value.length > 30 ? value.substring(0, 30) + '...' : value;
					},
				},
					form: {
						col: { span: 24 }, // 占满整行
						component: {
							placeholder: '请输入描述信息',
							rows: 3,
						},
					},
				},
		// 创建人
		creator_name: {
			title: '创建人',
			type: 'text',
			search: { show: false },
			column: {
				minWidth: 120,
				sortable: false,
				align: 'left',
				show: false,  // 隐藏列
			},
				form: {
					show: false,
				},
			},
			// 修改人
			modifier_name: {
				title: '修改人',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 120,
					sortable: false,
					align: 'left',
					show: false, // 默认隐藏
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
				align: 'left',
				width: 160,
				sortable: 'custom',
				show: false, // 隐藏列
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
					align: 'left',
					width: 160,
					sortable: 'custom',
					show: false, // 默认隐藏
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

