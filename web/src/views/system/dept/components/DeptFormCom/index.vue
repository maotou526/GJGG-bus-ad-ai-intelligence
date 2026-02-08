<template>
<el-form ref="formRef" :rules="rules" :model="deptFormData" label-width="100px" label-position="right" class="dept-form-com">
    <el-form-item label="所属公司">
        <el-input :model-value="displayCompanyLabel" disabled placeholder="请选择公司" />
	</el-form-item>
		<el-form-item label="父级部门" prop="parent">
			<el-tree-select
				v-model="deptFormData.parent"
				:props="defaultTreeProps"
				:data="deptDefaultList"
				:cache-data="props.cacheData"
				lazy
				check-strictly
				:load="handleTreeLoad"
				style="width: 100%"
			/>
		</el-form-item>
		<el-form-item required label="部门名称" prop="name">
			<el-input v-model="deptFormData.name" />
		</el-form-item>
		<el-form-item required label="部门标识" prop="key">
			<el-input v-model="deptFormData.key" />
		</el-form-item>
		<el-form-item label="负责人">
			<el-input v-model="deptFormData.owner" placeholder="请输入" />
		</el-form-item>
		<el-form-item label="备注">
			<el-input v-model="deptFormData.description" maxlength="200" show-word-limit type="textarea" />
		</el-form-item>
		<el-form-item>
			<el-button @click="handleUpdateMenu" type="primary" :loading="deptBtnLoading">
				{{ deptFormData.id ? '保存' : '新增' }}
			</el-button>
			<el-button @click="handleClose">取消 </el-button>
		</el-form-item>
	</el-form>
</template>

<script lang="ts" setup>
import { reactive, ref, onMounted, watch } from 'vue';
import { ElForm, FormRules } from 'element-plus';
import { lazyLoadDept, AddObj, UpdateObj } from '../../api';
import { successNotification } from '/@/utils/message';
import { DeptFormDataType, TreeItemType, APIResponseData } from '../../types';
import type Node from 'element-plus/es/components/tree/src/model/node';
import { request } from '/@/utils/service';

interface IProps {
    initFormData: TreeItemType | null;
    cacheData: TreeItemType[];
    companyId?: string | number | null;
    companyLabel?: string | null;
}

const defaultTreeProps: any = {
	children: 'children',
	label: 'name',
	value: 'id',
	isLeaf: (data: TreeItemType[], node: Node) => {
		if (node?.data.hasChild) {
			return false;
		} else {
			return true;
		}
	},
};

const formRef = ref<InstanceType<typeof ElForm>>();
const rules = reactive<FormRules>({
	name: [{ required: true, message: '部门名称必填', trigger: 'blur' }],
	key: [{ required: true, message: '部门标识必填', trigger: 'blur' }],
});

const props = withDefaults(defineProps<IProps>(), {
    cacheData: () => [],
    companyId: null,
    companyLabel: '',
});
const emit = defineEmits(['drawerClose']);

let deptDefaultList = ref<TreeItemType[]>([]);
let deptFormData = reactive<DeptFormDataType>({
	key: '',
	parent: '',
	name: '',
	owner: '',
	description: '',
});
let deptBtnLoading = ref(false);
let displayCompanyLabel = ref<string>('');

const setDeptFormData = () => {
	if (props.initFormData?.id) {
		deptFormData.id = props.initFormData?.id;
		deptFormData.key = props.initFormData.key || '';
		deptFormData.parent = props.initFormData.parent || '';
		deptFormData.name = props.initFormData.name || '';
		deptFormData.owner = props.initFormData.owner || '';
		deptFormData.description = props.initFormData.description || '';
	}
};

const loadCompanyLabel = async () => {
    displayCompanyLabel.value = '';
    if (!props.companyId) return;
    try {
        const res: any = await request({ url: `/api/CompanyModelViewSet/${props.companyId}`, method: 'get' });
        displayCompanyLabel.value = res?.data?.shortname || res?.data?.fullname || '';
    } catch (e) {
        displayCompanyLabel.value = '';
    }
};

const handleTreeLoad = (node: Node, resolve: Function) => {
	if (node.level !== 0) {
        lazyLoadDept({ parent: node.data.id, company_belong_id: props.companyId }).then((res: APIResponseData) => {
			resolve(res.data);
		});
	}
};

const handleUpdateMenu = () => {
	formRef.value?.validate(async (valid) => {
		if (!valid) return;
		try {
			let res;
			deptBtnLoading.value = true;
            // 写入所属公司（从父组件传入的筛选公司）
            if (props.companyId) {
                (deptFormData as any).company_belong_id = props.companyId;
            }
			if (deptFormData.id) {
				res = await UpdateObj(deptFormData);
			} else {
				res = await AddObj(deptFormData);
			}
			if (res?.code === 2000) {
				successNotification(res.msg as string);
				handleClose('submit');
			}
		} finally {
			deptBtnLoading.value = false;
		}
	});
};

const handleClose = (type: string = '') => {
	emit('drawerClose', type);
	formRef.value?.resetFields();
};

onMounted(async () => {
	// 使用懒加载，不需要预设 treeData
	setDeptFormData();
    await loadCompanyLabel();
});

watch(() => props.companyId, async () => {
    await loadCompanyLabel();
});
</script>

<style lang="scss" scoped>
.dept-form-com {
	height: 100%;
	padding: 20px;
	box-sizing: border-box;
}
</style>
