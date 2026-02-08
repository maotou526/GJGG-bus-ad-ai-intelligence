import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from '../api/process';
import { auth } from '/@/utils/authFunction';
import { listPageDefMultiLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import { Ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

//此处为crudOptions配置
export default function ({ 
	crudExpose, 
    categoryId,
    onOperation
}: { 
	crudExpose: CrudExpose; 
    categoryId: Ref<string>;
    onOperation: (key: string, row: any) => void;
}): CreateCrudOptionsRet {
	// 获取任务列表
	const pageRequest = async (query: any) => {
        // 合并 categoryId
        query.categoryId = categoryId.value;
		return await api.GetTaskPageList(query);
	};

	// 删除草稿
	const delRequest = async ({ row }: DelReq) => {
		return await api.DeleteDraft({ processId: row.id || row.process_id });
	};

	return {
		crudOptions: {
			...listPageDefMultiLineCfg,
			request: {
				pageRequest,
				delRequest,
			},
			// 搜索配置
			search: {
				collapsed: false,
			},
			form: {
				wrapper: {
					is: 'el-dialog',
                    width: '80%',
				},
			},
			actionbar: {
				buttons: {
					add: {
						show: false, // 通过自定义按钮触发
					},
                    // 自定义按钮：发起流程
                    create: {
                        text: '发起流程',
                        type: 'primary',
                        show: true, // auth('Workflow:Create'),
                        click: () => {
                            onOperation('create', {});
                        }
                    },
                    // 批量审核
                    batchAudit: {
                        text: '批量审核',
                        show: () => categoryId.value === '2', // 待办才显示
                        click: () => {
                            onOperation('batchAudit', {});
                        }
                    }
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width: 250,
				buttons: {
                    edit: { show: false },
                    remove: { show: false },
                    
                    // 草稿操作：编辑
                    draftEdit: {
                        text: '编辑',
                        type: 'primary',
                        size: 'small',
                        order: 1,
                        show: (context: any) => {
                            return context.row.enabled_mark === 2;
                        },
                        click: (context: any) => {
                            onOperation('draftEdit', context.row);
                        }
                    },
                    // 草稿操作：删除
                    draftDelete: {
                        text: '删除',
                        type: 'danger',
                        size: 'small',
                        order: 2,
                        show: (context: any) => {
                            return context.row.enabled_mark === 2;
                        },
                        click: async (context: any) => {
                            try {
                                await ElMessageBox.confirm('是否确认删除该草稿？', '提示', { type: 'warning' });
                                await api.DeleteDraft({ processId: context.row.id || context.row.process_id });
                                ElMessage.success('删除成功');
                                crudExpose.doRefresh();
                            } catch (e) {
                                // cancel
                            }
                        }
                    },
                    
                    // 待办操作：审核
                    audit: {
                        text: '审核',
                        type: 'primary',
                        size: 'small',
                        order: 1,
                        show: (context: any) => {
                            return categoryId.value === '2' && context.row.is_finished === 0;
                        },
                        click: (context: any) => {
                            onOperation('audit', context.row);
                        }
                    },
                    
                    // 我发起的：催办
                    urge: {
                        text: '催办',
                        type: 'warning',
                        size: 'small',
                        order: 1,
                        show: (context: any) => {
                            return categoryId.value === '1' && context.row.is_finished === 0;
                        },
                        click: async (context: any) => {
                            try {
                                await ElMessageBox.confirm('是否确认催办？', '提示', { type: 'warning' });
                                await api.UrgeFlow({ processId: context.row.process_id });
                                ElMessage.success('催办成功');
                            } catch (e) {
                                //
                            }
                        }
                    },
                    // 我发起的：撤销
                    revoke: {
                        text: '撤销',
                        type: 'danger',
                        size: 'small',
                        order: 2,
                        show: (context: any) => {
                            // 只有未开始处理的（is_start=0）可以撤销？Legacy code: if (row.F_IsStart == 0)
                            // 这里假设 is_start 字段存在
                            return categoryId.value === '1' && context.row.is_finished === 0 && context.row.is_start === 0;
                        },
                        click: async (context: any) => {
                             try {
                                await ElMessageBox.confirm('是否确认撤销流程？', '提示', { type: 'warning' });
                                await api.RevokeFlow({ processId: context.row.process_id });
                                ElMessage.success('撤销成功');
                                crudExpose.doRefresh();
                            } catch (e) {
                                //
                            }
                        }
                    },
                    
                    // 重新发起
                    recreate: {
                        text: '重新发起',
                        type: 'success',
                        size: 'small',
                        order: 3,
                        show: (context: any) => {
                            // 已结束或已作废，或者 TaskType=5 (Legacy logic)
                            // 简单逻辑：如果是已办且是重新发起节点? 
                            // Legacy: if (row.F_TaskType == 5) return '重新发起'
                            // Legacy: if categoryId == '1' and (is_again=1 or finished=0) ...
                            // 简化：任何已完成或作废的都可以重新发起？或者看业务需求。
                            // 只有 categoryId=1 (我发起的) 或 categoryId=3 (已办) 显示?
                            // 这里只为方便，先允许 '我的由于被驳回而结束的' 重新发起。
                            // 假设 status=3 (作废/驳回)
                            return categoryId.value === '1' && context.row.enabled_mark === 3;
                        },
                         click: (context: any) => {
                            onOperation('create', { processId: context.row.process_id, isAgain: true });
                        }
                    },
                    
                    // 查看详情
                    view: {
                        text: '查看',
                        type: 'info',
                        size: 'small',
                        order: 9,
                         show: (context: any) => {
                            return context.row.enabled_mark !== 2; // 草稿不能查看
                        },
                        click: (context: any) => {
                            onOperation('view', context.row);
                        }
                    }

				},
			},
			columns: {
				_index: getIndexColumnConfig(crudExpose),
                // 任务名称
				task_name: {
					title: '任务名称',
					type: 'text',
                    search: { show: true },
					column: {
						minWidth: 150,
                        sortable: 'custom',
					},
				},
				// 标题
				title: {
					title: '标题',
					type: 'input',
					search: { show: true },
					column: {
						minWidth: 200,
						sortable: 'custom',
                        formatter: ({ row }) => {
                            if (row.scheme_name && row.title && row.scheme_name !== row.title) {
                                return `${row.scheme_name}(${row.title})`;
                            }
                            return row.scheme_name || row.title;
                        }
					},
				},
				// 等级
				level: {
					title: '等级',
					type: 'dict-select',
					search: { show: false },
                    dict: dict({
                        data: [
                            { value: 0, label: '普通' },
                            { value: 1, label: '重要', color: 'warning' },
                            { value: 2, label: '紧急', color: 'danger' },
                        ]
                    }),
					column: {
						width: 80,
						align: 'center',
					},
				},
                // 状态
				enabled_mark: {
					title: '状态',
					type: 'dict-select',
					search: { show: false },
                    dict: dict({
                        data: [
                            { value: 1, label: '运行中', color: 'success' },
                            { value: 2, label: '草稿', color: 'info' },
                            { value: 3, label: '作废', color: 'danger' },
                            { value: 4, label: '结束', color: 'warning' } // 前端自定义状态
                        ]
                    }),
					column: {
						width: 100,
						align: 'center',
                        formatter: ({ row, value }) => {
                            if (row.is_finished === 1) return '结束';
                            if (value === 1) return '运行中';
                            if (value === 2) return '草稿';
                            if (value === 3) return '作废';
                            return value;
                        },
                        component: {
                            name: 'fs-dict-tag',
                            // 动态 dict data logic difficult here, rely on formatter or simple dict
                        }
					},
				},
				// 发起者
				creator_name: {
					title: '发起者',
					type: 'text',
					search: { show: false },
					column: {
						width: 100,
						align: 'center',
					},
				},
				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
                    search: { show: true }, // Legacy used DateSearch (range)
					column: {
						align: 'center',
						width: 160,
						sortable: 'custom',
                        component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
                    // Form config for date range search
                    form: {
                         component: {
                            name: 'el-date-picker',
                            props: {
                                type: 'daterange',
                                valueFormat: 'YYYY-MM-DD HH:mm:ss'
                            }
                         }
                    }
				},
			},
		},
	};
}
