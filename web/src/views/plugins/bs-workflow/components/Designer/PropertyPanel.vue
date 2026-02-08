<template>
    <el-drawer v-model="visible" :title="title" size="700px" @close="handleClose" append-to-body destroy-on-close>
        <el-tabs v-model="activeTab" class="node-config-tabs">
            <!-- 1. 基本配置 -->
            <el-tab-pane label="基本配置" name="baseInfo">
                <el-form label-width="120px" :model="form" class="node-form" :disabled="isReadonly">
                    <el-form-item label="节点标识">
                        <el-input v-model="form.id" readonly />
                    </el-form-item>

                    <el-form-item label="节点名称" required>
                        <el-input v-model="form.name" placeholder="请输入名称" :readonly="isNameReadonly" />
                    </el-form-item>

                    <!-- 通知策略 (开始节点、审核节点、传阅节点) -->
                    <el-form-item label="通知策略" v-if="showNotice">
                        <el-select v-model="form.notice" placeholder="请选择通知策略" clearable>
                            <el-option label="流程审核通知" value="workflowNotice" />
                            <el-option label="流程审核超时通知" value="workflowTimeout" />
                        </el-select>
                    </el-form-item>

                    <!-- 下一节点审核人 (开始节点) -->
                    <template v-if="showNext">
                        <el-form-item label="下一节点审核人">
                            <el-radio-group v-model="form.isNext">
                                <el-radio label="1">允许手动指定</el-radio>
                                <el-radio label="2">不允许手动指定</el-radio>
                            </el-radio-group>
                        </el-form-item>

                        <el-form-item label="自定义标题">
                            <el-radio-group v-model="form.isTitle">
                                <el-radio label="1">允许</el-radio>
                                <el-radio label="2">不允许</el-radio>
                            </el-radio-group>
                        </el-form-item>
                    </template>

                    <!-- 审核者配置 (审核节点、会签节点、传阅节点) -->
                    <template v-if="showAuditor">
                        <el-form-item label="所有审核者">
                            <el-radio-group v-model="form.isAllAuditor" @change="handleAuditorTypeChange">
                                <el-radio label="1">只要其中一人审核</el-radio>
                                <el-radio label="2">都需要审核</el-radio>
                            </el-radio-group>
                        </el-form-item>

                        <!-- 审核执行策略 (审核节点且都需要审核时) -->
                        <template v-if="showAuditorType">
                            <el-form-item label="审核执行策略">
                                <el-radio-group v-model="form.auditExecutType">
                                    <el-radio label="1">有人不同意流转</el-radio>
                                    <el-radio label="2">所有人审核完</el-radio>
                                </el-radio-group>
                            </el-form-item>

                            <el-form-item label="再次审核">
                                <el-radio-group v-model="form.auditorAgainType">
                                    <el-radio label="1">已通过不需要审核</el-radio>
                                    <el-radio label="2">已通过需要审核</el-radio>
                                </el-radio-group>
                            </el-form-item>

                            <el-form-item label="审核方式">
                                <el-radio-group v-model="form.auditorType">
                                    <el-radio label="1">并行</el-radio>
                                    <el-radio label="2">串行</el-radio>
                                </el-radio-group>
                            </el-form-item>
                        </template>
                    </template>

                    <!-- 允许加签 (审核节点) -->
                    <el-form-item label="允许加签" v-if="showSign">
                        <el-radio-group v-model="form.isSign">
                            <el-radio label="1">是</el-radio>
                            <el-radio label="2">否</el-radio>
                        </el-radio-group>
                    </el-form-item>

                    <!-- 允许批量审核 (审核节点、传阅节点) -->
                    <el-form-item label="允许批量审核" v-if="showBatchAudit">
                        <el-radio-group v-model="form.isBatchAudit">
                            <el-radio label="1">是</el-radio>
                            <el-radio label="2">否</el-radio>
                        </el-radio-group>
                    </el-form-item>

                    <!-- 自动同意规则 (审核节点) -->
                    <el-form-item label="自动同意规则" v-if="showAgreeGz">
                        <el-select v-model="form.agreeGz" multiple placeholder="请选择">
                            <el-option label="处理人就是提交人" value="1" />
                            <el-option label="处理人和上一步的处理人相同" value="2" />
                            <el-option label="处理人审批过" value="3" />
                        </el-select>
                    </el-form-item>

                    <!-- 无对应处理人 (审核节点) -->
                    <el-form-item label="无对应处理人" v-if="showNoPeopleGz">
                        <el-radio-group v-model="form.noPeopleGz">
                            <el-radio label="1">超级管理员处理</el-radio>
                            <el-radio label="2">跳过此步骤</el-radio>
                            <el-radio label="3">不能提交</el-radio>
                        </el-radio-group>
                    </el-form-item>

                    <!-- 会签策略 (会签节点) -->
                    <template v-if="showConfluence">
                        <el-form-item label="会签策略" required>
                            <el-select v-model="form.confluenceType" placeholder="请选择">
                                <el-option label="所有步骤通过" value="1" />
                                <el-option label="一个步骤通过即可" value="2" />
                                <el-option label="按百分比计算" value="3" />
                            </el-select>
                        </el-form-item>

                        <el-form-item label="会签比例">
                            <el-input-number v-model="form.confluenceRate" :min="0" :max="100" /> %
                        </el-form-item>
                    </template>

                    <!-- 子流程 (子流程节点) -->
                    <template v-if="showChild">
                        <el-form-item label="子流程" required>
                            <el-input v-model="form.childFlow" placeholder="请选择子流程" />
                        </el-form-item>

                        <el-form-item label="子流程执行策略" required>
                            <el-radio-group v-model="form.childType">
                                <el-radio label="1">同步</el-radio>
                                <el-radio label="2">异步</el-radio>
                            </el-radio-group>
                        </el-form-item>
                    </template>
                </el-form>
            </el-tab-pane>

            <!-- 2. 审核者 -->
            <el-tab-pane label="审核者" name="auditor" v-if="showAuditorTab">
                <div class="tab-pane-content">
                    <el-table :data="form.auditors" border height="400">
                        <el-table-column label="类型" width="100" align="center">
                            <template #default="{ row }">
                                {{ getAuditorTypeName(row.type) }}
                            </template>
                        </el-table-column>
                        <el-table-column label="名称" prop="auditorName" min-width="200" />
                        <el-table-column label="附加条件" width="150">
                            <template #default="{ row }">
                                {{ getConditionName(row.condition) }}
                            </template>
                        </el-table-column>
                        <el-table-column v-if="!isReadonly" label="操作" width="80" align="center">
                            <template #default="{ $index }">
                                <el-button type="danger" link @click="removeAuditor($index)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>

                    <template v-if="!isReadonly">
                        <div class="btn-group mt-3">
                            <div class="category-label">常用设置</div>
                            <el-button @click="addAuditor('role')" type="primary">添加角色</el-button>
                            <el-button @click="addAuditor('user')" type="primary">添加人员</el-button>
                            <el-button @click="addAuditor('node')" type="primary">添加节点执行人</el-button>
                            <el-button @click="addAuditor('ioc')" type="primary">IOC注入添加</el-button>
                        </div>
                        <div class="btn-group mt-2">
                            <div class="category-label">其他设置 (暂未开放)</div>
                            <el-button @click="notImplemented('岗位')" type="info" plain>添加岗位</el-button>
                            <el-button @click="notImplemented('上下级')" type="info" plain>添加上下级</el-button>
                            <el-button @click="notImplemented('表字段')" type="info" plain>添加表字段</el-button>
                        </div>
                    </template>
                </div>
            </el-tab-pane>

            <!-- 3. 表单设置 -->
            <el-tab-pane label="表单设置" name="workform" v-if="showWorkformTab">
                <div class="tab-pane-content">
                    <el-table :data="form.wfForms" border height="400">
                        <el-table-column label="表单类型" width="100" align="center">
                            <template #default="{ row }">
                                <el-tag v-if="row.type === '1'" type="success">自定义</el-tag>
                                <el-tag v-else type="warning">系统</el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="表单名称" prop="name" width="150" />
                        <el-table-column label="表单地址" prop="url" min-width="200" show-overflow-tooltip />
                        <el-table-column v-if="!isReadonly" label="操作" width="150" align="center">
                            <template #default="{ $index }">
                                <el-button link @click="editWorkform($index)">修改</el-button>
                                <el-button type="danger" link @click="removeWorkform($index)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>

                    <div v-if="!isReadonly" class="btn-group mt-3">
                        <el-button type="success" @click="addWorkform">添加</el-button>
                    </div>
                </div>
            </el-tab-pane>

            <!-- 4. 超时设置 -->
            <el-tab-pane label="超时设置" name="timeout" v-if="showTimeoutTab">
                <el-form label-width="120px" :model="form" class="node-form" :disabled="isReadonly">
                    <el-form-item label="通知时间(时)">
                        <el-input-number v-model="form.timeoutNotice" :min="0" />
                    </el-form-item>

                    <el-form-item label="通知间隔(时)">
                        <el-input-number v-model="form.timeoutInterval" :min="0" />
                    </el-form-item>

                    <el-form-item label="通知策略">
                        <el-select v-model="form.timeoutStrategy" placeholder="请选择通知策略" clearable>
                            <el-option label="流程审核通知" value="workflowNotice" />
                            <el-option label="流程审核超时通知" value="workflowTimeout" />
                        </el-select>
                    </el-form-item>

                    <el-form-item label="流转时间(时)">
                        <el-input-number v-model="form.timeoutAction" :min="0" />
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <!-- 5. 按钮设置 -->
            <el-tab-pane label="按钮设置" name="btnSetting" v-if="showBtnSettingTab">
                <div class="tab-pane-content">
                    <el-table :data="form.btnList" border height="400">
                        <el-table-column label="按钮名称" prop="name" width="100" />
                        <el-table-column label="按钮编码" prop="code" width="100" />
                        <el-table-column label="隐藏" width="70" align="center">
                            <template #default="{ row }">
                                <el-tag v-if="row.isHide === '1'" type="info">是</el-tag>
                                <el-tag v-else type="success">否</el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="签章" width="70" align="center">
                            <template #default="{ row }">
                                <el-tag v-if="row.isSign === '1'" type="success">是</el-tag>
                                <el-tag v-else type="info">否</el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column label="下一节点" width="90" align="center">
                            <template #default="{ row }">
                                <el-tag v-if="row.next === '2'" type="success">可设</el-tag>
                                <el-tag v-else type="info">不可</el-tag>
                            </template>
                        </el-table-column>
                        <el-table-column v-if="!isReadonly" label="操作" width="120" align="center">
                            <template #default="{ $index }">
                                <el-button link @click="editButton($index)">修改</el-button>
                                <el-button type="danger" link @click="removeButton($index)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>

                    <div v-if="!isReadonly" class="btn-group mt-3">
                        <el-button type="success" @click="addButton">添加</el-button>
                    </div>
                </div>
            </el-tab-pane>

            <!-- 6. 字段条件设置 -->
            <el-tab-pane label="字段条件设置" name="conditionField" v-if="showConditionFieldTab">
                <div class="tab-pane-content">
                    <el-table :data="form.conditions" border height="400">
                        <el-table-column label="字段名" prop="fieldName" width="150" />
                        <el-table-column label="比较符" prop="compare" width="100" />
                        <el-table-column label="值" prop="value" min-width="150" />
                        <el-table-column v-if="!isReadonly" label="操作" width="150" align="center">
                            <template #default="{ $index }">
                                <el-button link @click="editCondition($index)">修改</el-button>
                                <el-button type="danger" link @click="removeCondition($index)">删除</el-button>
                            </template>
                        </el-table-column>
                    </el-table>

                    <div v-if="!isReadonly" class="btn-group mt-3">
                        <el-button type="success" @click="addCondition">添加</el-button>
                    </div>
                </div>
            </el-tab-pane>

            <!-- 7. SQL条件设置 -->
            <el-tab-pane label="SQL条件设置" name="conditionSql" v-if="showConditionSqlTab">
                <el-alert type="warning" :closable="false" class="mb-3">
                    注意：请在开发人员指导下进行配置SQL语句
                    <br />支持变量：{processId} 流程发起实例主键, {userId} 用户Id, {userAccount} 用户账号, {companyId} 用户公司, {departmentId}
                    用户部门
                </el-alert>

                <el-form label-width="120px" :model="form" class="node-form" :disabled="isReadonly">
                    <el-form-item label="数据库">
                        <el-input v-model="form.dbConditionId" placeholder="数据库标识" />
                    </el-form-item>

                    <el-form-item label="SQL语句">
                        <el-input v-model="form.conditionSql" type="textarea" :rows="10" placeholder="请填写SQL语句" />
                    </el-form-item>
                </el-form>
            </el-tab-pane>

            <!-- 8. 绑定操作 -->
            <el-tab-pane label="绑定操作" name="operation" v-if="showOperationTab">
                <el-alert type="warning" :closable="false" class="mb-3">
                    注意：请在开发人员指导下进行配置
                </el-alert>

                <el-form label-width="120px" :model="form" class="node-form" :disabled="isReadonly">
                    <el-form-item label="操作类型">
                        <el-radio-group v-model="form.operationType">
                            <el-radio label="sql">SQL</el-radio>
                            <el-radio label="interface">接口</el-radio>
                            <el-radio label="ioc">依赖注入方法</el-radio>
                        </el-radio-group>
                    </el-form-item>

                    <!-- SQL模式 -->
                    <template v-if="form.operationType === 'sql'">
                        <el-form-item label="数据库">
                            <el-input v-model="form.dbId" placeholder="数据库标识" />
                        </el-form-item>

                        <el-form-item label="SQL语句">
                            <el-input v-model="form.strSql" type="textarea" :rows="8" placeholder="请填写SQL语句" />
                        </el-form-item>
                    </template>

                    <!-- 接口模式 -->
                    <template v-if="form.operationType === 'interface'">
                        <el-form-item label="接口地址">
                            <el-input v-model="form.strInterface" type="textarea" :rows="8" placeholder="请填写接口地址" />
                        </el-form-item>
                    </template>

                    <!-- IOC模式 -->
                    <template v-if="form.operationType === 'ioc'">
                        <el-form-item label="方法名">
                            <el-input v-model="form.iocName" type="textarea" :rows="8" placeholder="请填写方法名" />
                        </el-form-item>
                    </template>
                </el-form>
            </el-tab-pane>
        </el-tabs>

        <template #footer>
            <el-button @click="visible = false">关闭</el-button>
            <el-button v-if="!isReadonly" type="primary" @click="save">保存</el-button>
        </template>
    </el-drawer>

    <!-- 审核者选择器 -->
    <AuditorSelector ref="auditorSelectorRef" @confirm="handleAuditorConfirm" />
    <!-- 按钮编辑器 -->
    <ButtonEditor ref="buttonEditorRef" @confirm="handleButtonConfirm" />

    <!-- 表单编辑器 -->
    <WorkformEditor ref="workformEditorRef" @confirm="handleWorkformConfirm" />

    <!-- 条件编辑器 -->
    <ConditionEditor ref="conditionEditorRef" @confirm="handleConditionConfirm" />

    <!-- 人员选择器 -->
    <UserSelector v-model:visible="userSelectorVisible" title="选择人员" multiple @confirm="handleUserSelectConfirm" />
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import AuditorSelector from './AuditorSelector.vue'
import ButtonEditor from './ButtonEditor.vue'
import WorkformEditor from './WorkformEditor.vue'
import ConditionEditor from './ConditionEditor.vue'
import UserSelector from '/@/components/UserSelector/index.vue'

const visible = ref(false)
const userSelectorVisible = ref(false)
const activeTab = ref('baseInfo')
const title = ref('节点属性')
const isReadonly = ref(false)

// 表单数据
const form = reactive<any>({
    id: '',
    name: '',
    type: '',

    // 基本配置
    notice: '',
    isNext: '2',
    isTitle: '2',
    isAllAuditor: '1',
    auditExecutType: '1',
    auditorAgainType: '1',
    auditorType: '1',
    isSign: '2',
    isBatchAudit: '2',
    agreeGz: [],
    noPeopleGz: '1',
    confluenceType: '1',
    confluenceRate: 100,
    childFlow: '',
    childType: '1',

    // 审核者
    auditors: [],

    // 表单
    wfForms: [],

    // 超时
    timeoutNotice: null,
    timeoutInterval: null,
    timeoutStrategy: '',
    timeoutAction: null,

    // 按钮
    btnList: [],

    // 条件
    conditions: [],
    dbConditionId: '',
    conditionSql: '',

    // 操作
    operationType: 'sql',
    dbId: '',
    strSql: '',
    strInterface: '',
    iocName: ''
})

const currentAuditorSelection = ref<any>({})
const auditorSelectorRef = ref()
const buttonEditorRef = ref()
const workformEditorRef = ref()
const conditionEditorRef = ref()
let currentDesigner: any = null

// 计算属性：根据节点类型显示/隐藏不同的内容和选项卡
const isNameReadonly = computed(() => form.type === 'startround' || form.type === 'endround')

// 基本配置显示控制
const showNotice = computed(() => ['startround', 'stepnode', 'auditornode'].includes(form.type))
const showNext = computed(() => form.type === 'startround')
const showAuditor = computed(() => ['stepnode', 'auditornode'].includes(form.type))
const showAuditorType = computed(() => form.type === 'stepnode' && form.isAllAuditor === '2')
const showSign = computed(() => form.type === 'stepnode')
const showBatchAudit = computed(() => ['stepnode', 'auditornode'].includes(form.type))
const showAgreeGz = computed(() => form.type === 'stepnode')
const showNoPeopleGz = computed(() => form.type === 'stepnode')
const showConfluence = computed(() => form.type === 'confluencenode')
const showChild = computed(() => form.type === 'childwfnode')

// 选项卡显示控制
const showAuditorTab = computed(() => !['startround', 'endround', 'conditionnode', 'confluencenode'].includes(form.type))
const showWorkformTab = computed(() => !['confluencenode', 'endround'].includes(form.type))
const showTimeoutTab = computed(() => ['stepnode'].includes(form.type))
const showBtnSettingTab = computed(() => ['stepnode'].includes(form.type))
const showConditionFieldTab = computed(() => ['conditionnode'].includes(form.type))
const showConditionSqlTab = computed(() => ['conditionnode'].includes(form.type))
const showOperationTab = computed(() => ['childwfnode'].includes(form.type))

// 辅助方法
const getAuditorTypeName = (type: string) => {
    const types: Record<string, string> = {
        '1': '岗位',
        '2': '角色',
        '3': '用户',
        '4': '上下级',
        '5': '表字段',
        '6': '某节点执行人',
        '8': 'IOC注入'
    }
    return types[type] || type
}

const getConditionName = (condition: string) => {
    const conditions: Record<string, string> = {
        '1': '同一个部门',
        '2': '同一个公司',
        '3': '发起人上级',
        '4': '发起人下级'
    }
    return conditions[condition] || ''
}

// 打开面板
const open = (nodeData: any, designer: any, readonly: boolean = false) => {
    currentDesigner = designer
    isReadonly.value = readonly
    visible.value = true
    activeTab.value = 'baseInfo'
    title.value = `节点属性 - ${nodeData.name || '未命名'}${readonly ? ' (只读)' : ''}`

    // 加载节点数据
    Object.assign(form, {
        id: nodeData.id,
        name: nodeData.name,
        type: nodeData.type,
        notice: nodeData.notice || '',
        isNext: nodeData.isNext || '2',
        isTitle: nodeData.isTitle || '2',
        isAllAuditor: nodeData.isAllAuditor || '1',
        auditExecutType: nodeData.auditExecutType || '1',
        auditorAgainType: nodeData.auditorAgainType || '1',
        auditorType: nodeData.auditorType || '1',
        isSign: nodeData.isSign || '2',
        isBatchAudit: nodeData.isBatchAudit || '2',
        agreeGz: nodeData.agreeGz ? nodeData.agreeGz.split(',') : [],
        noPeopleGz: nodeData.noPeopleGz || '1',
        confluenceType: nodeData.confluenceType || '1',
        confluenceRate: nodeData.confluenceRate || 100,
        childFlow: nodeData.childFlow || '',
        childType: nodeData.childType || '1',
        auditors: nodeData.auditors || [],
        wfForms: nodeData.wfForms || [],
        timeoutNotice: nodeData.timeoutNotice || null,
        timeoutInterval: nodeData.timeoutInterval || null,
        timeoutStrategy: nodeData.timeoutStrategy || '',
        timeoutAction: nodeData.timeoutAction || null,
        btnList: nodeData.btnList || [],
        conditions: nodeData.conditions || [],
        dbConditionId: nodeData.dbConditionId || '',
        conditionSql: nodeData.conditionSql || '',
        operationType: nodeData.operationType || 'sql',
        dbId: nodeData.dbId || '',
        strSql: nodeData.strSql || '',
        strInterface: nodeData.strInterface || '',
        iocName: nodeData.iocName || ''
    })
}

// 审核者管理
const handleAuditorTypeChange = () => {
    // 切换审核者类型时的逻辑
}

const addAuditor = (type: string) => {
    // 特殊处理人员选择
    if (type === 'user') {
        userSelectorVisible.value = true
        return
    }

    // 打开其他审核者选择器
    if (auditorSelectorRef.value) {
        // 如果是节点执行人，传入当前所有节点
        const nodes = type === 'node' ? getAllNodes() : undefined
        auditorSelectorRef.value.open(type, nodes)
    }
}

const notImplemented = (name: string) => {
    ElMessage.warning(`${name}功能暂未实现`)
}

const removeAuditor = (index: number) => {
    form.auditors.splice(index, 1)
}

const handleAuditorConfirm = (data: any) => {
    // 检查是否重复
    const exists = form.auditors.some((a: any) => a.auditorId === data.auditorId && a.type === data.type)
    if (exists) {
        ElMessage.warning('该审核者已存在')
        return
    }

    // 添加到列表
    form.auditors.push(data)
}

// 人员选择确认
const handleUserSelectConfirm = (users: any[]) => {
    users.forEach(user => {
        const auditor = {
            id: learun.newGuid(),
            type: '3', // 3=用户
            auditorId: user.id,
            auditorName: user.name,
            condition: '' // 无附加条件
        }
        handleAuditorConfirm(auditor)
    })
}

// 获取所有节点（用于节点执行人选择）
// 获取所有节点（用于节点执行人选择）
const getAllNodes = () => {
    try {
        const $ = (window as any).$
        if (!$) return []

        const container = $('#lr_workflow_container')
        if (container.length === 0 || !container[0].dfop) return []

        // 获取所有节点
        const nodes = container[0].dfop.node || []

        // 返回所有节点（可以在这里过滤掉自己，如果需要）
        // 这里返回全部，AuditorSelector中会过滤掉开始和结束节点
        return nodes
    } catch (error) {
        console.error('获取节点列表失败:', error)
        return []
    }
}

// 表单管理
const addWorkform = () => {
    if (workformEditorRef.value) {
        workformEditorRef.value.open('add')
    }
}

const editWorkform = (index: number) => {
    if (workformEditorRef.value) {
        workformEditorRef.value.open('edit', form.wfForms[index], index)
    }
}

const removeWorkform = (index: number) => {
    form.wfForms.splice(index, 1)
}

const handleWorkformConfirm = (data: any, index?: number) => {
    if (index !== undefined && index >= 0) {
        // 编辑模式
        form.wfForms[index] = data
    } else {
        // 新增模式
        form.wfForms.push(data)
    }
}

// 按钮管理
const addButton = () => {
    if (buttonEditorRef.value) {
        buttonEditorRef.value.open('add')
    }
}

const editButton = (index: number) => {
    if (buttonEditorRef.value) {
        buttonEditorRef.value.open('edit', form.btnList[index], index)
    }
}

const removeButton = (index: number) => {
    form.btnList.splice(index, 1)
}

const handleButtonConfirm = (data: any, index?: number) => {
    if (index !== undefined && index >= 0) {
        // 编辑模式
        form.btnList[index] = data
    } else {
        // 新增模式
        // 检查代码是否重复
        const exists = form.btnList.some((btn: any) => btn.code === data.code)
        if (exists) {
            ElMessage.warning('按钮代码已存在')
            return
        }
        form.btnList.push(data)
    }
}

// 条件管理
const addCondition = () => {
    if (conditionEditorRef.value) {
        const isFirst = form.conditions.length === 0
        conditionEditorRef.value.open('add', undefined, undefined, isFirst)
    }
}

const editCondition = (index: number) => {
    if (conditionEditorRef.value) {
        const isFirst = index === 0
        conditionEditorRef.value.open('edit', form.conditions[index], index, isFirst)
    }
}

const removeCondition = (index: number) => {
    form.conditions.splice(index, 1)
}

const handleConditionConfirm = (data: any, index?: number) => {
    if (index !== undefined && index >= 0) {
        // 编辑模式
        form.conditions[index] = data
    } else {
        // 新增模式
        form.conditions.push(data)
    }
}

// 保存
const save = () => {
    // 构造节点数据
    const nodeData = {
        id: form.id,
        name: form.name,
        type: form.type,

        // 基本配置
        notice: form.notice,
        isNext: form.isNext,
        isTitle: form.isTitle,
        isAllAuditor: form.isAllAuditor,
        auditExecutType: form.auditExecutType,
        auditorAgainType: form.auditorAgainType,
        auditorType: form.auditorType,
        isSign: form.isSign,
        isBatchAudit: form.isBatchAudit,
        agreeGz: Array.isArray(form.agreeGz) ? form.agreeGz.join(',') : form.agreeGz,
        noPeopleGz: form.noPeopleGz,
        confluenceType: form.confluenceType,
        confluenceRate: form.confluenceRate,
        childFlow: form.childFlow,
        childType: form.childType,

        // 审核者
        auditors: form.auditors,

        // 表单
        wfForms: form.wfForms,

        // 超时
        timeoutNotice: form.timeoutNotice,
        timeoutInterval: form.timeoutInterval,
        timeoutStrategy: form.timeoutStrategy,
        timeoutAction: form.timeoutAction,

        // 按钮
        btnList: form.btnList,

        // 条件
        conditions: form.conditions,
        dbConditionId: form.dbConditionId,
        conditionSql: form.conditionSql,

        // 操作
        operationType: form.operationType,
        dbId: form.dbId,
        strSql: form.strSql,
        strInterface: form.strInterface,
        iocName: form.iocName
    }

    // 1. 先更新数据 (修改原内存对象)
    updateNodeInDesigner(nodeData)

    // 2. 再更新视觉显示
    if (currentDesigner && currentDesigner.updateNodeText) {
        currentDesigner.updateNodeText(form.id, form.name)
    }

    ElMessage.success('保存成功')
    visible.value = false
}

// 更新设计器中的节点数据
const updateNodeInDesigner = (nodeData: any) => {
    try {
        const $ = (window as any).$
        if (!$) return

        const container = $('#lr_workflow_container')
        if (container.length === 0 || !container[0].dfop) return

        // 获取所有节点
        const nodes = container[0].dfop.node || []

        // 查找并原地修改对象，保持引用一致
        const node = nodes.find((n: any) => n.id === nodeData.id)
        if (node) {
            Object.assign(node, nodeData)
            console.log('节点数据已更新:', node)
        }
    } catch (error) {
        console.error('更新节点数据失败:', error)
    }
}

const handleClose = () => {
    visible.value = false
}

defineExpose({
    open
})
</script>

<style scoped lang="scss">
.node-config-tabs {
    height: calc(100vh - 140px);

    :deep(.el-tabs__content) {
        height: calc(100% - 55px);
        overflow-y: auto;
    }

    :deep(.el-tab-pane) {
        height: 100%;
    }

    :deep(.el-tabs__nav) {
        padding-left: 20px;
    }
}

.node-form {
    padding: 20px;
}

.tab-pane-content {
    padding: 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.btn-group {
    padding: 15px 0;
    border-top: 1px solid #eee;

    .el-button {
        margin-right: 10px;
        margin-bottom: 10px;
    }
}

.mt-3 {
    margin-top: 15px;
}

.mb-3 {
    margin-bottom: 15px;
}

.category-label {
    font-size: 14px;
    font-weight: bold;
    color: #606266;
    margin-bottom: 10px;
    padding-left: 5px;
    border-left: 4px solid #409EFF;
    line-height: 1.2;
}

.mt-2 {
    margin-top: 10px;
}
</style>
