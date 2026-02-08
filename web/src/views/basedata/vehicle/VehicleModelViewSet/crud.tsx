import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import{getIndexColumnConfig} from '/@/utils/commonCrud';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ref, Ref } from 'vue';

//此处为crudOptions配置
export default function ({ crudExpose }: { crudExpose: CrudExpose }): CreateCrudOptionsRet {
	// 线路列表
	const roadlineList: Ref<any[]> = ref([]);

	// 加载线路列表
	const loadRoadlineList = async () => {
		try {
			const res = await api.getRoadlineList();
			// 处理不同的返回数据格式
			let data = [];
			if (res && res.data) {
				if (Array.isArray(res.data)) {
					data = res.data;
				} else if (res.data.results && Array.isArray(res.data.results)) {
					data = res.data.results;
				} else if (res.data.data && Array.isArray(res.data.data)) {
					data = res.data.data;
				}
			}
			if (data.length > 0) {
				roadlineList.value = data.map((item: any) => ({
					value: item.id,
					label: item.line_name || item.name || item.id,
				}));
			}
		} catch (error) {
			console.error('加载线路列表失败:', error);
		}
	};

	// 初始化时加载线路列表
	loadRoadlineList();

	// 获取车辆列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑车辆
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 处理日期字段，确保提交纯日期格式
		if (form.buy_date && typeof form.buy_date === 'string') {
			form.buy_date = form.buy_date.split(' ')[0];
		}
		if (form.actual_scrap_year && typeof form.actual_scrap_year === 'string') {
			form.actual_scrap_year = form.actual_scrap_year.split(' ')[0];
		}

		return await api.UpdateObj(form);
	};

	// 删除车辆
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加车辆
	const addRequest = async ({ form }: AddReq) => {
		// 处理日期字段
		if (form.buy_date && typeof form.buy_date === 'string') {
			form.buy_date = form.buy_date.split(' ')[0];
		}
		if (form.actual_scrap_year && typeof form.actual_scrap_year === 'string') {
			form.actual_scrap_year = form.actual_scrap_year.split(' ')[0];
		}

		return await api.AddObj(form);
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	// 启用/禁用车辆
	const enableRequest = async (row: any, enabled_mark: 0 | 1) => {
		return await api.enableVehicle({ id: row.id, enabled_mark });
	};

	// 从OD数据填充车辆信息
	const handlePopulateFromOd = async () => {
		try {
			await ElMessageBox.confirm(
				'此操作将从OD明细数据中提取车辆信息并填充到车辆表和车型表中，是否继续？',
				'提示',
				{
					confirmButtonText: '确定',
					cancelButtonText: '取消',
					type: 'warning',
				}
			);

			const loading = ElMessage({
				message: '正在填充车辆数据，请稍候...',
				type: 'info',
				duration: 0,
			});

			const result = await api.populateFromOd({});
			loading.close();

			if (result.code === 2000) {
				ElMessage({
					message: result.msg || '填充成功',
					type: 'success',
					duration: 3000,
				});
				// 刷新列表
				crudExpose.doRefresh();
			} else {
				ElMessage.error(result.msg || '填充失败');
			}
		} catch (error: any) {
			if (error !== 'cancel') {
				ElMessage.error(error.message || '填充失败');
			}
		}
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
			
			// // 搜索配置
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
						show: auth('VehicleModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('VehicleModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 280,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('VehicleModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('VehicleModelViewSet:Update'),
					},
				enable: {
					type: 'text',
					order: 3,
					text: '启用',
					//show: auth('VehicleModelViewSet:Update'),
					show: false,
					click: async (context: any) => {
						await enableRequest(context.row, 1);
						crudExpose.doRefresh();
					},
				},
				disable: {
					type: 'text',
					order: 4,
					text: '禁用',
					//show: auth('VehicleModelViewSet:Update'),
					show: false,
					click: async (context: any) => {
						await enableRequest(context.row, 0);
						crudExpose.doRefresh();
					},
				},
					remove: {
						type: 'text',
						order: 5,
						show: auth('VehicleModelViewSet:Delete'),
					},
				},
			},
			columns: {
				// ========== 基础信息 ==========
				//序号列
				_index:getIndexColumnConfig(crudExpose),
				// 牌照号
				
				// 自编号
				vehicle_no: {
					title: '车辆编号',
					type: 'input',
					search: { show: true },
					column: {
						minWidth:30,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入自编号',
						},
					},
				},
				vehicle_plate: {
					title: '车牌号',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 40,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '牌照号必填' }],
						component: {
							placeholder: '请输入牌照号',
						},
					},
				},
				// 公司名称
				company_name: {
					title: '公司',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 60,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: '公司名称必填' }],
						component: {
							placeholder: '请输入公司名称',
						},	
					},
				},
				// 车队
				branch: {
					title: '车队',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 40,
						sortable: 'custom',
						show: true,
					},
					form: {
						component: {
							placeholder: '请输入车队',
						},
					},
				},
				// 停车场名称
				park_name: {
					title: '停车场名称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 40,
						sortable: 'custom',
						show: true,
					},
					form: {
						component: {
							placeholder: '请输入停车场名称',
						},
					},
				},
				// 所属线路（外键关联）
				roadline: {
					title: '所属线路',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (roadlineList.value.length === 0) {
								await loadRoadlineList();
							}
							return roadlineList.value;
						},
					}),
					column: {
						minWidth: 60,
						sortable: 'custom',
						show: true, // 直接显示roadline字段
						formatter: (context: any) => {
							// 根据roadline ID查找对应的线路名称
							const roadlineId = context.value;
							if (!roadlineId) return '-';
							// 如果roadlineList还没加载，尝试加载
							if (roadlineList.value.length === 0) {
								loadRoadlineList();
								return roadlineId; // 暂时返回原值，等加载完成后会自动更新
							}
							const roadline = roadlineList.value.find((item: any) => item.value === roadlineId);
							// 如果找到对应的线路，显示线路名称；否则直接显示原值（可能是线路名称字符串）
							return roadline ? roadline.label : roadlineId;
						},
					},
					form: {
						component: {
							placeholder: '请选择所属线路',
							filterable: true,
						},
					},
				},
				// 线路名称显示字段（隐藏，不再使用）
				roadline_name: {
					title: '所属线路',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 60,
						sortable: false,
						align: 'left',
						show: false, // 隐藏此字段
					},
					form: { show: false }, // 表单中不显示
				},
				// ========== 车辆基本信息 ==========
				// 车辆品牌
				vehicle_brand: {
					title: '车辆品牌',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 20,
						sortable: 'custom',
						show:false,
					},
					form: {
						component: {
							placeholder: '请输入车辆品牌',
						},
					},
				},
			// 车辆型号
			vehicle_type: {
				title: '车型',
				type: 'input',
				search: { show: true }, // 表格显示，搜索开启
				column: {
					minWidth: 40,
					sortable: 'custom',
				},
					form: {
						component: {
							placeholder: '请输入车辆型号',
						},
					},
				},
				// 车型简称
				car_type: {
					title: '车型简称',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 40,
						sortable: 'custom',
					},
					form: {
						component: {
							placeholder: '请输入车型简称',
						},
					},
				},
				// 客车类型
				bus_type: {
					title: '客车类型',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 50,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入客车类型',
						},
					},
				},
				
				// 排放等级
				emission_class: {
					title: '排放等级',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入排放等级',
						},
					},
				},
				// ========== 车辆参数 ==========
				// 车辆长度
				vehicle_size: {
					title: '车辆长度(米)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}米` : '-';
						},
					},
					form: {
						component: {
							placeholder: '请输入车辆长度',
							precision: 2,
						},
					},
				},
				// 车辆尺寸
				size: {
					title: '车辆尺寸',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入车辆尺寸',
						},
					},
				},
			// 额定载客人数
			passenger_number: {
				title: '核载人数',
				type: 'number',
				search: { show: true }, // 表格显示，搜索开启
				column: {
					minWidth: 30,
					sortable: 'custom',
				
				},
					form: {
						component: {
							placeholder: '请输入额定载客人数',
							precision: 0,
						},
					},
				},

			// 燃料种类
			fuel_type: {
				title: '燃料类型',
				type: 'input',
				search: { show: true }, // 表格显示，搜索开启
				column: {
					minWidth: 30,
					sortable: 'custom',
				
				},
					form: {
						component: {
							placeholder: '请输入燃料种类',
						},
					},
				},
				// 车辆座位数
				seats_number: {
					title: '车辆座位数',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入车辆座位数',
							precision: 0,
						},
					},
				},
				// 车辆门数
				vehicle_door: {
					title: '车辆门数',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 110,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入车辆门数',
							precision: 0,
						},
					},
				},
				// 额定耗油
				rated_oil: {
					title: '额定耗油(升/百公里)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 170,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}升/百公里` : '-';
						},
					},
					form: {
						component: {
							placeholder: '请输入额定耗油',
							precision: 2,
						},
					},
				},
				// ========== 发动机信息 ==========
				// 发动机位置
				engine_position: {
					title: '发动机位置',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入发动机位置',
						},
					},
				},
				// 发动机型号
				engine_type: {
					title: '发动机型号',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入发动机型号',
						},
					},
				},
				// ========== 日期信息 ==========
				// 购买日期
				buy_date: {
					title: '购买日期',
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
							placeholder: '请选择购买日期',
						},
					},
				},
				// 报废年限
				scrap_years: {
					title: '报废年限(年)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value ? `${context.value}年` : '-';
						},
					},
					form: {
						component: {
							placeholder: '请输入报废年限',
							precision: 0,
						},
					},
				},
				// 报废年限(retirement_time)
				retirement_time: {
					title: '报废年限(年)',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value ? `${context.value}年` : '-';
						},
					},
					form: {
						component: {
							placeholder: '请输入报废年限',
							precision: 0,
						},
					},
				},
				// 计划报废年份
				plan_scrap_year: {
					title: '计划报废年份',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入计划报废年份',
							precision: 0,
						},
					},
				},
				// 实际报废日期
				actual_scrap_year: {
					title: '实际报废日期',
					type: 'date',
					search: { show: false },
					column: {
						align: 'center',
						width: 130,
						show: false,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择实际报废日期',
						},
					},
				},
				// ========== 布尔标记字段 ==========
				// 是否新车载
				is_new_cz: {
					title: '是否新车载',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 110,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// 是否无障碍
				has_wheelchair: {
					title: '是否无障碍',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 110,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// 是否共营车辆
				is_share: {
					title: '是否共营车辆',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// 有无空调
				have_air_condition: {
					title: '有无空调',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '无' },
							{ value: 1, label: '有' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '有' : '无';
						},
					},
					form: {
						value: 0,
					},
				},
				// 有无后置摄像头
				have_back_camera: {
					title: '有无后置摄像头',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '无' },
							{ value: 1, label: '有' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '有' : '无';
						},
					},
					form: {
						value: 0,
					},
				},
				// 高等级车
				is_high_grade: {
					title: '高等级车',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
			// 是否报废
			is_baofei: {
				title: '是否报废',
				type: 'dict-radio',
				dict: dict({
					//dict替代formatter完成数据字段类似的映射
					data: [
						{ value: 0, label: '否' },
						{ value: 1, label: '是' },
					],
				}),
				search: { show: false }, // 表格隐藏，搜索关闭
				column: {
					minWidth: 30,
					sortable: 'custom',
					show:false,
						// 移除 formatter，让 dict 自动显示为带颜色的标签
					},
					form: {
						value: 0,
					},
				},
			// 是否新能源车
			is_new_energy: {
				title: '是否新能源车',
				type: 'dict-radio',
				dict: dict({
					data: [
						{ value: 0, label: '否' },
						{ value: 1, label: '是' },
					],
				}),
				search: { show: false }, // 表格隐藏，搜索关闭
				column: {
					minWidth: 60,
					sortable: 'custom',
					show:false,

				},
					form: {
						value: 0,
					},
				},
			// 是否是新车
			new_flag: {
				title: '是否是新车',
				type: 'dict-radio',
				dict: dict({
					data: [
						{ value: 0, label: '否' },
						{ value: 1, label: '是' },
					],
				}),
				search: { show: false }, // 表格隐藏，搜索关闭
				column: {
					minWidth: 110,
					sortable: 'custom',
					show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// 是否改装过
				is_modified: {
					title: '是否改装过',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 110,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// 是否开通通话功能
				voice_card_enabled: {
					title: '是否开通通话功能',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// 是否开通视频功能
				video_enable: {
					title: '是否开通视频功能',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// 是否有视频功能
				has_video: {
					title: '是否有视频功能',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 140,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// 是否显示充电状态
				show_charge: {
					title: '是否显示充电状态',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ value: 0, label: '否' },
							{ value: 1, label: '是' },
						],
					}),
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
						formatter: (context: any) => {
							return context.value === 1 ? '是' : '否';
						},
					},
					form: {
						value: 0,
					},
				},
				// ========== 设备和状态信息 ==========
				// 智能化终端
				have_system: {
					title: '智能化终端',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入智能化终端',
						},
					},
				},
			// 车辆状态
			vehicle_condition: {
				title: '车辆状态',
				type: 'dict-select',
				dict: dict({
					data: [
						{ value: 1, label: '正常运营',},
						{ value: 0, label: '停运', },
						{ value: 2, label: '故障维修',},
					],
				}),
				search: { show: true },
				column: {
					minWidth: 50,
					sortable: 'custom',
					align: 'left',
				},
			form: {
				value: 1, // 默认值：正常运营
				component: {
					placeholder: '请选择车辆状态',
				},
			},
			},
				// 实时状况
				realtime_condition: {
					title: '实时状况',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入实时状况',
						},
					},
				},
				// 状态 比较通用的字段，后面再说吧
				vehicle_status: {
					title: '状态',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入状态',
						},
					},
				},
				// POS机编号
				pos_number: {
					title: 'POS机编号',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入POS机编号',
						},
					},
				},
				// 车载手机号
				mobile_number: {
					title: '车载手机号',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入车载手机号',
						},
					},
				},
				// 电子路牌
				electronic_lupai: {
					title: '电子路牌',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 110,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入电子路牌',
						},
					},
				},
				// 序列号
				sn: {
					title: '序列号',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入序列号',
						},
					},
				},
				// 车载GPS供应商
				manufacturer: {
					title: '车载GPS供应商',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入车载GPS供应商',
						},
					},
				},
				// 预计到站时间
				dzsj: {
					title: '预计到站时间',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 130,
						sortable: 'custom',
						show: false,
					},
					form: {
						component: {
							placeholder: '请输入预计到站时间',
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
				// ========== 状态字段 ==========
			// 启用状态
			enabled_mark: {
				title: '启用状态',
				type: 'dict-select',
				search: { show: false }, // 表格隐藏，搜索关闭
				dict: dict({
					data: [
						{ value: 1, label: '启用' },
						{ value: 0, label: '禁用' },
					],
				}),
				column: {
					minWidth: 100,
					sortable: 'custom',
					show: false,
				},
					form: {
						component: {
							placeholder: '请选择启用状态',
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
						show:false,
						formatter: (context: any) => {
							const value = context.value;
							return value ? '是' : '否';
						},
					},
					form: { show: false },
				},
				// ========== 审计字段 ==========
				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					search: { show: false },
					column: {
						show:false,
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
						show:false,
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


