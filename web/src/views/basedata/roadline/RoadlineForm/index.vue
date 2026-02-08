<template>
    <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        :disabled="isFormDisabled"
        label-width="120px"
        class="roadline-form"
    >
        <el-row :gutter="20">
            <!-- 基本信息 -->
            <el-col :span="24">
                <el-divider content-position="left">基本信息</el-divider>
            </el-col>

            <el-col :span="12">
                <el-form-item label="线路名称" prop="line_name">
                    <el-input v-model="formData.line_name" placeholder="请输入线路名称" />
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="所属公司" prop="company_belong_id">
                    <CompanySelector
                        v-model="formData.company_belong_id"
                        @change="handleCompanyChange"
                        placeholder="请选择所属公司"
                    />
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="车队" prop="branch">
                    <el-input v-model="formData.branch" placeholder="请输入车队" />
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="线路类型" prop="line_type">
                    <el-select v-model="formData.line_type" placeholder="请选择线路类型" clearable style="width: 100%">
                        <el-option
                            v-for="item in lineTypeOptions"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                        />
                    </el-select>
                </el-form-item>
            </el-col>

            <!-- 编码信息 -->
            <el-col :span="24">
                <el-divider content-position="left">编码信息</el-divider>
            </el-col>

            <el-col :span="12">
                <el-form-item label="企业线路编码" prop="normal_code">
                    <el-input v-model="formData.normal_code" placeholder="请输入企业线路编码" />
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="行业线路编号" prop="ygc_code">
                    <el-input v-model="formData.ygc_code" placeholder="请输入行业线路编号" />
                </el-form-item>
            </el-col>

            <!-- 运营信息 -->
            <el-col :span="24">
                <el-divider content-position="left">运营信息</el-divider>
            </el-col>

            <el-col :span="12">
                <el-form-item label="线路长度" prop="line_length">
                    <el-input-number
                        v-model="formData.line_length"
                        :precision="2"
                        :min="0"
                        placeholder="请输入"
                        style="width: 100%"
                    />
                    <span class="unit-text">km</span>
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="线路状态" prop="line_status">
                    <el-select v-model="formData.line_status" placeholder="请选择线路状态" clearable style="width: 100%">
                        <el-option label="正常运营" value="正常运营" />
                        <el-option label="停运" value="停运" />
                    </el-select>
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="售票方式" prop="sell_type">
                    <el-select v-model="formData.sell_type" placeholder="请选择售票方式" clearable style="width: 100%">
                        <el-option label="无人售票" :value="1" />
                        <el-option label="有人售票" :value="2" />
                    </el-select>
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="运营时段分类" prop="yy_type">
                    <el-select v-model="formData.yy_type" placeholder="请选择运营时段分类" clearable style="width: 100%">
                        <el-option label="全日线" :value="1" />
                        <el-option label="高峰线" :value="2" />
                        <el-option label="夜宵线" :value="3" />
                    </el-select>
                </el-form-item>
            </el-col>

            <!-- 票价信息 -->
            <el-col :span="24">
                <el-divider content-position="left">票价信息</el-divider>
            </el-col>

            <el-col :span="12">
                <el-form-item label="票价类型" prop="ticket_price_type">
                    <el-select v-model="formData.ticket_price_type" placeholder="请选择票价类型" clearable style="width: 100%">
                        <el-option label="单一票价" :value="1" />
                        <el-option label="多级票价" :value="2" />
                    </el-select>
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="票价" prop="ticket_price">
                    <el-input-number
                        v-model="formData.ticket_price"
                        :precision="2"
                        :min="0"
                        placeholder="请输入"
                        style="width: 100%"
                    />
                    <span class="unit-text">元</span>
                </el-form-item>
            </el-col>

            <!-- 其他设置 -->
            <el-col :span="24">
                <el-divider content-position="left">其他设置</el-divider>
            </el-col>

            <el-col :span="12">
                <el-form-item label="挂牌类型" prop="listing_type">
                    <el-select v-model="formData.listing_type" placeholder="请选择挂牌类型" clearable style="width: 100%">
                        <el-option label="无挂牌" :value="1" />
                        <el-option label="全日挂牌" :value="2" />
                        <el-option label="高峰挂牌" :value="3" />
                    </el-select>
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="定班类型" prop="schedule_type">
                    <el-select v-model="formData.schedule_type" placeholder="请选择定班类型" clearable style="width: 100%">
                        <el-option label="无定班" :value="1" />
                        <el-option label="定班线" :value="2" />
                    </el-select>
                </el-form-item>
            </el-col>

            <el-col :span="12">
                <el-form-item label="启用状态" prop="enabled_mark">
                    <el-select v-model="formData.enabled_mark" placeholder="请选择启用状态" clearable style="width: 100%">
                        <el-option label="启用" :value="1" />
                        <el-option label="禁用" :value="0" />
                    </el-select>
                </el-form-item>
            </el-col>
        </el-row>
    </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import CompanySelector from '/@/components/CompanySelector/index.vue'
import { GetObj, UpdateObj } from '/@/views/basedata/roadline/RoadlineModelViewSet/api'

// Props
const props = defineProps<{
    /** 是否只读模式 */
    readonly?: boolean
    /** 初始数据 */
    data?: Record<string, any>
    /** 节点ID（可用于控制不同节点显示不同字段） */
    nodeId?: string
    /** URL参数（来自工作流表单配置） */
    formParams?: Record<string, string>
}>()

// 计算是否禁用表单：readonly 属性或 viewFlag=1 参数
const isFormDisabled = computed(() => {
    return props.readonly || props.formParams?.viewFlag === '1'
})

// Emits
const emit = defineEmits<{
    change: [data: Record<string, any>]
}>()

// 表单引用
const formRef = ref()

// 表单数据
const formData = reactive({
    id: '',
    line_name: '',
    company_belong_id: '',
    company_code: '',
    company_name: '',
    branch: '',
    normal_code: '',
    ygc_code: '',
    line_length: null as number | null,
    line_type: '',
    sell_type: null as number | null,
    ticket_price_type: null as number | null,
    ticket_price: null as number | null,
    yy_type: null as number | null,
    listing_type: null as number | null,
    schedule_type: null as number | null,
    enabled_mark: 1,
    line_status: '正常运营'
})

// 表单验证规则
const rules = {
    line_name: [{ required: true, message: '请输入线路名称', trigger: 'blur' }],
    company_belong_id: [{ required: true, message: '请选择所属公司', trigger: 'change' }]
}

// 线路类型选项（直接配置，不使用字典）
const lineTypeOptions = [
    { value: 0, label: '普通' },
    { value: 1, label: '挂牌线' },
    { value: 2, label: '区间' },
    { value: 3, label: '同名区间' },
    { value: 4, label: '定班线' },
    { value: 5, label: '定制公交' },
    { value: 6, label: '高峰线' },
    { value: 7, label: '夜宵线' },
    { value: 8, label: '低谷定班线' },
]

// 公司选择变化
const handleCompanyChange = (value: any, row: any) => {
    if (value && row) {
        formData.company_code = row.encode || ''
        formData.company_name = row.shortname || ''
    } else {
        formData.company_code = ''
        formData.company_name = ''
    }
}

// 监听数据变化，同步到 formData
watch(
    () => props.data,
    (newData) => {
        if (newData) {
            Object.keys(formData).forEach((key) => {
                if (key in newData) {
                    (formData as any)[key] = newData[key]
                }
            })
        }
    },
    { immediate: true, deep: true }
)

// 监听 formData 变化，触发 change 事件
watch(
    formData,
    (newData) => {
        emit('change', { ...newData })
    },
    { deep: true }
)

// ========== 基础方法 ==========

/**
 * 表单验证（工作流规范：返回 boolean）
 */
const validate = async (): Promise<boolean> => {
    try {
        await formRef.value?.validate()
        return true
    } catch {
        return false
    }
}

// 重置表单
const resetFields = () => {
    formRef.value?.resetFields()
}

// 获取表单数据
const getFormData = () => {
    return { ...formData }
}

// 设置表单数据
const setFormData = (data: Record<string, any>) => {
    Object.keys(formData).forEach((key) => {
        if (key in data) {
            (formData as any)[key] = data[key]
        }
    })
}

// 根据ID加载数据
const loadDataById = async (id: string) => {
    if (!id) return
    try {
        const res: any = await GetObj(id as any)
        if (res.code === 2000 && res.data) {
            setFormData(res.data)
        }
    } catch (e) {
        console.error('[RoadlineForm] 加载数据失败:', e)
    }
}

// ========== 工作流集成方法 ==========

/**
 * 保存表单数据（工作流规范：审批成功后调用）
 */
const save = async (): Promise<boolean> => {
    if (!formData.id) {
        console.warn('[RoadlineForm] 保存失败：缺少数据ID')
        return false
    }
    try {
        const res: any = await UpdateObj({ ...formData } as any)
        if (res.code === 2000) {
            ElMessage.success('表单数据保存成功')
            return true
        }
        throw new Error(res.msg || '保存失败')
    } catch (e: any) {
        console.error('[RoadlineForm] 保存失败:', e)
        throw e  // 抛出异常让容器处理
    }
}

/**
 * 审批前钩子（工作流规范：可选）
 * @param _operationCode 操作码（agree/disagree等）
 * @param _operationName 操作名称
 * @returns 返回 false 阻止审批继续
 */
const onBeforeAudit = async (_operationCode: string, _operationName: string): Promise<boolean> => {
    // 示例：可以在这里添加业务逻辑检查
    // if (_operationCode === 'agree' && !formData.line_length) {
    //     ElMessage.warning('请填写线路长度')
    //     return false
    // }
    return true
}

/**
 * 审批后钩子（工作流规范：可选）
 * @param _operationCode 操作码
 * @param operationName 操作名称
 * @param success 审批是否成功
 */
const onAfterAudit = (_operationCode: string, operationName: string, success: boolean): void => {
    if (success) {
        console.log(`[RoadlineForm] 审批成功: ${operationName}`)
    } else {
        console.log(`[RoadlineForm] 审批失败: ${operationName}`)
    }
}

onMounted(() => {
    // 如果 formParams 中有 id，根据 ID 加载数据
    if (props.formParams?.id) {
        loadDataById(props.formParams.id)
    }
})

// 暴露方法给父组件（包含工作流规范方法）
defineExpose({
    // 基础方法
    formData,
    formRef,
    resetFields,
    getFormData,
    setFormData,
    loadDataById,
    // 工作流规范方法
    validate,       // 必须：表单验证
    save,           // 可选：保存表单数据（审批成功后调用）
    onBeforeAudit,  // 可选：审批前钩子
    onAfterAudit    // 可选：审批后钩子
})
</script>

<style lang="scss" scoped>
.roadline-form {
    padding: 10px;

    .el-divider {
        margin: 15px 0;

        :deep(.el-divider__text) {
            font-weight: bold;
            color: var(--el-color-primary);
        }
    }

    .unit-text {
        margin-left: 8px;
        color: var(--el-text-color-secondary);
    }

    .el-form-item {
        margin-bottom: 18px;
    }
}
</style>
