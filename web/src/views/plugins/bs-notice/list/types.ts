/**
 * 消息项数据类型
 */
export interface NoticeItem {
	id: string;
	notice_id: string;
	msg_type: number; // 1系统通知 2业务消息 3告警消息 4待办提醒
	title: string;
	content?: string;
	jump_url?: string;
	priority: number; // 1紧急 2普通 3低
	read_status: number; // 0未读 1已读
	read_time?: string;
	handle_status: number; // 0未处理 1已处理 2已忽略
	handle_time?: string;
	send_time: string;
	sender_name?: string;
	rec_table?: string;
	rec_id?: string;
}

/**
 * 分页查询参数
 */
export interface PageQuery {
	page?: number;
	limit?: number;
	msg_type?: number;
	read_status?: number;
	handle_status?: number;
	search?: string;
}

/**
 * 消息类型枚举
 */
export enum MsgType {
	SYSTEM = 1, // 系统通知
	BUSINESS = 2, // 业务消息
	ALERT = 3, // 告警消息
	TODO = 4, // 待办提醒
}

/**
 * 优先级枚举
 */
export enum Priority {
	URGENT = 1, // 紧急
	NORMAL = 2, // 普通
	LOW = 3, // 低
}

/**
 * 阅读状态枚举
 */
export enum ReadStatus {
	UNREAD = 0, // 未读
	READ = 1, // 已读
}

/**
 * 处理状态枚举
 */
export enum HandleStatus {
	UNHANDLED = 0, // 未处理
	HANDLED = 1, // 已处理
	IGNORED = 2, // 已忽略
}

/**
 * 消息类型显示配置
 */
export const MSG_TYPE_CONFIG = {
	[MsgType.SYSTEM]: { label: '系统通知', color: 'primary', icon: '📢' },
	[MsgType.BUSINESS]: { label: '业务消息', color: 'success', icon: '📋' },
	[MsgType.ALERT]: { label: '告警消息', color: 'danger', icon: '⚠️' },
	[MsgType.TODO]: { label: '待办提醒', color: 'warning', icon: '📌' },
};

/**
 * 优先级显示配置
 */
export const PRIORITY_CONFIG = {
	[Priority.URGENT]: { label: '紧急', color: 'danger', type: 'danger' },
	[Priority.NORMAL]: { label: '普通', color: 'primary', type: 'primary' },
	[Priority.LOW]: { label: '低', color: 'info', type: 'info' },
};

