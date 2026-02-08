<template>
	<el-select
		ref="selectRef"
		popper-class="popperClass"
		class="tableSelector"
		:multiple="props.tableConfig.isMultiple"
		:collapseTags="props.tableConfig.collapseTags"
		v-model="data"
		:placeholder="props.placeholder || '请选择'"
		clearable
		@visible-change="visibleChange"
		@clear="handleClear"
	>
		<template #empty>
			<div class="option">
				<el-input style="margin-bottom: 10px" v-model="search" clearable placeholder="请输入关键词" @change="getDict" @clear="getDict">
					<template #append>
						<el-button type="primary" icon="Search" />
					</template>
				</el-input>
				<el-table
					ref="tableRef"
					:data="tableData"
					:size="props.tableConfig.size"
					border
					row-key="id"
					:lazy="props.tableConfig.lazy"
					:load="props.tableConfig.load"
					:tree-props="props.tableConfig.treeProps"
					style="width: 600px"
					max-height="200"
					height="200"
					:highlight-current-row="!props.tableConfig.isMultiple"
					@selection-change="handleSelectionChange"
					@select="handleSelectionChange"
					@selectAll="handleSelectionChange"
					@current-change="handleCurrentChange"
					@row-click="handleRowClick"
				>
					<el-table-column v-if="props.tableConfig.isMultiple" fixed type="selection" reserve-selection width="55" />
					<el-table-column fixed type="index" label="#" width="50" />
					<el-table-column
						:prop="item.prop"
						:label="item.label"
						:width="item.width"
						v-for="(item, index) in props.tableConfig.columns"
						:key="index"
					/>
				</el-table>
				<el-pagination
					style="margin-top: 10px"
					background
					v-model:current-page="pageConfig.page"
					v-model:page-size="pageConfig.limit"
					layout="prev, pager, next"
					:total="pageConfig.total"
					@current-change="handlePageChange"
				/>
			</div>
		</template>
	</el-select>
</template>

<script setup lang="ts">
import { computed, defineProps, onMounted, reactive, ref, watch } from 'vue';
import XEUtils from 'xe-utils';
import { request } from '/@/utils/service';

const props = defineProps({
	modelValue: {
		type: [Array, String, Number],
		default: null,
	},
	tableConfig: {
		type: Object,
		default: {
			url: null,
			label: null, //显示值
			value: null, //数据值
			isTree: false,
			lazy: true,
			size: 'default',
			load: () => {},
			data: [], //默认数据
			isMultiple: false, //是否多选
			collapseTags: false,
			treeProps: { children: 'children', hasChildren: 'hasChildren' },
			columns: [], //每一项对应的列表项
		},
	},
	displayLabel: {},
	placeholder: {
		type: String,
		default: '请选择',
	},
} as any);
console.log(props.tableConfig);

const emit = defineEmits(['update:modelValue', 'update:rowValue']);
// tableRef
const tableRef = ref();
// selectRef - 用于控制下拉框关闭
const selectRef = ref<any>(null);
// template上使用data - 根据 isMultiple 初始化数据类型
const data = ref<any>(props.tableConfig.isMultiple ? [] : null);
// 多选值
const multipleSelection = ref();
// 搜索值
const search = ref(undefined);
//表格数据
const tableData = ref([]);
// 分页的配置
const pageConfig = reactive({
	page: 1,
	limit: 999,
	total: 0,
});
// 标志：是否是用户手动选择（避免 watch 覆盖用户选择的显示值）
const isUserSelecting = ref(false);

// 辅助函数：在树形数据中查找项
const findItemByValue = (data: any[], value: any): any => {
	for (const item of data) {
		if (item[props.tableConfig.value] === value) {
			return item;
		}
		if (item.children && item.children.length > 0) {
			const found = findItemByValue(item.children, value);
			if (found) return found;
		}
	}
	return null;
};

// 监听 modelValue 变化，用于初始化显示值
watch(() => props.modelValue, (newVal) => {
	// 如果是用户手动选择，跳过此次更新（避免覆盖用户选择的显示值）
	if (isUserSelecting.value) {
		isUserSelecting.value = false; // 重置标志
		return;
	}
	
	if (newVal !== undefined && newVal !== null) {
		if (props.tableConfig.isMultiple) {
			// 多选：如果是数组，需要根据值查找对应的 label
			if (Array.isArray(newVal) && newVal.length > 0 && tableData.value.length > 0) {
				const labels: string[] = newVal.map((val: any) => {
					const item = findItemByValue(tableData.value, val);
					return item ? item[props.tableConfig.label] : '';
				}).filter(Boolean) as string[];
				data.value = labels;
			} else if (Array.isArray(newVal) && newVal.length === 0) {
				data.value = [];
			}
		} else {
			// 单选：从 tableData 中查找对应的 label
			if (tableData.value.length > 0) {
				const item = findItemByValue(tableData.value, newVal);
				if (item) {
					data.value = item[props.tableConfig.label];
				} else {
					// 如果找不到，获取完整数据来查找（用于编辑模式）
					(async () => {
						try {
							const res: any = await request({
								url: props.tableConfig.url,
								params: { limit: 9999 }
							});
							const allData = res.data || [];
							// 直接从扁平数据中查找
							const item = allData.find((item: any) => item[props.tableConfig.value] === newVal);
							if (item) {
								data.value = item[props.tableConfig.label];
							}
						} catch (e) {
							// 忽略错误
						}
					})();
				}
			} else {
				// 如果还没有数据，也尝试获取完整数据来查找
				(async () => {
					try {
						const res: any = await request({
							url: props.tableConfig.url,
							params: { limit: 9999 }
						});
						const allData = res.data || [];
						const item = allData.find((item: any) => item[props.tableConfig.value] === newVal);
						if (item) {
							data.value = item[props.tableConfig.label];
						}
					} catch (e) {
						// 忽略错误
					}
				})();
			}
			// 注意：不再依赖 displayLabel，因为它可能是旧值
			// displayLabel 只用于初始化时的回显
		}
	} else {
		data.value = props.tableConfig.isMultiple ? [] : null;
	}
}, { immediate: true });

/**
 * 表格多选
 * @param val:Array
 */
const handleSelectionChange = (val: any) => {
	if (!props.tableConfig.isMultiple) return; // 单选模式下不处理
	
	const { tableConfig } = props;
	const result = val.map((item: any) => {
		return item[tableConfig.value];
	});
	data.value = val.map((item: any) => {
		return item[tableConfig.label];
	});

	emit('update:modelValue', result);
    // 传递整行数据数组
    emit('update:rowValue', val);
};
/**
 * 表格单选
 * @param val:Object
 */
const handleCurrentChange = (val: any) => {
	// 注意：这个事件会在 setCurrentRow 时自动触发
	// 为了避免自动触发导致的问题，实际选择逻辑已移到 handleRowClick 中
	// 此处不做任何操作，避免重复触发
};

/**
 * 行点击事件（单选模式）
 * @param row:Object
 * @param column:Object - 点击的列信息
 * @param event:Event - 原生事件对象
 */
const handleRowClick = (row: any, column: any, event: any) => {
	const { tableConfig } = props;
	if (!tableConfig.isMultiple && row) {
		// 树形表格：如果点击的是展开图标所在区域，不触发选择
		// 检查点击的目标元素，如果是展开图标或其父元素，则不处理
		const target = event?.target as HTMLElement;
		if (target) {
			// 检查是否点击了展开/收起图标
			const isExpandIcon = target.classList.contains('el-table__expand-icon') ||
				target.closest('.el-table__expand-icon');
			
			if (isExpandIcon) {
				// 点击的是展开图标，不做选择操作
				return;
			}
		}
		
		// 标记为用户手动选择，避免 watch 覆盖显示值
		isUserSelecting.value = true;
		// 先更新显示值
		data.value = row[tableConfig.label];
    // 然后触发 modelValue 与 rowValue 更新
    emit('update:modelValue', row[tableConfig.value]);
    emit('update:rowValue', row);
		// 选中后关闭下拉框
		closeDropdown();
	}
};

/**
 * 关闭下拉框
 */
const closeDropdown = () => {
	// 延迟执行，确保选择操作完成后再关闭
	setTimeout(() => {
		if (selectRef.value) {
			selectRef.value.blur();
		}
	}, 100);
};

/**
 * 清空选择
 */
const handleClear = () => {
	// 清空显示值
	data.value = props.tableConfig.isMultiple ? [] : null;
	// 发出清空事件（将值设为 null）
	emit('update:modelValue', null);
    emit('update:rowValue', null);
};

/**
 * 获取字典值
 */
const getDict = async () => {
	const url = props.tableConfig.url;
	console.log(url);

	const params = {
		page: pageConfig.page,
		limit: pageConfig.limit,
		search: search.value,
	};
	const { data: responseData, page, limit, total } = await request({
		url: url,
		params: params,
	});
	pageConfig.page = page;
	pageConfig.limit = limit;
	pageConfig.total = total;
	
	let processedData = [];
	if (props.tableConfig.data === undefined || props.tableConfig.data.length === 0) {
		if (props.tableConfig.isTree) {
			processedData = XEUtils.toArrayTree(responseData, { parentKey: 'parent', key: 'id', children: 'children' });
		} else {
			processedData = responseData;
		}
	} else {
		processedData = props.tableConfig.data;
	}
	
	tableData.value = processedData;
	
	// 数据加载后，如果有 modelValue，更新显示值（单选模式）
	if (!props.tableConfig.isMultiple && props.modelValue !== undefined && props.modelValue !== null) {
		// 优先使用 displayLabel
		if (props.displayLabel !== undefined && props.displayLabel !== null) {
			data.value = props.displayLabel;
		} else {
			// 否则从 tableData 中查找
			const item = findItemByValue(processedData, props.modelValue);
			if (item) {
				data.value = item[props.tableConfig.label];
			}
		}
	}
};

// 获取节点值
const getNodeValues = () => {
	console.log(props.tableConfig.url);
	
	request({
		url: props.tableConfig.url,
		method: 'post',
		data: { ids: props.modelValue },
	}).then((res: any) => {
		if (res.data && res.data.length > 0) {
			data.value = res.data.map((item: any) => {
				return item[props.tableConfig.label];
			});

			tableRef.value!.clearSelection();
			res.data.forEach((row: any) => {
				tableRef.value!.toggleRowSelection(row, true, false);
			});
		}
	});
};

/**
 * 下拉框展开/关闭
 * @param bool
 */
const visibleChange = (bool: any) => {
	if (bool) {
		// 打开下拉框时，清除表格的当前行选中状态，避免自动触发 current-change
		if (tableRef.value && !props.tableConfig.isMultiple) {
			tableRef.value.setCurrentRow(null);
		}
		getDict();
	}
};

/**
 * 分页
 * @param page
 */
const handlePageChange = (page: any) => {
	pageConfig.page = page;
	getDict();
};

onMounted(async () => {
	// 初始化时如果有值且有 displayLabel，直接使用（用于编辑模式的回显）
	if (!props.tableConfig.isMultiple && props.modelValue !== undefined && props.modelValue !== null) {
		if (props.displayLabel !== undefined && props.displayLabel !== null) {
			data.value = props.displayLabel;
		} else {
			// 如果没有 displayLabel，尝试从已加载的数据中查找
			if (tableData.value.length > 0) {
				const item = findItemByValue(tableData.value, props.modelValue);
				if (item) {
					data.value = item[props.tableConfig.label];
				} else {
						// 如果找不到，获取完整数据来查找（用于编辑模式）
						// 对于树形结构，获取所有数据（不分页），然后从扁平数据中直接查找（更简单可靠）
						try {
							const res: any = await request({
								url: props.tableConfig.url,
								params: { limit: 9999 } // 获取所有数据
							});
							const allData = res.data || [];
							// 直接从扁平数据中查找（不转换为树形，因为只需要找标签）
							const item = allData.find((item: any) => item[props.tableConfig.value] === props.modelValue);
							if (item) {
								data.value = item[props.tableConfig.label];
							}
						} catch (e) {
							// 忽略错误
						}
				}
			} else {
				// 如果还没有加载数据，先加载一次
				await getDict();
				// 加载后再次查找
				if (tableData.value.length > 0) {
					const item = findItemByValue(tableData.value, props.modelValue);
					if (item) {
						data.value = item[props.tableConfig.label];
					} else {
						// 如果还是找不到，获取完整数据
						try {
							const res: any = await request({
								url: props.tableConfig.url,
								params: { limit: 9999 }
							});
							const allData = res.data || [];
							// 直接从扁平数据中查找（不转换为树形，因为只需要找标签）
							const item = allData.find((item: any) => item[props.tableConfig.value] === props.modelValue);
							if (item) {
								data.value = item[props.tableConfig.label];
							}
						} catch (e) {
							// 忽略错误
						}
					}
				}
			}
		}
	}
});

// 单独监听 displayLabel 的初始化（仅用于编辑时的回显）
watch(() => props.displayLabel, (newLabel, oldLabel) => {
	// 只在有新值且和旧值不同时更新（避免覆盖用户的选择）
	if (!props.tableConfig.isMultiple && newLabel !== undefined && newLabel !== null && newLabel !== oldLabel) {
		// 只有当前 data.value 为空或等于 oldLabel 时才更新
		if (!data.value || data.value === oldLabel) {
			data.value = newLabel;
		}
	}
});
</script>

<style scoped>
.option {
	height: auto;
	line-height: 1;
	padding: 5px;
	background-color: #fff;
}

/* 单选模式下，表格行添加点击样式 */
:deep(.el-table__body tbody tr) {
	cursor: pointer;
}

:deep(.el-table__body tbody tr:hover) {
	background-color: var(--el-table-row-hover-bg-color);
}
</style>
<style lang="scss">
.popperClass {
	height: 320px;
}

.el-select-dropdown__wrap {
	max-height: 310px !important;
}

.tableSelector {
	/* 只隐藏多选标签的关闭图标，不隐藏清空按钮 */
	.el-tag__close {
		display: none;
	}
}
</style>

