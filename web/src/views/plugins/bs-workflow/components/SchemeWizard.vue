<template>
    <div class="scheme-wizard">
        <!-- 步骤条 - 简洁横向布局 -->
        <div class="wizard-steps">
            <el-steps :active="activeStep" finish-status="success" style="max-width: 600px" :space="10" simple>
                <el-step title="基本配置" />
                <el-step title="权限设置" />
                <el-step title="模板设计" />
            </el-steps>
        </div>

        <!-- 步骤内容区（可滚动） -->
        <div class="wizard-content">
            <!-- 步骤1: 基本配置 -->
            <div v-show="activeStep === 0" class="step-pane">
                <el-card shadow="never">
                    <template #header>
                        <h3 class="card-title">模板基本信息配置</h3>
                    </template>

                    <el-form ref="basicFormRef" :model="formData" :rules="basicRules" label-width="140px">
                        <el-row :gutter="20">
                            <el-col :span="12">
                                <el-form-item label="模板编号" prop="scheme_code">
                                    <el-input v-model="formData.scheme_code" :disabled="dialogStatus === 'update'"
                                            placeholder="请输入编号" />
                                </el-form-item>
                            </el-col>

                            <el-col :span="12">
                                <el-form-item label="模板名称" prop="scheme_name">
                                    <el-input v-model="formData.scheme_name" placeholder="请输入名称" />
                                </el-form-item>
                            </el-col>

                            <el-col :span="12">
                                <el-form-item label="模板分类" prop="category">
                                    <el-select v-model="formData.category" placeholder="请选择分类" style="width: 100%;">
                                        <el-option label="默认分类" value="default" />
                                        <!-- TODO: 从数据字典加载分类 -->
                                    </el-select>
                                </el-form-item>
                            </el-col>

                            <el-col :span="12">
                                <el-form-item label="我的任务" prop="mark">
                                    <el-radio-group v-model="formData.mark">
                                        <el-radio :label="1">允许发起</el-radio>
                                        <el-radio :label="2">不允许发起</el-radio>
                                    </el-radio-group>
                                </el-form-item>
                            </el-col>

                            <el-col :span="12">
                                <el-form-item label="移动端" prop="is_in_app">
                                    <el-radio-group v-model="formData.is_in_app">
                                        <el-radio :label="1">显示</el-radio>
                                        <el-radio :label="2">不显示</el-radio>
                                    </el-radio-group>
                                </el-form-item>
                            </el-col>

                            <el-col :span="12">
                                <el-form-item label="撤销作废执行" prop="close_do_type">
                                    <el-radio-group v-model="formData.close_do_type" @change="handleCloseDoTypeChange">
                                        <el-radio label="sql">SQL</el-radio>
                                        <el-radio label="ioc">依赖注入方法</el-radio>
                                        <el-radio label="interface">接口</el-radio>
                                    </el-radio-group>
                                </el-form-item>
                            </el-col>

                            <!-- 动态配置区 -->
                            <el-col :span="24" v-if="formData.close_do_type === 'sql'">
                                <el-alert
                                        title="注意:请配置SQL语句({processId}流程进程主键{userId}用户Id{userAccount}用户账号{companyId}用户公司{departmentId}用户部门{code}1撤销2作废3删除草稿)"
                                        type="warning" :closable="false" style="margin-bottom: 15px;" />
                                <el-form-item label="数据库">
                                    <el-select v-model="formData.close_do_db_id" placeholder="请选择数据库"
                                            style="width: 100%;">
                                        <el-option label="默认数据库" value="default" />
                                    </el-select>
                                </el-form-item>
                                <el-form-item label="SQL语句">
                                    <el-input v-model="formData.close_do_sql" type="textarea" :rows="4"
                                            placeholder="请填写SQL语句" />
                                </el-form-item>
                            </el-col>

                            <el-col :span="24" v-if="formData.close_do_type === 'ioc'">
                                <el-alert title="注意:必须要开发人员指导下进行配置注册的IOC方法名,需要继承接口IWorkFlowMethod" type="warning"
                                        :closable="false" style="margin-bottom: 15px;" />
                                <el-form-item label="方法名">
                                    <el-input v-model="formData.close_do_ioc_name" type="textarea" :rows="4"
                                            placeholder="请填写方法名" resize="none" />
                                </el-form-item>
                            </el-col>

                            <el-col :span="24" v-if="formData.close_do_type === 'interface'">
                                <el-alert title="注意:必须要开发人员指导下进行配置支持Post方法的接口,json数据格式" type="warning" :closable="false"
                                        style="margin-bottom: 15px;" />
                                <el-form-item label="接口地址">
                                    <el-input v-model="formData.close_do_interface" type="textarea" :rows="4"
                                            placeholder="请填写接口地址" />
                                </el-form-item>
                            </el-col>

                            <el-col :span="24">
                                <el-form-item label="备注">
                                    <el-input v-model="formData.description" type="textarea" :rows="4"
                                            placeholder="请输入备注" resize="none" />
                                </el-form-item>
                            </el-col>
                        </el-row>
                    </el-form>
                </el-card>
            </div>

            <!-- 步骤2: 权限设置 -->
            <div v-show="activeStep === 1" class="step-pane">
                <el-card shadow="never">
                    <template #header>
                        <div class="card-header">
                            <h3 class="card-title">权限配置</h3>
                            <el-radio-group v-model="authorizeType" @change="handleAuthorizeTypeChange">
                                <el-radio :value="1">所有成员</el-radio>
                                <el-radio :value="2" disabled>指定成员</el-radio>
                            </el-radio-group>
                        </div>
                    </template>

                    <div class="authorize-container">
                        <div class="authorize-toolbar">
                            <el-button type="success" icon="UserFilled" :disabled="authorizeType === 1"
                                    @click="handleAddPost">
                                添加岗位
                            </el-button>
                            <el-button type="info" icon="Star" :disabled="authorizeType === 1" @click="handleAddRole">
                                添加角色
                            </el-button>
                            <el-button type="primary" icon="User" :disabled="authorizeType === 1"
                                    @click="handleAddUser">
                                添加人员
                            </el-button>
                            <el-button type="danger" icon="Delete" :disabled="authorizeType === 1"
                                    @click="handleRemoveAuthorize">
                                移除
                            </el-button>
                        </div>

                        <el-table ref="authorizeTable" :data="schemeAuthorizes" border style="width: 100%;"
                                :row-class-name="authorizeType === 1 ? 'disabled-row' : ''" highlight-current-row
                                @current-change="handleAuthorizeCurrentChange">
                            <el-table-column label="类型" align="center" width="120">
                                <template #default="{ row }">
                                    <el-tag v-if="row.obj_type === 1" type="success">岗位</el-tag>
                                    <el-tag v-else-if="row.obj_type === 2" type="info">角色</el-tag>
                                    <el-tag v-else-if="row.obj_type === 3" type="primary">用户</el-tag>
                                    <el-tag v-else-if="row.obj_type === 4" type="warning">所有成员</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="名称" prop="obj_name" align="left" />
                        </el-table>

                        <div v-if="authorizeType === 1" class="authorize-mask" />
                    </div>
                </el-card>
            </div>

            <!-- 步骤3: 模板设计 -->
            <div v-show="activeStep === 2" class="step-pane">
                <el-card shadow="never" :body-style="{ padding: '0px', height: '100%' }">
                    <div style="height: 600px;">
                        <Designer v-if="activeStep === 2" ref="designerRef" :init-content="designerContent" />
                    </div>
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, Check, Document } from '@element-plus/icons-vue'
import { AddObj, UpdateObj, GetObj, SaveSchemeData } from '../api/scheme'
import Designer from './Designer/index.vue'

interface Props {
    dialogStatus: 'create' | 'update'
    schemeData?: any
    categoryId?: string
}

const props = defineProps<Props>()
const emit = defineEmits(['close', 'refresh'])

const activeStep = ref(0) // el-steps 的 active 从 0 开始
const basicFormRef = ref<any>(null)
const authorizeTable = ref<any>(null)
const designerRef = ref<any>(null)
const authorizeType = ref(1) // 1=所有成员, 2=指定成员
const currentAuthorize = ref<any>(null)

// 表单数据
const formData = reactive({
    id: undefined,
    scheme_code: '',
    scheme_name: '',
    category: 'default',
    mark: 1,
    is_in_app: 2,
    close_do_type: 'ioc',
    close_do_db_id: '',
    close_do_sql: '',
    close_do_ioc_name: '',
    close_do_interface: '',
    description: '',
    type: 1,
    content: null
})

// 设计器内容
const designerContent = ref<any>(null)

// 权限人员列表
const schemeAuthorizes = ref<any[]>([])

// 基本信息验证规则
const basicRules = {
    scheme_code: [
        { required: true, message: '请输入模板编号', trigger: 'blur' },
        { pattern: /^[a-zA-Z0-9_]+$/, message: '只能包含字母、数字和下划线', trigger: 'blur' }
    ],
    scheme_name: [
        { required: true, message: '请输入模板名称', trigger: 'blur' }
    ],
    category: [
        { required: true, message: '请选择模板分类', trigger: 'change' }
    ]
}

// 撤销作废类型切换
const handleCloseDoTypeChange = () => {
    formData.close_do_sql = ''
    formData.close_do_ioc_name = ''
    formData.close_do_interface = ''
}

// 权限类型切换
const handleAuthorizeTypeChange = () => {
    if (authorizeType.value === 1) {
        schemeAuthorizes.value = []
    }
}

// 权限表格当前行切换
const handleAuthorizeCurrentChange = (row: any) => {
    currentAuthorize.value = row
}

// 添加岗位
const handleAddPost = () => {
    ElMessage.info('添加岗位功能待实现')
}

// 添加角色
const handleAddRole = () => {
    ElMessage.info('添加角色功能待实现')
}

// 添加人员
const handleAddUser = () => {
    ElMessage.info('添加人员功能待实现')
}

// 移除权限
const handleRemoveAuthorize = () => {
    if (!currentAuthorize.value) {
        ElMessage.warning('请先选择要移除的记录')
        return
    }

    const index = schemeAuthorizes.value.findIndex(
        item => item.id === currentAuthorize.value.id
    )
    if (index > -1) {
        schemeAuthorizes.value.splice(index, 1)
        ElMessage.success('移除成功')
    }
}

// 上一步
const handlePrev = () => {
    if (activeStep.value > 0) {
        activeStep.value--
    }
}

// 下一步
const handleNext = () => {
    if (activeStep.value === 0) {
        basicFormRef.value?.validate((valid: boolean) => {
            if (valid) {
                activeStep.value++
            }
        })
    } else if (activeStep.value === 1) {
        if (authorizeType.value === 2 && schemeAuthorizes.value.length === 0) {
            ElMessage.error('请添加权限人员信息')
            return
        }
        activeStep.value++
    }
}

// 保存草稿
const handleDraftSave = () => {
    saveData(2)
}

// 完成保存
const handleFinish = () => {
    basicFormRef.value?.validate((valid: boolean) => {
        if (valid) {
            saveData(1)
        }
    })
}

// 保存数据
const saveData = (type: number) => {
    // 获取流程图数据
    let flowData = null
    if (designerRef.value) {
        flowData = designerRef.value.getData()
    } else if (designerContent.value) {
        flowData = designerContent.value
    }

    // 打印流程图数据
    console.log('====== 流程图数据 ======')
    console.log('原始流程图对象:', flowData)

    // 构造 schemeInfo 对象（基本信息）
    const schemeInfo: any = {
        scheme_id: formData.id || undefined,
        code: formData.scheme_code,
        name: formData.scheme_name,
        category: formData.category,
        mark: String(formData.mark),
        is_in_app: String(formData.is_in_app),
        close_do_type: formData.close_do_type,
        close_do_db_id: formData.close_do_db_id || '&nbsp;',
        close_do_sql: formData.close_do_sql || '',
        close_do_ioc_name: formData.close_do_ioc_name || '',
        close_do_interface: formData.close_do_interface || '',
        description: formData.description || '&nbsp;'
    }

    // 构造 scheme 对象（流程图数据 + closeDo）
    const scheme: any = {
        nodes: flowData?.nodes || flowData?.node || [],
        lines: flowData?.lines || flowData?.line || [],
        closeDo: {
            close_do_type: formData.close_do_type,
            close_do_db_id: formData.close_do_db_id || '&nbsp;',
            close_do_sql: formData.close_do_sql || '',
            close_do_ioc_name: formData.close_do_ioc_name || '',
            close_do_interface: formData.close_do_interface || ''
        }
    }

    // 构造 shcemeAuth 数组（权限人员）
    let shcemeAuth: any[] = []
    if (authorizeType.value === 1) {
        shcemeAuth = [{
            id: undefined,
            obj_type: 4
        }]
    } else {
        shcemeAuth = schemeAuthorizes.value.map(item => ({
            id: item.id,
            obj_name: item.obj_name,
            obj_id: item.obj_id,
            obj_type: item.obj_type
        }))
    }

    // 构造完整的请求数据（完全按照原始结构）
    const postData = {
        schemeInfo: JSON.stringify(schemeInfo),
        scheme: JSON.stringify(scheme),
        shcemeAuth: JSON.stringify(shcemeAuth),
        type: type
    }

    // 打印完整的请求数据
    console.log('====== 完整的请求数据对象（原始结构） ======')
    console.log('保存类型:', type === 1 ? '正式保存' : '保存草稿')
    console.log('schemeInfo:', schemeInfo)
    console.log('scheme:', scheme)
    console.log('shcemeAuth:', shcemeAuth)
    console.log('type:', type)
    console.log('------')
    console.log('最终发送数据（JSON字符串格式）:', postData)
    console.log('================================')

    // 使用新的保存接口
    SaveSchemeData(postData).then(() => {
        ElMessage.success(type === 2 ? '保存草稿成功' : '保存成功')
        emit('refresh')
        emit('close')
    }).catch(() => {
        // service层已有报错提示
    })
}

// 初始化数据
const initData = () => {
    if (props.dialogStatus === 'update' && props.schemeData) {
        // 新的数据格式: { info, scheme, authList }
        // 使用小写字段名，无 F_ 前缀
        const { info, scheme, authList } = props.schemeData

        if (info) {
            // 将 info 的数据赋值给 formData
            Object.assign(formData, {
                id: info.id,
                scheme_code: info.code,
                scheme_name: info.name,
                category: info.category,
                mark: info.mark,
                is_in_app: info.is_in_app,
                description: info.description
            })
        }

        if (scheme && scheme.content) {
            // content 是JSON字符串，需要解析
            try {
                designerContent.value = JSON.parse(scheme.content)
            } catch (e) {
                console.error('解析流程内容失败', e)
                designerContent.value = { nodes: [], lines: [] }
            }
        }

        if (authList && authList.length > 0) {
            // 加载权限数据
            const firstAuth = authList[0]
            if (firstAuth.obj_type === 4) {
                // 所有人
                authorizeType.value = 1
            } else {
                // 指定成员
                authorizeType.value = 2
                schemeAuthorizes.value = authList.map((item: any) => ({
                    id: item.id,
                    obj_type: item.obj_type,
                    obj_id: item.obj_id,
                    obj_name: item.obj_name
                }))
            }
        }
    } else if (props.categoryId) {
        formData.category = props.categoryId
    }
}

watch(() => props.schemeData, () => {
    initData()
}, { immediate: true })

onMounted(() => {
    initData()
})

// 暴露方法给父组件调用
defineExpose({
    activeStep,
    handlePrev,
    handleNext,
    handleDraftSave,
    handleFinish
})
</script>

<style scoped lang="scss">
.scheme-wizard {
    display: flex;
    flex-direction: column;
    height: 100%;
    height: 100%;
    // min-height: 600px; // 移除固定最小高度，完全跟随父容器

    .wizard-steps {
        height: 40px; // 稍微增加高度
        // border-bottom: 1px solid #e4e7ed; // 可选：添加底部分割线
        background: #fff; // 确保背景色
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center; // 水平居中

        :deep(.el-steps) {
            &.el-steps--simple {
                background: transparent;
                padding: 10px 20px;
                border-radius: 4px; // 圆角
                width: 100%; // 占满容器以便居中生效（配合 max-width）

                // 如果需要更明显的卡片感，可以给 steps 本身加背景
                // background: #f5f7fa; 

                .el-step {

                    .el-step__title {
                        font-size: 15px; // 稍微调大字体
                        font-weight: 500;
                    }
                }

                .el-step__icon {
                    height: 24px;
                    width: 24px;
                }
            }
        }
    }

    .wizard-content {
        height: 1660px;
        // height: 0; // 关键：配合 flex: 1 使用，防止内容撑开容器
        overflow: hidden; // 自身不滚动，让 flex 处理
        display: flex;
        flex-direction: column;
        padding: 20px;
        background: #f5f7fa;

        .step-pane {
            flex: 1; // 让 pane 填满剩余空间
            overflow-y: auto; // 内容在这里滚动
            height: 100%; // 确保占满高度

            // 移除 min-height: 500px，完全由外部容器决定高度
            // 如果想要内容少时也有一定高度感，可以使用 flex 自动填充
            animation: fadeIn 0.3s ease-in-out;
        }

        :deep(.el-card) {
            border-radius: 8px;
            margin-bottom: 0;

            .card-title {
                margin: 0;
                font-size: 16px;
                font-weight: 600;
                color: #303133;
            }

            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
        }

        .authorize-container {
            position: relative;

            .authorize-toolbar {
                margin-bottom: 16px;
                display: flex;
                gap: 10px;
            }

            .authorize-mask {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.7);
                z-index: 10;
                pointer-events: none;
                border-radius: 4px;
            }

            :deep(.disabled-row) {
                opacity: 0.6;
            }
        }
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
