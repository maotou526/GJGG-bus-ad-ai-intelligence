<template>
	<fs-page>
		<el-row class="dept-el-row">
			<el-col :span="6">
				<div class="dept-box dept-left">
					<DeptTreeCom ref="deptTreeRef" @companyChange="handleCompanyChange"
							@treeClick="handleTreeClick" @updateDept="handleUpdateMenu"
							@deleteDept="handleDeleteMenu" />
				</div>
			</el-col>

			<el-col :span="18">
				<div class="dept-box dept-table">
					<DeptUserCom 
						v-if="selectedDeptId" 
						ref="deptUserRef" 
						:selectedCompanyId="selectedCompanyId"
						:selectedDeptId="selectedDeptId"
					/>
				</div>
			</el-col>
		</el-row>

		<el-drawer v-model="drawerVisible" title="部门配置" direction="rtl" size="500px" :close-on-click-modal="false"
				:before-close="handleDrawerClose">
			<DeptFormCom v-if="drawerVisible" :initFormData="drawerFormData"
					:cacheData="deptTreeCacheData" :companyId="selectedCompanyId" :companyLabel="companyLabel" @drawerClose="handleDrawerClose" />
		</el-drawer>
	</fs-page>
</template>

<script lang="ts" setup name="dept">
import { ref, onMounted, nextTick } from 'vue';
import { ElMessageBox } from 'element-plus';
import DeptTreeCom from './components/DeptTreeCom/index.vue';
import DeptFormCom from './components/DeptFormCom/index.vue';
import DeptUserCom from './components/DeptUserCom/index.vue';
import { DelObj } from './api';
import { successNotification } from '../../../utils/message';
import { APIResponseData, TreeItemType } from './types';

let selectedCompanyId = ref<string | number | undefined>(undefined);
let companyLabel = ref<string>('');
let selectedDeptId = ref<string | number | undefined>('');
let deptTreeCacheData = ref<TreeItemType[]>([]);
let drawerVisible = ref(false);
let drawerFormData = ref<Partial<TreeItemType>>({});
let deptUserRef = ref<InstanceType<typeof DeptUserCom> | null>(null);
let deptTreeRef = ref<InstanceType<typeof DeptTreeCom> | null>(null);

/**
 * 部门的点击事件
 */
const handleTreeClick = async (record: TreeItemType) => {
	selectedDeptId.value = record.id as string;
		// 等待组件渲染完成后再调用刷新方法
	await nextTick();
	deptUserRef.value?.handleDoRefreshUser(record.id as string);
};

/**
 * 部门的删除事件
 */
const handleDeleteMenu = (id: string, callback: Function) => {
	ElMessageBox.confirm('您确认删除该部门吗?', '温馨提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	}).then(async () => {
		const res: APIResponseData = await DelObj(id);
		callback();
		if (res?.code === 2000) {
			successNotification(res.msg as string);
			// 刷新部门树
			deptTreeRef.value?.loadDeptTree();
			deptUserRef.value?.handleDoRefreshUser('');
			selectedDeptId.value = '';
		}
	});
};

// 切换公司筛选
const handleCompanyChange = (companyId: string | number | undefined) => {
    selectedCompanyId.value = companyId;
    // 清空右侧用户表
    deptUserRef.value?.handleDoRefreshUser('');
    selectedDeptId.value = '';
};

/**
 * 部门的 新增 or 编辑 事件
 */
const handleUpdateMenu = (type: string, record?: TreeItemType) => {
	if (type === 'update' && record) {
		const parentData = deptTreeRef.value?.treeRef?.currentNode?.parent?.data || {};
		deptTreeCacheData.value = [parentData];
		drawerFormData.value = record;
	}
	drawerVisible.value = true;
};
const handleDrawerClose = (type?: string) => {
	if (type === 'submit') {
		// 刷新部门树
		deptTreeRef.value?.loadDeptTree();
	}
	drawerVisible.value = false;
	drawerFormData.value = {};
};

onMounted(() => {
	// 部门树数据由 DeptTreeCom 内部管理，无需在此初始化
});
</script>

<style lang="scss" scoped>
.dept-el-row {
	height: 100%;
	overflow: hidden;

	.el-col {
		height: 100%;
		padding: 10px 0;
		box-sizing: border-box;
	}
}

.dept-box {
	height: 100%;
	position: relative;
	box-sizing: border-box;
}

.dept-left {
	background-color: var(--el-fill-color-blank);;
	border-radius: 0 8px 8px 0;
	padding: 10px;
}

.dept-table {
	margin-left: 10px;
	padding-bottom: 10px;
}
</style>
