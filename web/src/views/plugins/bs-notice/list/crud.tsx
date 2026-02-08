import * as api from '../api';
import { dict, AddReq, CrudExpose, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { computed } from 'vue';
import { MsgType, Priority, ReadStatus, HandleStatus } from './types';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { ElMessage, ElMessageBox } from 'element-plus';

export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context: any }): CreateCrudOptionsRet {
	const { tabActivted, openDetail } = context;

	// 获取消息列表（标准DRF接口）
	const pageRequest = async (query: any) => {
		if (tabActivted.value === 'unread') {
			query.read_status = 0;
		} else if (tabActivted.value === 'read') {
			query.read_status = 1;
		} else if (tabActivted.value === 'todo') {
			query.handle_status = 0;
		}
		return await api.GetList(query);
	};

	// 发送通知
	const addRequest = async ({ form }: AddReq) => {
		return await api.sendNotification({
			msg_type: form.msg_type,
			title: form.title,
			content: form.content,
			jump_url: form.jump_url,
			priority: form.priority || 2,
			send_type: form.send_type,
			extra_data: form.extra_data ? JSON.parse(form.extra_data) : {},
			expire_time: form.expire_time,
		});
	};

	// 标记已读
	const handleMarkRead = async (row: any) => {
		try {
			await api.markAsRead(row.id);
			ElMessage.success('标记成功');
			crudExpose.doRefresh();
		} catch (error: any) {
			ElMessage.error(error.message || '标记失败');
		}
	};

	// 标记已处理
	const handleMarkHandled = async (row: any) => {
		try {
			await api.markAsHandled(row.id);
			ElMessage.success('标记成功');
			crudExpose.doRefresh();
		} catch (error: any) {
			ElMessage.error(error.message || '标记失败');
		}
	};

	// 标记已忽略
	const handleMarkIgnored = async (row: any) => {
		try {
			await api.markAsIgnored(row.id);
			ElMessage.success('标记成功');
			crudExpose.doRefresh();
		} catch (error: any) {
			ElMessage.error(error.message || '标记失败');
		}
	};

	// 删除消息
	const handleDelete = async (row: any) => {
		try {
			await ElMessageBox.confirm('确定要删除这条消息吗？', '提示', {
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'warning',
			});
			await api.deleteNotice(row.id);
			ElMessage.success('删除成功');
			crudExpose.doRefresh();
		} catch (error: any) {
			if (error !== 'cancel') {
				ElMessage.error(error.message || '删除失败');
			}
		}
	};

	return {
		crudOptions: {
			...listPageDefSingleLineCfg,
			request: {
				pageRequest,
				addRequest,
			},
			actionbar: {
				buttons: {
					add: { show: false },
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 250,
				buttons: {
					view: { show: false },
					edit: { show: false },
					remove: { show: false },
					viewDetail: {
						text: '查看',
						type: 'text',
						icon: 'View',
						click: ({ row }: any) => openDetail(row),
					},
					markRead: {
						text: '已读',
						type: 'text',
						icon: 'Check',
						click: ({ row }: any) => handleMarkRead(row),
						show: computed(() => tabActivted.value !== 'read'),
					},
					markHandled: {
						text: '已处理',
						type: 'text',
						icon: 'CircleCheck',
						click: ({ row }: any) => handleMarkHandled(row),
						show: computed(() => tabActivted.value === 'todo'),
					},
					markIgnored: {
						text: '忽略',
						type: 'text',
						icon: 'Close',
						click: ({ row }: any) => handleMarkIgnored(row),
						show: computed(() => tabActivted.value === 'todo'),
					},
					deleteBtn: {
						text: '删除',
						type: 'text',
						icon: 'Delete',
						click: ({ row }: any) => handleDelete(row),
					},
				},
			},
			form: {
				labelWidth: '100px',
				wrapper: {
					is: 'el-dialog',
					title: '发送通知',
					width: '600px',
				},
			},
			columns: {
				msg_type: {
					title: '消息类型',
					type: 'dict-select',
					dict: dict({
						data: [
							{ label: '系统通知', value: MsgType.SYSTEM, color: 'primary' },
							{ label: '业务消息', value: MsgType.BUSINESS, color: 'success' },
							{ label: '告警消息', value: MsgType.ALERT, color: 'warning' },
							{ label: '待办提醒', value: MsgType.TODO, color: 'danger' },
						],
					}),
					column: {
						width: 120,
					},
					form: {
						rules: [{ required: true, message: '请选择消息类型' }],
						value: MsgType.SYSTEM,
					},
				},
				title: {
					title: '标题',
					type: 'text',
					column: { minWidth: 200 },
					form: {
						rules: [{ required: true, message: '请输入标题' }],
						component: { placeholder: '请输入消息标题' },
					},
				},
				content: {
					title: '消息内容',
					type: 'textarea',
					column: {
						minWidth: 200,
						showOverflowTooltip: true,
					},
					form: {
						component: {
							placeholder: '请输入消息内容',
							rows: 4,
						},
					},
				},
				priority: {
					title: '优先级',
					type: 'dict-select',
					dict: dict({
						data: [
							{ label: '紧急', value: Priority.URGENT, color: 'danger' },
							{ label: '普通', value: Priority.NORMAL, color: 'primary' },
							{ label: '低', value: Priority.LOW, color: 'info' },
						],
					}),
					column: {
						width: 100
					},
					form: {
						value: Priority.NORMAL,
					},
				},
				sender_name: {
					title: '发送人',
					type: 'text',
					column: { width: 120 },
					form: { show: false },
				},
				user_name: {
					title: '接收人',
					type: 'text',
					search: { show: true },
					column: { width: 120 },
					form: { show: false },
				},
				send_time: {
					title: '发送时间',
					type: 'datetime',
					column: {
						width: 180,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: { show: false },
				},
				read_status: {
					title: '阅读状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ label: '未读', value: ReadStatus.UNREAD },
							{ label: '已读', value: ReadStatus.READ },
						],
					}),
					column: {
						width: 100,
						show: computed(() => tabActivted.value === 'all'),
					},
					form: { show: false },
				},
				handle_status: {
					title: '处理状态',
					type: 'dict-select',
					search: { show: false },
					dict: dict({
						data: [
							{ label: '未处理', value: HandleStatus.UNHANDLED },
							{ label: '已处理', value: HandleStatus.HANDLED },
							{ label: '已忽略', value: HandleStatus.IGNORED },
						],
					}),
					column: {
						width: 100,
						show: computed(() => tabActivted.value === 'todo'),
					},
					form: { show: false },
				},
				send_type: {
					title: '发送方式',
					type: 'dict-select',
					dict: dict({
						data: [
							{ label: '指定用户', value: 1 },
							{ label: '指定角色', value: 2 },
							{ label: '指定部门', value: 3 },
							{ label: '全局广播', value: 4 },
							{ label: '混合模式', value: 5 },
						],
					}),
					column: { show: false },
					form: {
						rules: [{ required: true, message: '请选择发送方式' }],
						value: 4,
						helper: '全局广播：发送给所有用户；指定用户/角色/部门需在扩展数据中填写对应ID',
					},
				},
				extra_data: {
					title: '接收范围',
					type: 'textarea',
					column: { show: false },
					form: {
						component: {
							placeholder: '全局广播可留空，其他方式示例：\n指定用户: {"user_ids":["用户ID1","用户ID2"]}\n指定角色: {"role_ids":["角色ID1"]}\n指定部门: {"dept_ids":["部门ID1"]}',
							rows: 3,
						},
						helper: '全局广播时留空即可，其他发送方式需填写JSON格式的接收范围',
					},
				},
				jump_url: {
					title: '跳转链接',
					type: 'text',
					column: { show: false },
					form: {
						component: { placeholder: '点击消息跳转的前端路由，如 /booking/detail?id=xxx' },
					},
				},
				expire_time: {
					title: '过期时间',
					type: 'datetime',
					column: { show: false },
					form: {
						component: {
							placeholder: '留空则永不过期',
							valueFormat: 'YYYY-MM-DD HH:mm:ss',
						},
					},
				},
			},
		},
	};
}
