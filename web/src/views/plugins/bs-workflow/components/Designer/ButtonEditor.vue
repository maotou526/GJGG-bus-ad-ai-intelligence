<template>
    <el-dialog v-model="visible" :title="dialogTitle" width="600px" @close="handleClose" append-to-body
            destroy-on-close>
        <el-form :model="form" label-width="130px" ref="formRef" :rules="rules">
            <el-form-item label="按钮ID">
                <el-input v-model="form.id" readonly placeholder="自动生成" />
            </el-form-item>

            <el-form-item label="按钮名称" prop="name" required>
                <el-input v-model="form.name" placeholder="请输入按钮名称，如：同意、不同意" />
            </el-form-item>

            <el-form-item label="按钮编码" prop="code" required>
                <el-input v-model="form.code" placeholder="请输入按钮编码，如：agree、disagree">
                    <template #append>
                        <el-button @click="showCodeSuggestions">常用代码</el-button>
                    </template>
                </el-input>
            </el-form-item>

            <el-form-item label="是否隐藏">
                <el-radio-group v-model="form.isHide">
                    <el-radio label="1">是</el-radio>
                    <el-radio label="2">否</el-radio>
                </el-radio-group>
            </el-form-item>

            <el-form-item label="需要签名或盖章">
                <el-radio-group v-model="form.isSign">
                    <el-radio label="1">需要</el-radio>
                    <el-radio label="2">不需要</el-radio>
                </el-radio-group>
            </el-form-item>

            <el-form-item label="下一节点审核人">
                <el-radio-group v-model="form.next">
                    <el-radio label="1">不能手动设置</el-radio>
                    <el-radio label="2">能手动设置</el-radio>
                </el-radio-group>
            </el-form-item>
        </el-form>

        <template #footer>
            <el-button @click="visible = false">取消</el-button>
            <el-button type="primary" @click="handleConfirm">确定</el-button>
        </template>
    </el-dialog>

    <!-- 常用代码选择 -->
    <el-dialog v-model="codeDialogVisible" title="常用按钮代码" width="500px" append-to-body>
        <el-table :data="commonCodes" @row-click="selectCode" highlight-current-row>
            <el-table-column label="代码" prop="code" width="150" />
            <el-table-column label="名称" prop="name" width="150" />
            <el-table-column label="说明" prop="description" />
        </el-table>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

interface ButtonForm {
    id: string
    name: string
    code: string
    isHide: string
    isSign: string
    next: string
}

const visible = ref(false)
const codeDialogVisible = ref(false)
const formRef = ref()
const editMode = ref<'add' | 'edit'>('add')
const editIndex = ref(-1)

const form = reactive<ButtonForm>({
    id: '',
    name: '',
    code: '',
    isHide: '2', // 默认不隐藏
    isSign: '2', // 默认不需要
    next: '1' // 默认不能手动设置
})

const rules = {
    name: [{ required: true, message: '请输入按钮名称', trigger: 'blur' }],
    code: [
        { required: true, message: '请输入按钮代码', trigger: 'blur' },
        { pattern: /^[a-zA-Z_][a-zA-Z0-9_]*$/, message: '只能包含字母、数字和下划线，且不能以数字开头', trigger: 'blur' }
    ]
}

// 常用按钮代码
const commonCodes = [
    { code: 'agree', name: '同意', description: '审核通过' },
    { code: 'disagree', name: '不同意', description: '审核不通过' },
    { code: 'reject', name: '驳回', description: '驳回到上一步' },
    { code: 'next', name: '下一步', description: '流转到下一步' },
    { code: 'transfer', name: '转办', description: '转给其他人处理' },
    { code: 'cancel', name: '作废', description: '作废流程' },
    { code: 'save', name: '保存', description: '保存草稿' },
    { code: 'recall', name: '撤回', description: '撤回申请' }
]

const dialogTitle = computed(() => editMode.value === 'add' ? '添加按钮' : '修改按钮')

const emit = defineEmits<{
    confirm: [data: ButtonForm, index?: number]
}>()

// 打开对话框
const open = (mode: 'add' | 'edit' = 'add', data?: ButtonForm, index?: number) => {
    editMode.value = mode
    editIndex.value = index !== undefined ? index : -1

    if (mode === 'edit' && data) {
        // 编辑模式，填充数据
        Object.assign(form, {
            id: data.id,
            name: data.name,
            code: data.code,
            isHide: data.isHide || '2',
            isSign: data.isSign || '2',
            next: data.next || '1'
        })
    } else {
        // 新增模式，重置表单
        form.id = learun.newGuid()
        form.name = ''
        form.code = ''
        form.isHide = '2'
        form.isSign = '2'
        form.next = '1'
    }

    visible.value = true
}

// 显示常用代码
const showCodeSuggestions = () => {
    codeDialogVisible.value = true
}

// 选择常用代码
const selectCode = (row: any) => {
    form.code = row.code
    form.name = row.name
    codeDialogVisible.value = false
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

:deep(.el-table) {
    cursor: pointer;
}
</style>
