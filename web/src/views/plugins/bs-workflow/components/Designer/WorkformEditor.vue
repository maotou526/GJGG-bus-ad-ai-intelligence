<template>
    <el-dialog v-model="visible" :title="dialogTitle" width="600px" @close="handleClose" append-to-body
            destroy-on-close>
        <el-form :model="form" label-width="100px" ref="formRef" :rules="rules">
            <el-form-item label="表单类型" prop="type" required>
                <el-radio-group v-model="form.type" @change="handleTypeChange">
                    <el-radio label="1" disabled>自定义表单</el-radio>
                    <el-radio label="0">系统表单</el-radio>
                </el-radio-group>
            </el-form-item>

            <!-- 自定义表单 -->
            <template v-if="form.type === '1'">
                <el-form-item label="表单选择" prop="formId">
                    <el-select v-model="form.formId" placeholder="请选择表单" filterable @change="handleFormChange">
                        <el-option v-for="item in formList" :key="item.id" :label="item.name" :value="item.id" />
                    </el-select>
                    <el-button class="ml-2" @click="previewForm" :disabled="!form.formId">预览表单</el-button>
                </el-form-item>

                <el-form-item label="关联字段" prop="field" required>
                    <el-select v-model="form.field" placeholder="请选择字段" filterable>
                        <el-option v-for="item in fieldList" :key="item.id" :label="item.text" :value="item.id" />
                    </el-select>
                </el-form-item>
            </template>

            <el-form-item label="表单名称" prop="name" required>
                <el-input v-model="form.name" placeholder="请输入名称" />
            </el-form-item>

            <el-form-item label="表单地址" prop="url" required>
                <el-input v-model="form.url" placeholder="例如: basedata/roadline/RoadlineForm?viewFlag=1" />
                <div class="form-item-tip">
                    <el-text type="info" size="small">
                        填写相对于 /src/views/ 的路径，支持 URL 参数。<br />
                        示例：basedata/roadline/RoadlineForm?viewFlag=1&readonly=true<br />
                        参数会通过 formParams 属性传递给表单组件
                    </el-text>
                </div>
            </el-form-item>

            <!-- 系统表单 -->
            <el-form-item label="移动表单地址" v-if="form.type === '0'">
                <el-input v-model="form.appurl" placeholder="请输入移动表单地址" />
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
import { ElMessage } from 'element-plus'

interface WorkformData {
    id: string
    type: string      // 1=自定义表单, 0=系统表单
    formId?: string   // 表单选择（自定义表单）
    field?: string    // 关联字段（自定义表单）
    name: string      // 表单名称
    url: string       // 表单地址
    appurl?: string   // 移动表单地址（系统表单）
}

const visible = ref(false)
const formRef = ref()
const editMode = ref<'add' | 'edit'>('add')
const editIndex = ref(-1)

const form = reactive<WorkformData>({
    id: '',
    type: '1',
    formId: '',
    field: '',
    name: '',
    url: '',
    appurl: ''
})

const formList = ref<any[]>([])
const fieldList = ref<any[]>([])

const rules = {
    type: [{ required: true, message: '请选择表单类型', trigger: 'change' }],
    name: [{ required: true, message: '请输入表单名称', trigger: 'blur' }],
    url: [{ required: true, message: '请输入表单地址', trigger: 'blur' }],
    field: [{ required: true, message: '请选择关联字段', trigger: 'change' }]
}

const dialogTitle = computed(() => editMode.value === 'add' ? '添加表单' : '修改表单')

const emit = defineEmits<{
    confirm: [data: WorkformData, index?: number]
}>()

// 打开对话框
const open = (mode: 'add' | 'edit' = 'add', data?: WorkformData, index?: number) => {
    editMode.value = mode
    editIndex.value = index !== undefined ? index : -1

    if (mode === 'edit' && data) {
        // 编辑模式，填充数据
        Object.assign(form, {
            id: data.id,
            type: data.type || '1',
            formId: data.formId || '',
            field: data.field || '',
            name: data.name,
            url: data.url,
            appurl: data.appurl || ''
        })
    } else {
        // 新增模式，重置表单
        form.id = learun.newGuid()
        form.type = '0'
        form.formId = ''
        form.field = ''
        form.name = ''
        form.url = ''
        form.appurl = ''
    }

    // 加载表单列表（自定义表单）
    if (form.type === '1') {
        loadFormList()
    }

    visible.value = true
}

// 加载表单列表
const loadFormList = async () => {
    try {
        // TODO: 调用API获取自定义表单列表
        // const res = await axios.get('/LR_FormModule/Custmerform/GetSchemeInfoList')
        formList.value = [
            { id: 'form_001', name: '自定义表单1' },
            { id: 'form_002', name: '自定义表单2' }
        ]
    } catch (error) {
        console.error('加载表单列表失败:', error)
    }
}

// 表单类型切换
const handleTypeChange = (type: string) => {
    if (type === '1') {
        // 切换到自定义表单
        loadFormList()
        form.appurl = ''
    } else {
        // 切换到系统表单
        form.formId = ''
        form.field = ''
        fieldList.value = []
    }
}

// 表单选择变化
const handleFormChange = async (formId: string) => {
    if (!formId) {
        form.name = ''
        form.url = ''
        fieldList.value = []
        return
    }

    try {
        const selectedForm = formList.value.find(f => f.id === formId)
        if (selectedForm) {
            form.name = selectedForm.name
            form.url = `/LR_FormModule/Custmerform/WorkflowInstanceForm?id=${formId}`
        }

        // TODO: 加载表单字段
        // const res = await axios.get(`/LR_FormModule/Custmerform/GetFormData?keyValue=${formId}`)
        // 解析scheme获取字段列表
        fieldList.value = [
            { id: 'field_001', text: '字段1' },
            { id: 'field_002', text: '字段2' }
        ]
    } catch (error) {
        console.error('加载表单字段失败:', error)
    }
}

// 预览表单
const previewForm = () => {
    if (!form.formId) {
        ElMessage.warning('请选择表单')
        return
    }

    // TODO: 打开预览窗口
    console.log('预览表单:', form.formId)
    ElMessage.info('预览功能待实现')
}

// 确认
const handleConfirm = async () => {
    try {
        await formRef.value?.validate()

        // 自定义表单必须选择关联字段
        if (form.type === '1' && !form.field) {
            ElMessage.error('请选择【关联字段】')
            return
        }

        const data = { ...form }

        // 系统表单清空formId
        if (data.type !== '1') {
            data.formId = ''
        }

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
.ml-2 {
    margin-left: 8px;
}

.form-item-tip {
    margin-top: 4px;
    line-height: 1.4;
}
</style>
