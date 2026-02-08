<template>
	<div class="notice-popover-content">
		<div class="notice-popover-header">
			<span class="header-title">未读消息 ({{ unreadCount }})</span>
			<el-button
				link
				type="primary"
				size="small"
				@click="handleViewAll"
				:disabled="unreadCount === 0"
			>
				查看全部
			</el-button>
		</div>
		<div class="notice-popover-body" v-loading="loading">
			<template v-if="noticeList.length > 0">
				<div
					v-for="item in noticeList"
					:key="item.id"
					class="notice-item"
					@click="handleItemClick(item)"
				>
					<div class="notice-item-header">
						<span class="notice-title">{{ item.title }}</span>
						<el-tag
							:type="getMsgTypeConfig(item.msg_type)?.color"
							size="small"
							effect="plain"
						>
							{{ getMsgTypeConfig(item.msg_type)?.label }}
						</el-tag>
					</div>
					<div class="notice-item-content" v-if="item.content">
						{{ item.content.length > 50 ? item.content.substring(0, 50) + '...' : item.content }}
					</div>
					<div class="notice-item-footer">
						<span class="notice-time">{{ formatTime(item.send_time) }}</span>
					</div>
				</div>
			</template>
			<el-empty v-else description="暂无未读消息" :image-size="80" />
		</div>
	</div>
	<!-- 消息详情弹窗 -->
	<NoticeDetail ref="noticeDetailRef" @refresh="handleDetailRefresh" />
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { getUnreadCount, getMyNotices } from '../../api';
import { NoticeItem, MSG_TYPE_CONFIG } from '../../list/types';
import NoticeDetail from '../NoticeDetail/index.vue';
import { messageCenterStore } from '/@/stores/messageCenter';

const router = useRouter();
const messageCenter = messageCenterStore();
const unreadCount = ref(0);
const noticeList = ref<NoticeItem[]>([]);
const loading = ref(false);
let refreshTimer: any = null;

// 获取未读数量
const fetchUnreadCount = async () => {
	try {
		const res = await getUnreadCount();
		if (res.code === 2000) {
			unreadCount.value = res.data?.count || 0;
			messageCenter.setUnread(unreadCount.value);
		}
	} catch (error) {
		console.error('获取未读数量失败', error);
	}
};

// 获取未读消息列表
const fetchNoticeList = async () => {
	if (unreadCount.value === 0) {
		noticeList.value = [];
		return;
	}
	loading.value = true;
	try {
		const res = await getMyNotices({
			read_status: 0,
			offset: 0,
			limit: 10,
		});
		noticeList.value = res?.data || [];
	} catch (error) {
		console.error('获取未读消息列表失败', error);
	} finally {
		loading.value = false;
	}
};

// 消息详情弹窗
const noticeDetailRef = ref();
const handleItemClick = (item: NoticeItem) => {
	noticeDetailRef.value?.open(item);
};

// 详情弹窗操作后刷新
const handleDetailRefresh = () => {
	fetchUnreadCount();
	fetchNoticeList();
};

// 查看全部
const handleViewAll = () => {
	router.push('/plugins/bs-notice');
};

// 格式化时间
const formatTime = (time: string) => {
	if (!time) return '-';
	const date = new Date(time);
	const now = new Date();
	const diff = now.getTime() - date.getTime();
	const minutes = Math.floor(diff / 60000);
	const hours = Math.floor(diff / 3600000);
	const days = Math.floor(diff / 86400000);

	if (minutes < 1) return '刚刚';
	if (minutes < 60) return `${minutes}分钟前`;
	if (hours < 24) return `${hours}小时前`;
	if (days < 7) return `${days}天前`;
	return date.toLocaleDateString('zh-CN');
};

// 获取消息类型配置
const getMsgTypeConfig = (msgType: number) => {
	return MSG_TYPE_CONFIG[msgType as keyof typeof MSG_TYPE_CONFIG];
};

// 初始化
onMounted(async () => {
	await fetchUnreadCount();
	await fetchNoticeList();
	// 每30秒刷新一次
	refreshTimer = setInterval(() => {
		fetchUnreadCount();
		fetchNoticeList();
	}, 30000);
});

// 清理
onUnmounted(() => {
	if (refreshTimer) {
		clearInterval(refreshTimer);
	}
});
</script>

<style scoped lang="scss">
.notice-popover-content {
	.notice-popover-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 12px 16px;
		border-bottom: 1px solid #ebeef5;

		.header-title {
			font-size: 14px;
			font-weight: 500;
			color: #303133;
		}
	}

	.notice-popover-body {
		max-height: 400px;
		overflow-y: auto;
		padding: 8px 0;

		.notice-item {
			padding: 12px 16px;
			border-bottom: 1px solid #f5f7fa;
			cursor: pointer;
			transition: background-color 0.3s;

			&:hover {
				background-color: #f5f7fa;
			}

			&:last-child {
				border-bottom: none;
			}

			.notice-item-header {
				display: flex;
				justify-content: space-between;
				align-items: center;
				margin-bottom: 8px;

				.notice-title {
					font-size: 14px;
					font-weight: 500;
					color: #303133;
					flex: 1;
					overflow: hidden;
					text-overflow: ellipsis;
					white-space: nowrap;
				}
			}

			.notice-item-content {
				font-size: 12px;
				color: #909399;
				margin-bottom: 8px;
				line-height: 1.5;
			}

			.notice-item-footer {
				display: flex;
				justify-content: space-between;
				align-items: center;

				.notice-time {
					font-size: 12px;
					color: #c0c4cc;
				}

			}
		}
	}
}
</style>

