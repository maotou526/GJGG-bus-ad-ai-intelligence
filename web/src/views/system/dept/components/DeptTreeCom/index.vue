<template>
	<div class="dept-tree-wrapper">
		<!-- 公司筛选下拉（树形懒加载选择器） -->
		<el-row :gutter="10" style="margin-bottom: 8px">
			<el-col :span="12">
				<TableSelector
					v-model="selectedCompanyId"
					:displayLabel="selectedCompanyLabel"
					:tableConfig="companyTableConfig"
					placeholder="请选择公司"
					@update:modelValue="handleCompanyChange"
				/>
			</el-col>
			<el-col :span="12">
				<el-input v-model="filterVal" :prefix-icon="Search" placeholder="请输入部门名称" />
			</el-col>
		</el-row>
		<div class="dept-tree-com">
		<div class="tc-head">
			<el-icon size="16" color="#606266" class="tc-head-icon">
				<HomeFilled />
			</el-icon>
			<span class="tc-head-txt">部门架构</span>
			<el-icon size="16" color="#606266" @click="() => (showTotalNum = !showTotalNum)" class="tc-head-icon">
				<View v-show="!showTotalNum" />
				<Hide v-show="showTotalNum" />
			</el-icon>
		</div>

		<el-tree
			ref="treeRef"
			:data="internalTreeData"
			:props="defaultTreeProps"
			node-key="id"
			:expand-on-click-node="false"
			:filter-node-method="handleFilterTreeNode"
			:indent="38"
			@node-click="handleNodeClick"
			highlight-current
			default-expand-all
		>
			<template #default="{ node, data }">
				<element-tree-line :node="node" :showLabelLine="false" :indent="32">
					<span v-if="data.status" class="font-normal font-black text-center">
						<SvgIcon name="iconfont icon-shouye" color="var(--el-color-primary)" />&nbsp;{{ node.label }}
						<span v-show="showTotalNum">（{{ data.dept_user_count }}人）</span>
					</span>
					<span v-else color="var(--el-color-primary)"> <SvgIcon name="iconfont icon-shouye" />&nbsp;{{ node.label }} </span>
				</element-tree-line>
			</template>
		</el-tree>

		<div class="tree-tags">
			<el-tooltip effect="dark" content="新增">
				<el-icon size="16" @click="handleUpdateMenu('create')" class="mlt-icon">
					<Plus />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="编辑">
				<el-icon size="16" @click="handleUpdateMenu('update')" class="mlt-icon">
					<Edit />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="上移">
				<el-icon size="16" @click="handleSort('up')" class="mlt-icon">
					<Top />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="下移">
				<el-icon size="16" @click="handleSort('down')" class="mlt-icon">
					<Bottom />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="删除">
				<el-icon size="16" @click="handleDeleteDept" class="mlt-icon">
					<Delete />
				</el-icon>
			</el-tooltip>
		</div>
		</div>
	</div>
</template>

<script lang="ts" setup>
import { ref, watch, toRaw, h, onMounted } from 'vue';
import { ElTree } from 'element-plus';
import { getElementLabelLine } from 'element-tree-line';
import { Search } from '@element-plus/icons-vue';
import { getAllDeptList, deptMoveUp, deptMoveDown } from '../../api';
import { warningNotification } from '/@/utils/message';
import { request } from '/@/utils/service';
import { TreeItemType, APIResponseData } from '../../types';
import type Node from 'element-plus/es/components/tree/src/model/node';
import TableSelector from '/@/components/tableSelector/index.vue';
import XEUtils from 'xe-utils';

const ElementTreeLine = getElementLabelLine(h);

const defaultTreeProps: any = {
	children: 'children',
	label: 'name',
};

const emit = defineEmits(['treeClick', 'deleteDept', 'updateDept', 'companyChange']);

let filterVal = ref('');
let showTotalNum = ref(false);
let sortDisable = ref(false);
let treeSelectDept = ref<TreeItemType>({});
let treeSelectNode = ref<Node | null>(null);
const treeRef = ref<InstanceType<typeof ElTree>>();
// 内部树形数据（从全量数据组织而来）
const internalTreeData = ref<TreeItemType[]>([]);
// 公司筛选数据（树形懒加载）
const selectedCompanyId = ref<string | number | undefined>(undefined);
const selectedCompanyLabel = ref<string | undefined>(undefined);
const companyTableConfig: any = {
    url: '/api/CompanyModelViewSet/',
    label: 'shortname',
    value: 'id',
    isTree: true,
    isMultiple: false,
    lazy: true,
    load: (tree: any, treeNode: any, resolve: Function) => {
        request({ url: '/api/CompanyModelViewSet/', params: { parentid: tree.id, limit: 999 } }).then((res: any) => {
            resolve(res.data || []);
        });
    },
    treeProps: { children: 'children', hasChildren: 'hasChild' },
    columns: [
        { prop: 'shortname', label: '名称', width: 150 },
        { prop: 'encode', label: '编码' },
    ],
};

watch(filterVal, (val) => {
	treeRef.value!.filter(val);
});

/**
 * 部门树的搜索事件
 */
const handleFilterTreeNode = (value: string, data: TreeItemType) => {
	if (!value) return true;
	return toRaw(data).name?.indexOf(value) !== -1;
};

/**
 * 加载部门树数据（全量）
 */
const loadDeptTree = async () => {
	// 未选择公司时，清空树
	if (!selectedCompanyId.value) {
		internalTreeData.value = [];
		return;
	}

	try {
		// 获取指定公司的全量部门数据（通过后端过滤）
		const res: any = await getAllDeptList({
			company_belong_id: selectedCompanyId.value
		});
		
		if (res?.data) {
			// 使用 XEUtils.toArrayTree 组织成树形结构
			internalTreeData.value = XEUtils.toArrayTree(res.data, {
				parentKey: 'parent',
				key: 'id',
				children: 'children',
			});
		}
	} catch (error) {
		console.error('加载部门树失败:', error);
		internalTreeData.value = [];
	}
};

/**
 * 部门的点击事件
 */
const handleNodeClick = (record: TreeItemType, node: Node) => {
	treeSelectDept.value = record;
	treeSelectNode.value = node;
    emit('treeClick', record);
};

/**
 * 新增 or 编辑 操作
 */
const handleUpdateMenu = (type: string) => {
	if (type === 'update') {
		if (!treeSelectDept.value.id) {
			warningNotification('请选择菜单！');
			return;
		}
		emit('updateDept', type, treeSelectDept.value);
	} else {
        // 创建前必须选择公司
        if (!selectedCompanyId.value) {
            warningNotification('请先选择公司！');
            return;
        }
		emit('updateDept', type);
	}
};

/**
 * 删除部门
 */
const handleDeleteDept = () => {
	if (!treeSelectDept.value.id) {
		warningNotification('请选择菜单！');
		return;
	}
	emit('deleteDept', treeSelectDept.value.id, () => {
		treeSelectDept.value = {};
	});
};

/**
 * 部门上下移动操作
 */
const handleSort = async (type: string) => {
	if (!treeSelectDept.value.id) {
		warningNotification('请选择菜单！');
		return;
	}
	if (sortDisable.value) return;

	const parentList = treeSelectNode.value?.parent?.childNodes || [];
	const index = parentList.findIndex((i) => i.data.id === treeSelectDept.value.id);
	const record = parentList.find((i) => i.data.id === treeSelectDept.value.id);

	if (type === 'up') {
		if (index === 0) return;
		parentList.splice(index - 1, 0, record as any);
		parentList.splice(index + 1, 1);
		sortDisable.value = true;
		await deptMoveUp({ dept_id: treeSelectDept.value.id });
		sortDisable.value = false;
	}
	if (type === 'down') {
		parentList.splice(index + 2, 0, record as any);
		parentList.splice(index, 1);
		sortDisable.value = true;
		await deptMoveDown({ dept_id: treeSelectDept.value.id });
		sortDisable.value = false;
	}
};

defineExpose({
	treeRef,
	loadDeptTree,
});

const handleCompanyChange = async () => {
    // 通知父组件公司变化
    emit('companyChange', selectedCompanyId.value);
    // 清空树的当前选中状态
    try {
        treeRef.value?.setCurrentKey(undefined);
    } catch (e) {
        // ignore if node-key not ready
    }
    // 重新加载部门树
    await loadDeptTree();
};

onMounted(() => {
    // 初始化时不加载，等待选择公司后加载
});
</script>

<style lang="scss" scoped>
.tc-head {
	display: flex;
	align-items: center;
	margin-left: -8px;
	color: #606266;
	font-weight: 600;

	.tc-head-txt {
		margin: 0 8px;
	}

	.tc-head-icon {
		position: relative;
		top: -1px;
		cursor: pointer;
	}
}

.tree-tags {
	height: 40px;
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	padding: 0 20px;
	display: flex;
	align-items: center;
	justify-content: space-around;
	box-sizing: border-box;

	.mlt-icon {
		cursor: pointer;
		color: var(--el-color-primary);
	}
}
</style>

<style lang="scss">
.dept-tree-com {
	height: calc(100% - 60px);
	padding: 20px;
	box-sizing: border-box;
	overflow-y: auto;

	.el-tree-node__content {
		height: 32px !important;
	}

	.el-tree .el-tree-node__expand-icon svg {
		display: none !important;
		height: 0;
		width: 0;
	}

	.el-tree-node__expand-icon {
		font-size: 16px;
	}

	.el-tree-node__content > .el-tree-node__expand-icon {
		padding: 0;
		box-sizing: border-box;
		margin-right: 5px;
		margin-left: 20px;
	}

	.el-tree .el-tree-node__expand-icon.expanded {
		-webkit-transform: rotate(0deg);
		transform: rotate(0deg);
	}

	.el-tree .el-tree-node__expand-icon.is-leaf {
		margin-left: 0;
	}

	.el-tree .el-tree-node__expand-icon:before {
		background: url('../../../../../assets/img/menu-tree-show-icon.png') no-repeat center / 100%;
		content: '';
		display: block;
		width: 24px;
		height: 24px;
	}

	.el-tree .el-tree-node__expand-icon.expanded:before {
		background: url('../../../../../assets/img/menu-tree-hidden-icon.png') no-repeat center / 100%;
		content: '';
		display: block;
		width: 24px;
		height: 24px;
	}

	.el-tree .is-leaf.el-tree-node__expand-icon::before {
		display: block;
		background: none !important;
		content: '';
		width: 18px;
		height: 18px;
		border: none;
	}
}
</style>
