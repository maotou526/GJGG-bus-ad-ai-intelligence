<template>
	<fs-page class="bs-notice-list-page">
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #header-middle>
				<el-tabs v-model="tabActivted" @tab-click="onTabClick">
					<el-tab-pane label="全部" name="all"></el-tab-pane>
					<el-tab-pane label="未读" name="unread">
						<template #label>
							<span>未读</span>
							<el-badge v-if="unreadCount > 0" :value="unreadCount" class="ml-2" />
						</template>
					</el-tab-pane>
					<el-tab-pane label="已读" name="read"></el-tab-pane>
					<el-tab-pane label="待办" name="todo">
						<template #label>
							<span>待办</span>
							<el-badge v-if="todoCount > 0" :value="todoCount" class="ml-2" />
						</template>
					</el-tab-pane>
				</el-tabs>
			</template>
		</fs-crud>
		<!-- 消息详情弹窗 -->
		<NoticeDetail ref="noticeDetailRef" @refresh="handleDetailRefresh" />
	</fs-page>
</template>

<script lang="ts" setup name="BsNoticeList">
import { ref, onMounted, onUnmounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';
import { getUnreadCount } from '../api';
import NoticeDetail from '../components/NoticeDetail/index.vue';

// tab选择
const tabActivted = ref('all');
const unreadCount = ref(0);
const todoCount = ref(0);
let refreshTimer: any = null;

// 消息详情弹窗
const noticeDetailRef = ref();
const openDetail = (row: any) => {
	noticeDetailRef.value?.open(row);
};

const onTabClick = (tab: any) => {
	const { paneName } = tab;
	tabActivted.value = paneName;
	crudExpose.doRefresh();
};

const context: any = { tabActivted, openDetail };
const { crudRef, crudBinding, crudExpose } = useFs({ createCrudOptions, context });

// 详情弹窗操作后刷新列表
const handleDetailRefresh = () => {
	crudExpose.doRefresh();
	fetchUnreadCount();
};

// 获取未读数量
const fetchUnreadCount = async () => {
	try {
		const res = await getUnreadCount();
		if (res.code === 2000) {
			unreadCount.value = res.data?.count || 0;
		}
	} catch (error) {
		console.error('获取未读数量失败', error);
	}
};

// 页面打开后获取列表数据
onMounted(async () => {
	await fetchUnreadCount();
	crudExpose.doRefresh();
	// 每30秒刷新一次未读数量
	refreshTimer = setInterval(() => {
		fetchUnreadCount();
	}, 30000);
});

// 页面卸载时清除定时器
onUnmounted(() => {
	if (refreshTimer) {
		clearInterval(refreshTimer);
	}
});
</script>

<style scoped lang="scss">
.bs-notice-list-page {
	height: 100%;
}

.ml-2 {
	margin-left: 8px;
}
</style>