import { CrudOptions, CrudExpose, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from '../../../roadline_detail/RoadlineDetailViewSet/api';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import { dict } from '@fast-crud/fast-crud';

// 线路走向信息列表的 crud 配置（用于详情弹窗）
export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context?: any }): CreateCrudOptionsRet {
	// 获取线路走向详情列表
	const pageRequest = async (query: any) => {
		// 如果 context 中有线路ID，添加到查询参数中
		if (context?.getRoadlineId) {
			const roadlineId = context.getRoadlineId();
			if (roadlineId) {
				query.roadline = roadlineId;
			}
		}
		// 禁用分页，获取所有数据
		query.limit = 10000; // 设置一个很大的值来获取所有数据
		query.page = 1;
		return await api.GetList(query);
	};

	return {
		crudOptions: {
			...listPageDefSingleLineCfg,
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
				// 关联线路（用于搜索过滤，不显示）
				roadline: {
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
				// 线路名称（显示字段）
				roadline_name: {
					title: '线路名称',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},
				// 上下行显示字段
				up_down_display: {
					title: '上下行',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},
				// 起点名称
				start_name: {
					title: '起点名称',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},
				// 开往方向
				to_direction: {
					title: '开往方向',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},
				// 线路走向
				line_direction: {
					title: '线路走向',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},
				// 首末班时间（格式化显示字段）
				start_end_time_formatted: {
					title: '首末班时间',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: false,
						align: 'left',
					},
					form: { show: false },
				},
				// 线路详情长度
				line_length: {
					title: '线路长度（km）',
					type: 'number',
					search: { show: false },
					column: {
						minWidth: 140,
						sortable: false,
						align: 'left',
						formatter: (context: any) => {
							const value = context.value;
							return value ? `${value}km` : '-';
						},
					},
					form: { show: false },
				},
			},
		},
	};
}
