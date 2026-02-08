<!--
 * @Description: 基础类型选择组件（左右分栏）
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
-->
<template>
	<div class="component-type-selector">
		<!-- 加载中提示 -->
		<div v-if="loading" style="padding: 20px; text-align: center; color: #909399;">
			正在加载基础类型列表...
		</div>
		<!-- 无数据提示 -->
		<div v-else-if="allBaseTypes.length === 0" style="padding: 20px; text-align: center; color: #909399;">
			暂无可选基础类型
		</div>
		<!-- 正常显示选择器 -->
		<div v-else class="selector-container">
			<!-- 左侧：可选择的基础类型 -->
			<div class="selector-panel left-panel">
				<div class="panel-header">
					<span class="panel-title">可选基础类型</span>
					<el-input
						v-model="leftSearchText"
						placeholder="搜索基础类型"
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
					<el-scrollbar height="300px">
						<el-checkbox-group v-model="selectedIds" @change="handleSelectionChange" :disabled="disabled">
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
						<div v-if="filteredLeftList.length === 0" class="empty-tip">
							暂无可选基础类型
						</div>
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

			<!-- 右侧：已选的基础类型 -->
			<div class="selector-panel right-panel">
				<div class="panel-header">
					<span class="panel-title">已选基础类型</span>
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
					<el-scrollbar height="300px">
						<div
							v-for="(item, index) in filteredRightList"
							:key="item.id"
							class="selected-item"
						>
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
						<div v-if="filteredRightList.length === 0" class="empty-tip">
							暂无已选基础类型
						</div>
					</el-scrollbar>
				</div>
			</div>
		</div>
	</div>
</template>

<script lang="ts" setup name="ComponentTypeSelector">
import { ref, computed, watch, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Search, ArrowRight, ArrowLeft, Delete } from '@element-plus/icons-vue';
import * as api from '../api';

interface ComponentType {
	id: string;
	media_name: string;
	sort_order?: number;
}

const props = defineProps<{
	modelValue?: ComponentType[];
	value?: ComponentType[]; // 兼容 fast-crud 可能传递的 value
	mediaCategory?: number; // 大类归属，用于过滤基础类型
	disabled?: boolean; // 是否禁用
}>();

const emit = defineEmits<{
	'update:modelValue': [value: ComponentType[]];
	'update:value': [value: ComponentType[]]; // 兼容 fast-crud
	'change': [value: ComponentType[]]; // 兼容 fast-crud
}>();

// 获取实际的值（兼容 modelValue 和 value）
const actualValue = computed(() => {
	return props.modelValue || props.value || [];
});

// 加载状态
const loading = ref(false);
// 所有基础类型列表
const allBaseTypes = ref<ComponentType[]>([]);
// 已选的基础类型列表
const selectedList = ref<ComponentType[]>([]);
// 左侧搜索文本
const leftSearchText = ref('');
// 右侧搜索文本
const rightSearchText = ref('');
// 左侧选中的ID（用于批量添加）
const leftSelectedIds = ref<string[]>([]);
// 所有选中的ID（用于checkbox-group，仅用于左侧）
const selectedIds = ref<string[]>([]);

// 过滤后的左侧列表（排除已选的）
const filteredLeftList = computed(() => {
	// 获取已选的基础类型ID集合
	const selectedIdsSet = new Set(selectedList.value.map((item) => item.id));
	// 从所有基础类型中排除已选的
	let list = allBaseTypes.value.filter(
		(item) => !selectedIdsSet.has(item.id)
	);
	if (leftSearchText.value) {
		list = list.filter((item) =>
			item.media_name.toLowerCase().includes(leftSearchText.value.toLowerCase())
		);
	}
	return list;
});

// 过滤后的右侧列表（已选的）
const filteredRightList = computed(() => {
	let list = selectedList.value;
	if (rightSearchText.value) {
		list = list.filter((item) =>
			item.media_name.toLowerCase().includes(rightSearchText.value.toLowerCase())
		);
	}
	return list;
});

// 加载基础类型列表
const loadBaseTypes = async () => {
	loading.value = true;
	try {
		console.log('加载基础类型列表, mediaCategory:', props.mediaCategory);
		const response = await api.GetBaseTypes({
			is_composite: false,
			enabled_mark: 1,
			delete_mark: 0,
			...(props.mediaCategory ? { media_category: props.mediaCategory } : {}),
		});
		console.log('基础类型列表响应:', response);
		if (response.data && response.data.results) {
			allBaseTypes.value = response.data.results.map((item: any) => ({
				id: String(item.id), // 确保 id 是字符串类型，与 selectedList 中的 id 类型一致
				media_name: item.media_name,
			}));
		} else if (Array.isArray(response.data)) {
			allBaseTypes.value = response.data.map((item: any) => ({
				id: String(item.id), // 确保 id 是字符串类型
				media_name: item.media_name,
			}));
		}
		console.log('解析后的基础类型列表:', allBaseTypes.value);
		console.log('当前已选的基础类型:', selectedList.value);
	} catch (error) {
		console.error('加载基础类型列表失败:', error);
		ElMessage.error('加载基础类型列表失败');
	} finally {
		loading.value = false;
	}
};

// 处理选择变化（左侧checkbox）
const handleSelectionChange = (value: string[]) => {
	leftSelectedIds.value = value;
};

// 添加到右侧
const moveToRight = () => {
	if (leftSelectedIds.value.length === 0) return;

	const itemsToAdd = allBaseTypes.value.filter((item) =>
		leftSelectedIds.value.includes(item.id)
	);

	// 获取当前最大sort_order
	const maxSortOrder =
		selectedList.value.length > 0
			? Math.max(...selectedList.value.map((item) => item.sort_order || 0))
			: 0;

	itemsToAdd.forEach((item) => {
		if (!selectedList.value.some((selected) => selected.id === item.id)) {
			selectedList.value.push({
				...item,
				sort_order: maxSortOrder + selectedList.value.length + 1,
			});
		}
	});

	leftSelectedIds.value = [];
	selectedIds.value = [];
	updateModelValue();
};


// 删除单个项
const removeItem = (id: string) => {
	selectedList.value = selectedList.value.filter((item) => item.id !== id);
	updateModelValue();
};

// 处理排序变化
const handleSortOrderChange = () => {
	updateModelValue();
};

// 更新modelValue
const updateModelValue = () => {
	const newValue = [...selectedList.value];
	emit('update:modelValue', newValue);
	emit('update:value', newValue);
	emit('change', newValue);
};

// 监听props变化，确保编辑模式下从 composition 表加载的数据能正确显示
watch(
	() => actualValue.value,
	(newValue, oldValue) => {
		console.log('ComponentTypeSelector value changed:', {
			newValue,
			oldValue,
			newValueLength: newValue?.length,
			props: props,
		});
		if (newValue && Array.isArray(newValue) && newValue.length > 0) {
			// 深拷贝，确保响应式更新
			const newSelectedList = newValue.map((item) => ({
				id: String(item.id), // 确保 id 是字符串类型
				media_name: item.media_name || '',
				sort_order: item.sort_order || 0,
			}));
			console.log('更新 selectedList:', newSelectedList);
			selectedList.value = newSelectedList;
		} else {
			console.log('清空 selectedList');
			selectedList.value = [];
		}
	},
	{ immediate: true, deep: true }
);

// 监听大类归属变化，重新加载基础类型
watch(
	() => props.mediaCategory,
	() => {
		loadBaseTypes();
	}
);

onMounted(() => {
	loadBaseTypes();
});
</script>

<style scoped lang="scss">
.component-type-selector {
	width: 100%;

	.selector-container {
		display: flex;
		gap: 16px;
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
				width: 200px;
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
				margin-bottom: 12px;
				padding: 12px;
				border: 1px solid #e4e7ed;
				border-radius: 4px;
				background: #fafafa;

				.item-content {
					display: flex;
					justify-content: space-between;
					align-items: center;
					margin-bottom: 8px;

					.item-name {
						font-weight: 500;
						color: #303133;
					}
				}

				.item-order {
					display: flex;
					align-items: center;
					gap: 8px;
					margin-top: 8px;

					.order-label {
						font-size: 12px;
						color: #606266;
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
		padding-top: 120px;
	}
}
</style>
