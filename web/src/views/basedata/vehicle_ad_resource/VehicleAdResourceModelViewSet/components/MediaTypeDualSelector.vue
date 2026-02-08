<!--
 * @Description: 媒体类型选择组件（左右分栏：左侧已选，右侧可选）
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2026-02-05
-->
<template>
	<div class="media-type-dual-selector">
		<div v-if="loading" style="padding: 20px; text-align: center; color: #909399;">
			正在加载媒体类型列表...
		</div>
		<div v-else-if="allTypes.length === 0" style="padding: 20px; text-align: center; color: #909399;">
			暂无可选媒体类型
		</div>
		<div v-else class="selector-container">
			<!-- 左侧：可选 -->
			<div class="selector-panel left-panel">
				<div class="panel-header">
					<span class="panel-title">可选类型</span>
					<el-input
						v-model="leftSearchText"
						placeholder="搜索可选类型"
						clearable
						size="small"
						class="search-input"
						:disabled="disabled"
					>
						<template #prefix>
							<el-icon><Search /></el-icon>
						</template>
					</el-input>
				</div>
				<div class="panel-body">
					<el-scrollbar height="320px">
						<el-checkbox-group v-model="leftSelectedIds" :disabled="disabled">
							<el-checkbox
								v-for="item in filteredLeftList"
								:key="item.id"
								:value="item.id"
								class="checkbox-item"
								:disabled="disabled"
							>
								{{ item.media_name }}
							</el-checkbox>
						</el-checkbox-group>
						<div v-if="filteredLeftList.length === 0" class="empty-tip">暂无可选类型</div>
					</el-scrollbar>
				</div>
			</div>

			<!-- 中间：操作按钮 -->
			<div class="selector-actions">
				<el-button
					type="primary"
					:icon="ArrowRight"
					:disabled="disabled || leftSelectedIds.length === 0"
					@click="moveToRight"
					size="small"
				>
					添加
				</el-button>
			</div>

			<!-- 右侧：已选 -->
			<div class="selector-panel right-panel">
				<div class="panel-header">
					<span class="panel-title">已选类型</span>
					<el-input
						v-model="rightSearchText"
						placeholder="搜索已选类型"
						clearable
						size="small"
						class="search-input"
						:disabled="disabled"
					>
						<template #prefix>
							<el-icon><Search /></el-icon>
						</template>
					</el-input>
				</div>
				<div class="panel-body">
					<el-scrollbar height="320px">
						<div v-for="item in filteredRightList" :key="item.id" class="selected-item">
							<div class="item-content">
								<span class="item-name">{{ item.media_name }}</span>
								<el-button
									v-if="!disabled"
									type="danger"
									:icon="Delete"
									link
									size="small"
									@click="removeItem(item.id)"
								>								
								</el-button>
							</div>
						</div>
						<div v-if="filteredRightList.length === 0" class="empty-tip">暂无已选类型</div>
					</el-scrollbar>
				</div>
			</div>
		</div>
	</div>
</template>

<script lang="ts" setup name="MediaTypeDualSelector">
import { ref, computed, watch, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Search, ArrowRight, Delete } from '@element-plus/icons-vue';
import { request } from '/@/utils/service';

interface MediaTypeItem {
	id: string;
	media_name: string;
}

const props = defineProps<{
	modelValue?: MediaTypeItem[];
	value?: MediaTypeItem[]; // 兼容 fast-crud
	disabled?: boolean;
}>();

const emit = defineEmits<{
	'update:modelValue': [value: MediaTypeItem[]];
	'update:value': [value: MediaTypeItem[]];
	change: [value: MediaTypeItem[]];
}>();

const actualValue = computed(() => props.modelValue || props.value || []);

const loading = ref(false);
const allTypes = ref<MediaTypeItem[]>([]);
const selectedList = ref<MediaTypeItem[]>([]);

const leftSearchText = ref('');
const rightSearchText = ref('');
const leftSelectedIds = ref<string[]>([]);

// 过滤：左侧可选（排除已选）
const filteredLeftList = computed(() => {
	const selectedIdsSet = new Set(selectedList.value.map((x) => x.id));
	let list = allTypes.value.filter((x) => !selectedIdsSet.has(x.id));
	if (leftSearchText.value) {
		const q = leftSearchText.value.toLowerCase();
		list = list.filter((x) => (x.media_name || '').toLowerCase().includes(q));
	}
	return list;
});

// 过滤：右侧已选
const filteredRightList = computed(() => {
	let list = selectedList.value;
	if (rightSearchText.value) {
		const q = rightSearchText.value.toLowerCase();
		list = list.filter((x) => (x.media_name || '').toLowerCase().includes(q));
	}
	return list;
});

const updateModelValue = () => {
	const newValue = [...selectedList.value];
	emit('update:modelValue', newValue);
	emit('update:value', newValue);
	emit('change', newValue);
};

const removeItem = (id: string) => {
	selectedList.value = selectedList.value.filter((x) => x.id !== id);
	updateModelValue();
};

const moveToRight = () => {
	if (leftSelectedIds.value.length === 0) return;
	const itemsToAdd = allTypes.value.filter((x) => leftSelectedIds.value.includes(x.id));
	itemsToAdd.forEach((item) => {
		if (!selectedList.value.some((s) => s.id === item.id)) {
			selectedList.value.push({ ...item });
		}
	});
	leftSelectedIds.value = [];
	updateModelValue();
};

const loadAllTypes = async () => {
	loading.value = true;
	try {
		// 复用后端列表接口：包含基础类型与组合类型（crud.tsx 中也是这么取的）
		const resp: any = await request({
			url: '/api/AdMediaTypeModelViewSet/',
			method: 'get',
			params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
		});
		const data = resp?.data;
		const list = Array.isArray(data) ? data : Array.isArray(data?.results) ? data.results : [];
		allTypes.value = (list || []).map((item: any) => ({
			id: String(item.id),
			media_name: item.media_name || `媒体类型ID:${item.id}`,
		}));
	} catch (e) {
		console.error('加载媒体类型列表失败:', e);
		ElMessage.error('加载媒体类型列表失败');
	} finally {
		loading.value = false;
	}
};

watch(
	() => actualValue.value,
	(newValue) => {
		if (Array.isArray(newValue) && newValue.length > 0) {
			selectedList.value = newValue.map((x: any) => ({
				id: String(x.id),
				media_name: x.media_name || x.name || '',
			}));
		} else {
			selectedList.value = [];
		}
	},
	{ immediate: true, deep: true }
);

onMounted(() => {
	loadAllTypes();
});
</script>

<style scoped lang="scss">
.media-type-dual-selector {
	width: 100%;

	.selector-container {
		display: flex;
		gap: 12px;
		align-items: flex-start;
	}

	.selector-panel {
		flex: 1;
		border: 1px solid #dcdfe6;
		border-radius: 4px;
		background: #fff;

		.panel-header {
			padding: 12px;
			border-bottom: 1px solid #dcdfe6;
			display: flex;
			justify-content: space-between;
			align-items: center;
			background: #f5f7fa;

			.panel-title {
				font-weight: 600;
				color: #303133;
			}

			.search-input {
				width: 160px;
			}
		}

		.panel-body {
			padding: 12px;

			.checkbox-item {
				display: block;
				margin-bottom: 8px;
				padding: 8px;
				border-radius: 4px;
				transition: background-color 0.2s;
				&:hover {
					background-color: #f5f7fa;
				}
			}

			.selected-item {
				margin-bottom: 10px;
				padding: 10px;
				border: 1px solid #e4e7ed;
				border-radius: 4px;
				background: #fafafa;

				.item-content {
					display: flex;
					justify-content: space-between;
					align-items: center;

					.item-name {
						font-weight: 500;
						color: #303133;
					}
				}
			}

			.empty-tip {
				text-align: center;
				color: #909399;
				padding: 40px 0;
			}
		}
	}

	.selector-actions {
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: 12px;
		padding-top: 96px;
		width: 88px;
	}
}
</style>

