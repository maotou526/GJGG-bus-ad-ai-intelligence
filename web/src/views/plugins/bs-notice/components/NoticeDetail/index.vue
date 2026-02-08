<template>
	<el-dialog
		v-model="visible"
		:title="noticeData?.title || '消息详情'"
		width="600px"
		:close-on-click-modal="false"
		@close="handleClose"
	>
		<div class="notice-detail-content" v-if="noticeData">
			<div class="notice-detail-header">
				<div class="notice-meta">
					<el-tag :type="getMsgTypeTag(noticeData.msg_type)" effect="plain">
						{{ getMsgTypeLabel(noticeData.msg_type) }}
					</el-tag>
					<el-tag :type="getPriorityTag(noticeData.priority)" size="small" class="ml-2">
						{{ getPriorityLabel(noticeData.priority) }}
					</el-tag>
					<el-tag v-if="noticeData.read_status === 0" type="danger" size="small" class="ml-2">未读</el-tag>
					<el-tag v-else type="info" size="small" class="ml-2">已读</el-tag>
				</div>
				<div class="notice-info">
					<div class="info-item">
						<span class="info-label">发送人：</span>
						<span class="info-value">{{ noticeData.sender_name || '系统' }}</span>
					</div>
					<div class="info-item">
						<span class="info-label">发送时间：</span>
						<span class="info-value">{{ formatDateTime(noticeData.send_time) }}</span>
					</div>
					<div class="info-item" v-if="noticeData.read_time">
						<span class="info-label">阅读时间：</span>
						<span class="info-value">{{ formatDateTime(noticeData.read_time) }}</span>
					</div>
					<div class="info-item" v-if="noticeData.handle_status !== undefined && noticeData.handle_status !== 0">
						<span class="info-label">处理状态：</span>
						<span class="info-value">{{ noticeData.handle_status === 1 ? '已处理' : '已忽略' }}</span>
					</div>
				</div>
			</div>
			<div class="notice-detail-body">
				<div class="notice-body-content" v-if="noticeData.content" v-html="noticeData.content"></div>
				<div class="notice-body-empty" v-else>暂无内容</div>
			</div>
		</div>
		<el-empty v-else description="消息不存在" :image-size="100" />
		<template #footer>
			<div class="notice-detail-footer">
				<el-button @click="handleClose">关闭</el-button>
				<el-button v-if="noticeData?.read_status === 0" type="primary" @click="handleMarkRead">
					标记已读
				</el-button>
				<el-button v-if="noticeData?.handle_status === 0 && noticeData?.msg_type === 4" type="success" @click="handleMarkHandled">
					已处理
				</el-button>
				<el-button v-if="noticeData?.handle_status === 0 && noticeData?.msg_type === 4" @click="handleMarkIgnored">
					忽略
				</el-button>
				<el-button
					v-if="noticeData?.jump_url || (noticeData?.rec_table && noticeData?.rec_id)"
					type="primary"
					@click="handleJump"
				>
					跳转业务
				</el-button>
			</div>
		</template>
	</el-dialog>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { markAsRead, markAsHandled, markAsIgnored } from '../../api';
import type { NoticeItem } from '../../list/types';

const emit = defineEmits<{
	(e: 'refresh'): void;
}>();

const visible = ref(false);
const noticeData = ref<NoticeItem | null>(null);

/**
 * 打开消息详情弹窗（供外部调用）
 * @param data 消息数据（列表行数据）
 */
const open = (data: NoticeItem) => {
	noticeData.value = { ...data };
	visible.value = true;
	// 自动标记已读
	if (data.read_status === 0) {
		autoMarkRead(data.id);
	}
};

// 自动标记已读（静默，不弹提示）
const autoMarkRead = async (id: string) => {
	try {
		await markAsRead(id);
		if (noticeData.value) {
			noticeData.value.read_status = 1;
			noticeData.value.read_time = new Date().toISOString();
		}
		emit('refresh');
	} catch {
		// 静默失败
	}
};

const handleMarkRead = async () => {
	if (!noticeData.value) return;
	try {
		await markAsRead(noticeData.value.id);
		ElMessage.success('标记成功');
		noticeData.value.read_status = 1;
		noticeData.value.read_time = new Date().toISOString();
		emit('refresh');
	} catch (error: any) {
		ElMessage.error(error.message || '标记失败');
	}
};

const handleMarkHandled = async () => {
	if (!noticeData.value) return;
	try {
		await markAsHandled(noticeData.value.id);
		ElMessage.success('标记成功');
		emit('refresh');
		handleClose();
	} catch (error: any) {
		ElMessage.error(error.message || '标记失败');
	}
};

const handleMarkIgnored = async () => {
	if (!noticeData.value) return;
	try {
		await markAsIgnored(noticeData.value.id);
		ElMessage.success('标记成功');
		emit('refresh');
		handleClose();
	} catch (error: any) {
		ElMessage.error(error.message || '标记失败');
	}
};

const handleJump = () => {
	if (!noticeData.value) return;
	if (noticeData.value.jump_url) {
		window.open(noticeData.value.jump_url, '_blank');
	} else if (noticeData.value.rec_table && noticeData.value.rec_id) {
		const jumpMap: Record<string, string> = {
			booking_order: `/booking/detail?id=${noticeData.value.rec_id}`,
			on_air_order: `/on-air/detail?id=${noticeData.value.rec_id}`,
			off_air_order: `/off-air/detail?id=${noticeData.value.rec_id}`,
		};
		const url = jumpMap[noticeData.value.rec_table] || `/business/detail?table=${noticeData.value.rec_table}&id=${noticeData.value.rec_id}`;
		window.open(url, '_blank');
	}
};

const handleClose = () => {
	visible.value = false;
	noticeData.value = null;
};

const formatDateTime = (time: string) => {
	if (!time) return '-';
	const date = new Date(time);
	return date.toLocaleString('zh-CN', {
		year: 'numeric',
		month: '2-digit',
		day: '2-digit',
		hour: '2-digit',
		minute: '2-digit',
		second: '2-digit',
	});
};

const MSG_TYPE_MAP: Record<number, { label: string; tag: string }> = {
	1: { label: '系统通知', tag: 'primary' },
	2: { label: '业务消息', tag: 'success' },
	3: { label: '告警消息', tag: 'warning' },
	4: { label: '待办提醒', tag: 'danger' },
};

const PRIORITY_MAP: Record<number, { label: string; tag: string }> = {
	1: { label: '紧急', tag: 'danger' },
	2: { label: '普通', tag: 'primary' },
	3: { label: '低', tag: 'info' },
};

const getMsgTypeLabel = (type: number) => MSG_TYPE_MAP[type]?.label || '未知';
const getMsgTypeTag = (type: number) => MSG_TYPE_MAP[type]?.tag || 'info';
const getPriorityLabel = (p: number) => PRIORITY_MAP[p]?.label || '未知';
const getPriorityTag = (p: number) => PRIORITY_MAP[p]?.tag || 'info';

defineExpose({ open });
</script>

<style scoped lang="scss">
.notice-detail-content {
	min-height: 200px;

	.notice-detail-header {
		margin-bottom: 20px;
		padding-bottom: 16px;
		border-bottom: 1px solid #ebeef5;

		.notice-meta {
			display: flex;
			align-items: center;
			margin-bottom: 12px;

			.ml-2 {
				margin-left: 8px;
			}
		}

		.notice-info {
			.info-item {
				margin-bottom: 8px;
				font-size: 14px;

				.info-label {
					color: #909399;
					margin-right: 8px;
				}

				.info-value {
					color: #303133;
				}
			}
		}
	}

	.notice-detail-body {
		.notice-body-content {
			font-size: 14px;
			line-height: 1.6;
			color: #303133;
			min-height: 100px;
		}

		.notice-body-empty {
			color: #909399;
			text-align: center;
			padding: 40px 0;
		}
	}
}

.notice-detail-footer {
	display: flex;
	justify-content: flex-end;
	gap: 12px;
}
</style>
