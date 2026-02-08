<template>
    <el-dialog v-model="visible" title="线条信息设置" width="750px" :close-on-click-modal="false" @close="handleClose">
        <el-tabs v-model="activeTab" v-if="currentLine">
            <!-- 基本配置标签页 -->
            <el-tab-pane label="基本配置" name="baseInfo">
                <el-form ref="baseFormRef" :model="formData" label-width="120px">
                    <el-form-item label="名称">
                        <el-input v-model="formData.name" placeholder="请输入名称" clearable />
                    </el-form-item>

                    <!-- 颜色选择：仅对特定节点类型显示 -->
                    <el-form-item label="颜色" v-if="showColorConfig">
                        <el-select v-model="formData.color" placeholder="请选择颜色" style="width: 100%">
                            <el-option label="黑" value="1" />
                            <el-option label="红" value="2" />
                        </el-select>
                    </el-form-item>

                    <!-- 通过策略：仅对特定节点类型显示 -->
                    <el-form-item label="通过策略" v-if="showStrategyConfig">
                        <el-select v-model="formData.strategy" placeholder="请选择通过策略" style="width: 100%"
                                @change="handleStrategyChange">
                            <el-option label="所有情况都通过" value="1" />
                            <el-option label="自定义设置" value="2" />
                        </el-select>
                    </el-form-item>

                    <!-- 通过项：仅当策略为自定义时显示 -->
                    <el-form-item label="通过项" v-if="showAgreeList">
                        <el-select v-model="formData.agreeList" multiple placeholder="请选择通过项" style="width: 100%">
                            <el-option v-for="item in agreeListOptions" :key="item.code" :label="item.name"
                                    :value="item.code" />
                        </el-select>
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <!-- 绑定操作标签页 -->
            <el-tab-pane label="绑定操作" name="operation">
                <div style="margin-bottom: 20px;">
                    <el-radio-group v-model="formData.operationType" @change="handleOperationTypeChange">
                        <el-radio label="sql">SQL</el-radio>
                        <el-radio label="interface">接口</el-radio>
                        <el-radio label="ioc">依赖注入方法</el-radio>
                    </el-radio-group>
                </div>

                <!-- SQL 配置 -->
                <div v-show="formData.operationType === 'sql'">
                    <el-alert
                            title="注意：请在开发人员指导下进行配置SQL语句（{processId}流程发起实例主键{userId}用户Id{userAccount}用户账号{companyId}用户公司{departmentId}用户部门{code}上一节点操作码）"
                            type="warning" :closable="false" style="margin-bottom: 15px" />
                    <el-form-item label="数据库" label-width="100px">
                        <el-select v-model="formData.dbId" placeholder="请选择数据库" style="width: 100%">
                            <el-option label="默认数据库" value="default" />
                        </el-select>
                    </el-form-item>
                    <el-form-item label="SQL语句" label-width="100px">
                        <el-input v-model="formData.strSql" type="textarea" :rows="4" placeholder="请填写SQL语句" />
                    </el-form-item>
                    <el-form-item label="SQL语句(撤销)" label-width="100px">
                        <el-input v-model="formData.strSqlR" type="textarea" :rows="4" placeholder="请填写SQL语句（撤销执行）" />
                    </el-form-item>
                </div>

                <!-- 接口配置 -->
                <div v-show="formData.operationType === 'interface'">
                    <el-alert
                            title="注意：必须要开发人员指导下进行配置支持Post方法的接口,json数据格式。{processId:'流程发起实例主键',userId:'用户Id',userAccount:'用户账号',companyId:'用户公司',departmentId:'用户部门',code:'上一节点操作码'}"
                            type="warning" :closable="false" style="margin-bottom: 15px" />
                    <el-form-item label="接口地址" label-width="100px">
                        <el-input v-model="formData.strInterface" type="textarea" :rows="4" placeholder="请填写接口地址" />
                    </el-form-item>
                    <el-form-item label="接口地址(撤销)" label-width="100px">
                        <el-input v-model="formData.strInterfaceR" type="textarea" :rows="4"
                                placeholder="请填写接口地址（撤销执行）" />
                    </el-form-item>
                </div>

                <!-- IOC 配置 -->
                <div v-show="formData.operationType === 'ioc'">
                    <el-alert title="注意：必须要开发人员指导下进行配置注册的IOC方法名" type="warning" :closable="false"
                            style="margin-bottom: 15px" />
                    <el-form-item label="方法名(执行前)" label-width="120px">
                        <el-input v-model="formData.iocNameB" type="textarea" :rows="3" placeholder="请填写方法名(流程执行前执行)" />
                    </el-form-item>
                    <el-form-item label="方法名" label-width="120px">
                        <el-input v-model="formData.iocName" type="textarea" :rows="3" placeholder="请填写方法名" />
                    </el-form-item>
                    <el-form-item label="方法名(撤销)" label-width="120px">
                        <el-input v-model="formData.iocNameR" type="textarea" :rows="3" placeholder="请填写方法名（撤销执行）" />
                    </el-form-item>
                </div>
            </el-tab-pane>
        </el-tabs>

        <template #footer>
            <el-button @click="handleClose">取消</el-button>
            <el-button type="primary" @click="handleConfirm">确定</el-button>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

const visible = ref(false)
const activeTab = ref('baseInfo')
const baseFormRef = ref()
const currentLine = ref<any>(null)
const fromNode = ref<any>(null)
const allNodes = ref<any[]>([])
const updateCallback = ref<Function | null>(null)

const formData = reactive({
    name: '',
    color: '1',
    strategy: '1',
    agreeList: [] as string[],
    operationType: 'sql',
    dbId: '',
    strSql: '',
    strSqlR: '',
    strInterface: '',
    strInterfaceR: '',
    iocNameB: '',
    iocName: '',
    iocNameR: ''
})

// 通过项选项列表
const agreeListOptions = ref<any[]>([])

// 是否显示颜色配置（开始节点和子流程节点不显示）
const showColorConfig = computed(() => {
    if (!fromNode.value) return true
    const type = fromNode.value.type
    return type !== 'startround' && type !== 'childwfnode'
})

// 是否显示策略配置（开始节点和子流程节点不显示）
const showStrategyConfig = computed(() => {
    if (!fromNode.value) return true
    const type = fromNode.value.type
    return type !== 'startround' && type !== 'childwfnode'
})

// 是否显示通过项（策略为自定义时显示）
const showAgreeList = computed(() => {
    return showStrategyConfig.value && formData.strategy === '2'
})

// 策略改变事件
const handleStrategyChange = (value: string) => {
    if (value !== '2') {
        formData.agreeList = []
    }
}

// 操作类型改变事件
const handleOperationTypeChange = () => {
    // 清空其他类型的数据（可选）
}

// 初始化通过项列表
const initAgreeList = () => {
    if (!fromNode.value) return

    let list: any[] = []

    switch (fromNode.value.type) {
        case 'startround':   // 开始节点
        case 'childwfnode':  // 子流程
            // 这些节点不需要通过项
            break

        case 'stepnode':     // 一般审核节点
            if (fromNode.value.btnList && fromNode.value.btnList.length > 0) {
                list = fromNode.value.btnList.map((btn: any) => ({
                    name: btn.name,
                    code: btn.code
                }))
                // 如果有超时配置，添加超时选项
                if (fromNode.value.timeoutAction && fromNode.value.timeoutAction !== '0') {
                    list.push({ name: '超时', code: 'lrtimeout' })
                }
            } else {
                list = [
                    { name: '同意', code: 'agree' },
                    { name: '不同意', code: 'disagree' }
                ]
            }
            break

        case 'confluencenode':  // 会签
            list = [
                { name: '同意', code: 'agree' },
                { name: '不同意', code: 'disagree' }
            ]
            break

        case 'conditionnode':  // 条件
            list = [
                { name: '是', code: 'agree' },
                { name: '否', code: 'disagree' }
            ]
            break
    }

    agreeListOptions.value = list
}

// 打开对话框
const open = (lineData: any, fromNodeData: any, nodes: any[], callback?: Function) => {
    currentLine.value = lineData
    fromNode.value = fromNodeData
    allNodes.value = nodes || []
    updateCallback.value = callback || null

    // 初始化通过项列表
    initAgreeList()

    // 填充基本配置
    formData.name = lineData.name || ''
    formData.color = lineData.color || '1'
    formData.strategy = lineData.strategy || '1'
    formData.agreeList = lineData.agreeList ? (Array.isArray(lineData.agreeList) ? lineData.agreeList : lineData.agreeList.split(',')) : ['agree']

    // 填充操作配置
    formData.operationType = lineData.operationType || 'sql'
    formData.dbId = lineData.dbId || ''
    formData.strSql = lineData.strSql || ''
    formData.strSqlR = lineData.strSqlR || ''
    formData.strInterface = lineData.strInterface || ''
    formData.strInterfaceR = lineData.strInterfaceR || ''
    formData.iocNameB = lineData.iocNameB || ''
    formData.iocName = lineData.iocName || ''
    formData.iocNameR = lineData.iocNameR || ''

    activeTab.value = 'baseInfo'
    visible.value = true
}

// 关闭对话框
const handleClose = () => {
    visible.value = false
    currentLine.value = null
    fromNode.value = null
    updateCallback.value = null
}

// 确认保存
const handleConfirm = () => {
    if (!currentLine.value) return

    // 更新基本配置
    currentLine.value.name = formData.name

    // 根据节点类型保存不同的配置
    const fromType = fromNode.value?.type
    if (fromType !== 'startround' && fromType !== 'childwfnode') {
        currentLine.value.color = formData.color
        currentLine.value.strategy = formData.strategy
        currentLine.value.agreeList = formData.agreeList.join(',')
    }

    // 更新操作配置
    currentLine.value.operationType = formData.operationType

    switch (formData.operationType) {
        case 'sql':
            currentLine.value.dbId = formData.dbId
            currentLine.value.strSql = formData.strSql
            currentLine.value.strSqlR = formData.strSqlR
            break
        case 'interface':
            currentLine.value.strInterface = formData.strInterface
            currentLine.value.strInterfaceR = formData.strInterfaceR
            break
        case 'ioc':
            currentLine.value.iocNameB = formData.iocNameB
            currentLine.value.iocName = formData.iocName
            currentLine.value.iocNameR = formData.iocNameR
            break
    }

    // 调用更新回调
    if (updateCallback.value && typeof updateCallback.value === 'function') {
        updateCallback.value(currentLine.value.id)
    }

    ElMessage.success('线条配置已更新')
    handleClose()
}

// 暴露方法
defineExpose({
    open
})
</script>

<style scoped lang="scss">
:deep(.el-form-item__label) {
    font-weight: 500;
}

:deep(.el-tabs__item) {
    font-size: 14px;
    font-weight: 500;
}

:deep(.el-alert__title) {
    font-size: 13px;
    line-height: 1.6;
}
</style>
