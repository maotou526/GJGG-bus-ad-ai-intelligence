import { CrudOptions, CrudExpose, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from '../../../roadline_stop_rel/RoadlineStopRelModelViewSet/api';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import { dict } from '@fast-crud/fast-crud';

// 站级信息列表的 crud 配置（用于详情弹窗）
export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context?: any }): CreateCrudOptionsRet {
	// 获取站点关联列表
	const pageRequest = async (query: any) => {
		// 字段映射：前端 up_down -> 后端 line_dtl_id__up_down
		const mappedQuery = { ...query };
		
		// 如果 context 中有线路ID，添加到查询参数中
		if (context?.getRoadlineId) {
			const roadlineId = context.getRoadlineId();
			if (roadlineId) {
				mappedQuery.roadline_id = roadlineId;
			}
		}
		
		// 禁用分页，获取所有数据
		mappedQuery.limit = 10000; // 设置一个很大的值来获取所有数据
		mappedQuery.page = 1;
		
		// 处理搜索过滤字段
		if (mappedQuery.up_down !== undefined) {
			mappedQuery['line_dtl_id__up_down'] = mappedQuery.up_down;
			delete mappedQuery.up_down;
		}
		
		// 处理排序字段
		if (mappedQuery.ordering) {
			mappedQuery.ordering = mappedQuery.ordering.replace(/^-?up_down$/, (match: string) => {
				return match.startsWith('-') ? '-line_dtl_id__up_down' : 'line_dtl_id__up_down';
			});
		}
		
		return await api.GetList(mappedQuery);
	};

	return {
		crudOptions: {
			...listPageDefMultiLineCfg,
			request: {
				pageRequest,
			},
			// 隐藏搜索栏、工具栏、操作列等，仅显示列表
			search: {
				show: false,
			},
			// 禁用分页
			pagination: {
				show: false,
			},
			actionbar: {
				buttons: {
					add: { show: false },
					export: { show: false },
				},
			},
			rowHandle: {
				show: false, // 隐藏操作列
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),
				// 关联线路ID（用于搜索过滤，不显示）
				roadline_id: {
					title: '线路名称',
					type: 'dict-select',
					search: { 
						show: false, // 隐藏搜索框，但允许通过 setSearchFormData 设置
						value: null, // 初始值为空
					},
					dict: dict({
						url: '/api/RoadlineModelViewSet/?limit=1000&enabled_mark=1&delete_mark=0',
						value: 'id',
						label: 'line_name',
					}),
					column: {
						show: false, // 不显示在列表中
					},
					form: { show: false },
				},
				// 关联线路名称显示字段
				roadline_name: {
					title: '线路名称',
					type: 'text',
					search: { show: false },
					column: {
						width: 120,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 上下行方向
				up_down: {
					title: '线路方向',
					type: 'dict-select',
					dict: dict({
						data: [
							{ value: 0, label: '上行' },
							{ value: 1, label: '下行' },
						],
					}),
					search: { show: false },
					column: {
						width: 90,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},
				// 站级序号
				level_id: {
					title: '站级序号',
					type: 'number',
					search: { show: false },
					column: {
						width: 90,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},
				// 站级名称
				level_name: {
					title: '站级名称',
					type: 'input',
					search: { show: false },
					column: {
						minwidth: 100,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 站点编号
				stop_code: {
					title: '站点编号',
					type: 'input',
					search: { show: false },
					column: {
						width: 110,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 环域
				stop_area: {
					title: '环域',
					type: 'text',
					search: { show: false },
					column: {
						width: 90,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 区属
				stop_district: {
					title: '区属',
					type: 'text',
					search: { show: false },
					column: {
						width: 90,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 路名
				stop_roadline_name: {
					title: '路名',
					type: 'text',
					search: { show: false },
					column: {
						width: 110,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 站名
				stop_name: {
					title: '站名',
					type: 'text',
					search: { show: false },
					column: {
						width: 120,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 车向
				stop_path_direction: {
					title: '车向',
					type: 'text',
					search: { show: false },
					column: {
						width: 90,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 站址
				stop_address: {
					title: '站址',
					type: 'text',
					search: { show: false },
					column: {
						minwidth: 150,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
				// 停靠线路
				stop_road_line_list: {
					title: '停靠线路',
					type: 'text',
					search: { show: false },
					column: {
						minwidth: 150,
						sortable: false,
						align: 'left',
						showOverflowTooltip: true,
					},
					form: { show: false },
				},
			},
		},
	};
}
