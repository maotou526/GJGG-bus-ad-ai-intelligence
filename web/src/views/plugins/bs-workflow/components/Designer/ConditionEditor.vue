<template>
    <el-dialog v-model="visible" :title="dialogTitle" width="500px" @close="handleClose" append-to-body
            destroy-on-close>
        <el-form :model="form" label-width="80px" ref="formRef" :rules="rules">
            <el-form-item label="字段名" prop="fieldName" required>
                <el-input v-model="form.fieldName" placeholder="请输入字段名，如：status" />
            </el-form-item>

            <el-form-item label="比较符" prop="compare" required>
                <el-select v-model="form.compare" placeholder="请选择比较符">
                    <el-option label="等于 (=)" value="=" />
                    <el-option label="不等于 (!=)" value="!=" />
                    <el-option label="大于 (>)" value=">" />
                    <el-option label="大于等于 (>=)" value=">=" />
                    <el-option label="小于 (<)" value="<" />
                    <el-option label="小于等于 (<=)" value="<=" />
                    <el-option label="包含 (LIKE)" value="LIKE" />
                    <el-option label="不包含 (NOT LIKE)" value="NOT LIKE" />
                    <el-option label="在范围内 (IN)" value="IN" />
                    <el-option label="不在范围内 (NOT IN)" value="NOT IN" />
                </el-select>
            </el-form-item>

            <el-form-item label="值" prop="value" required>
                <el-input v-model="form.value" placeholder="请输入比较值" />
                <div class="form-help">
                    多个值用逗号分隔（IN/NOT IN时）
                </div>
            </el-form-item>

            <el-form-item label="逻辑关系" v-if="showLogic">
                <el-radio-group v-model="form.logic">
                    <el-radio label="AND">并且</el-radio>
                    <el-radio label="OR">或者</el-radio>
                </el-radio-group>
            </el-form-item>
        </el-form>

        <template #footer>
            <el-button @click="visible = false">取消</el-button>
            <el-button type="primary" @click="handleConfirm">确定</el-button>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

interface ConditionForm {
    id?: string
    fieldName: string
    compare: string
    value: string
    logic?: string
}

const visible = ref(false)
const formRef = ref()
const editMode = ref<'add' | 'edit'>('add')
const editIndex = ref(-1)
const showLogic = ref(false)

const form = reactive<ConditionForm>({
    id: '',
    fieldName: '',
    compare: '=',
    value: '',
    logic: 'AND'
})

const rules = {
    fieldName: [{ required: true, message: '请输入字段名', trigger: 'blur' }],
    compare: [{ required: true, message: '请选择比较符', trigger: 'change' }],
    value: [{ required: true, message: '请输入比较值', trigger: 'blur' }]
}

const dialogTitle = computed(() => editMode.value === 'add' ? '添加条件' : '修改条件')

const emit = defineEmits<{
    confirm: [data: ConditionForm, index?: number]
}>()

// 打开对话框
const open = (mode: 'add' | 'edit' = 'add', data?: ConditionForm, index?: number, isFirst?: boolean) => {
    editMode.value = mode
    editIndex.value = index !== undefined ? index : -1
    showLogic.value = !isFirst // 第一个条件不显示逻辑关系

    if (mode === 'edit' && data) {
        // 编辑模式，填充数据
        Object.assign(form, {
            id: data.id,
            fieldName: data.fieldName,
            compare: data.compare,
            value: data.value,
            logic: data.logic || 'AND'
        })
    } else {
        // 新增模式，重置表单
        form.id = learun.newGuid()
        form.fieldName = ''
        form.compare = '='
        form.value = ''
        form.logic = 'AND'
    }

    visible.value = true
}

// 确认
const handleConfirm = async () => {
    try {
        await formRef.value?.validate()

        const data = { ...form }

        if (editMode.value === 'edit') {
            emit('confirm', data, editIndex.value)
        } else {
            emit('confirm', data)
        }

        visible.value = false
    } catch (error) {
        console.error('表单验证失败:', error)
    }
}

const handleClose = () => {
    formRef.value?.resetFields()
    visible.value = false
}

defineExpose({
    open
})
</script>

<style scoped lang="scss">
.form-help {
    color: #909399;
    font-size: 12px;
    margin-top: 5px;
}
</style>
