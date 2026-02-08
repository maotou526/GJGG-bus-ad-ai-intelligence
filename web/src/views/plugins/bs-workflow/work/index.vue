<template>
    <fs-page class="workflow-work-page">
        <div class="lr-layout-panel">
            <!-- 左侧：Tabs（表单信息/流程信息/流转记录） -->
            <div class="lr-layout-left">
                <!-- 工具栏 -->
                <div class="lr-toolbar">
                    <el-button v-if="showPrintBtn" size="small" @click="handlePrint">打印表单</el-button>
                    <el-button v-if="parentProcessId" size="small" @click="handleViewParent">查看父流程</el-button>
                </div>

                <!-- Tabs -->
                <el-tabs v-model="activeTab" class="lr-tabs">
                    <el-tab-pane label="表单信息" name="forminfo">
                        <div class="tab-content form-content">
                            <component v-if="formComponent" :is="formComponent" ref="formRef" :readonly="isReadOnly"
                                    :data="formData" :nodeId="currentNodeId" :formParams="formParams" />
                            <el-empty v-else description="未找到关联的表单组件" />
                        </div>
                    </el-tab-pane>

                    <el-tab-pane label="流程信息" name="workflowshcemeinfo">
                        <div class="tab-content flow-content">
                            <!-- 流程图区域（使用力软 lrworkflow 组件） -->
                            <div class="flow-diagram-area">
                                <WorkflowDesigner v-if="flowSchemeData" ref="workflowDesignerRef"
                                        :initContent="flowSchemeData" :readOnly="true"
                                        @node-double-click="handleNodeDoubleClick" />
                                <el-empty v-else description="暂无流程图数据" />
                            </div>
                            <!-- 图例（与力软一致：0=正在处理, 1=已处理同意, 2=已处理不同意, 3=未处理） -->
                            <div class="flow-legend">
                                <div class="legend-item">
                                    <span class="legend-color current"></span>
                                    <span>正在处理</span>
                                </div>
                                <div class="legend-item">
                                    <span class="legend-color done"></span>
                                    <span>已处理</span>
                                </div>
                                <div class="legend-item">
                                    <span class="legend-color pending"></span>
                                    <span>未处理</span>
                                </div>
                            </div>
                        </div>
                    </el-tab-pane>

                    <el-tab-pane label="流转记录" name="auditinfo">
                        <div class="tab-content audit-content">
                            <div v-if="timelineItems.length > 0" class="lr-timeline">
                                <div v-for="(item, index) in timelineItems" :key="index" class="timeline-item"
                                        :class="{ 'is-current': item.type === 'current' }">
                                    <div class="timeline-dot" :class="getTimelineDotClass(item)"></div>
                                    <div class="timeline-content">
                                        <div class="timeline-header">
                                            <span class="timeline-title">{{ item.title }}</span>
                                            <span class="timeline-time">{{ item.time }}</span>
                                        </div>
                                        <div class="timeline-body">
                                            <div class="timeline-user">{{ item.userName }}</div>
                                            <div v-if="item.content" class="timeline-desc" v-html="item.content"></div>
                                        </div>
                                        <!-- 签章图片（如果有） -->
                                        <div v-if="item.signImg || item.stampImg" class="timeline-sign">
                                            <img v-if="item.stampImg" :src="getStampUrl(item.stampImg)" alt="印章"
                                                    class="stamp-img" />
                                            <img v-if="item.signImg" :src="getSignUrl(item.signImg)" alt="签名"
                                                    class="sign-img" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <el-empty v-else description="暂无流转记录" />
                        </div>
                    </el-tab-pane>
                </el-tabs>
            </div>

            <!-- 右侧：审批信息 -->
            <div class="lr-layout-right">
                <div class="right-header">审批信息</div>
                <div class="right-body">
                    <div v-if="loading" class="loading-box">
                        <el-icon class="is-loading">
                            <Loading />
                        </el-icon>
                        <span>加载中...</span>
                    </div>

                    <template v-else>
                        <!-- 创建/草稿模式：显示标题和等级 -->
                        <template v-if="mode === 'create' || mode === 'draftCreate'">
                            <el-form label-position="top" class="audit-form">
                                <el-form-item label="流程标题">
                                    <el-input v-model="processForm.title" placeholder="请输入流程标题" />
                                </el-form-item>
                                <el-form-item label="重要等级">
                                    <el-radio-group v-model="processForm.level">
                                        <el-radio :value="0">普通</el-radio>
                                        <el-radio :value="1">重要</el-radio>
                                        <el-radio :value="2">紧急</el-radio>
                                    </el-radio-group>
                                </el-form-item>
                            </el-form>
                            <div class="action-buttons">
                                <el-button type="success" @click="handleCreate" :loading="submitting">创建流程</el-button>
                                <el-button type="default" @click="handleSaveDraft"
                                        :loading="submitting">保存草稿</el-button>
                            </div>
                        </template>

                        <!-- 审批模式 -->
                        <template v-else-if="mode === 'audit' || mode === 'signAudit'">
                            <el-form label-position="top" class="audit-form">
                                <el-form-item label="审批意见">
                                    <el-input type="textarea" v-model="auditForm.des" :rows="5" placeholder="请输入审批意见" />
                                </el-form-item>
                            </el-form>

                            <div v-if="!isFinished" class="action-buttons">
                                <!-- 动态渲染节点配置的按钮 -->
                                <template v-for="btn in auditButtons" :key="btn.id">
                                    <el-button
                                        v-if="btn.isHide !== '1'"
                                        :type="getButtonType(btn.code)"
                                        :loading="submitting"
                                        @click="handleButtonClick(btn)"
                                    >
                                        {{ btn.name }}
                                    </el-button>
                                </template>
                                <!-- 加签按钮（特殊处理） -->
                                <el-button v-if="showSignBtn" type="info" @click="handleSign" :loading="submitting">
                                    加签
                                </el-button>
                            </div>
                            <el-alert v-else title="流程已结束" type="success" :closable="false" show-icon />
                        </template>

                        <!-- 传阅模式 -->
                        <template v-else-if="mode === 'refer'">
                            <el-form label-position="top" class="audit-form">
                                <el-form-item label="传阅意见">
                                    <el-input type="textarea" v-model="auditForm.des" :rows="3" placeholder="已阅" />
                                </el-form-item>
                            </el-form>
                            <div class="action-buttons">
                                <el-button type="primary" @click="handleRefer" :loading="submitting">确认阅读</el-button>
                            </div>
                        </template>

                        <!-- 重新创建模式 -->
                        <template v-else-if="mode === 'againCreate'">
                            <el-form label-position="top" class="audit-form">
                                <el-form-item label="流程标题">
                                    <el-input v-model="processForm.title" placeholder="请输入流程标题" />
                                </el-form-item>
                            </el-form>
                            <div class="action-buttons">
                                <el-button type="primary" @click="handleAgainCreate"
                                        :loading="submitting">重新创建</el-button>
                            </div>
                        </template>

                        <!-- 查看模式 -->
                        <template v-else-if="mode === 'look' || mode === 'childlook' || mode === 'lookParent'">
                            <!-- 流程基本信息摘要（紧凑两列布局） -->
                            <div class="process-summary-compact">
                                <div class="summary-header">
                                    <span class="summary-title">{{ processInfo.title || processInfo.schemeName || '流程详情' }}</span>
                                    <el-tag :type="processInfo.isFinished === 1 ? 'success' : 'primary'" size="small">
                                        {{ processInfo.isFinished === 1 ? '已结束' : '运行中' }}
                                    </el-tag>
                                </div>
                                <div class="summary-grid">
                                    <span class="summary-item"><i class="label">发起人</i>{{ processInfo.creatorName || '-' }}</span>
                                    <span class="summary-item"><i class="label">发起时间</i>{{ processInfo.createTime || '-' }}</span>
                                    <span class="summary-item"><i class="label">当前节点</i>{{ currentNodeName || '-' }}</span>
                                </div>
                            </div>

                            <!-- 审批记录卡片（仿力软 tab-flow-audit 样式） -->
                            <div v-if="auditInfoCards.length > 0" class="tab-flow-audit">
                                <div v-for="(card, index) in auditInfoCards" :key="index" class="auditinfo">
                                    <div class="auditinfo-h">{{ card.nodeName }}</div>
                                    <div class="auditinfo-b">
                                        <!-- 印章图片 -->
                                        <div v-if="card.stampImg" class="auditinfo-s">
                                            <img :src="getStampUrl(card.stampImg)" alt="印章" />
                                        </div>
                                        <!-- 签名图片 -->
                                        <div v-if="card.signImg" class="auditinfo-sg">
                                            <img :src="getSignUrl(card.signImg)" alt="签名" />
                                        </div>
                                        <!-- 审批内容 -->
                                        <p class="auditinfo-content" v-html="card.content"></p>
                                        <!-- 签字人 -->
                                        <div class="auditinfo-n">
                                            <span>签&nbsp;&nbsp;&nbsp;&nbsp;字：</span>
                                            <span>{{ card.userName }}</span>
                                        </div>
                                        <!-- 日期 -->
                                        <div class="auditinfo-d">
                                            <span>日&nbsp;&nbsp;&nbsp;&nbsp;期：</span>
                                            <span>{{ card.date }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <el-empty v-else-if="taskLogs.length === 0" description="暂无审批记录" :image-size="60" />
                        </template>

                        <!-- 审批历史摘要（非查看模式显示） -->
                        <div v-if="mode !== 'look' && mode !== 'childlook' && taskLogs.length > 0"
                                class="audit-history-summary">
                            <el-divider content-position="left">审批记录</el-divider>
                            <div v-for="(log, index) in taskLogs.slice(0, 3)" :key="index" class="history-item">
                                <div class="history-header">
                                    <span class="history-node">{{ log.F_NodeName }}</span>
                                    <el-tag :type="getLogTagType(log)" size="small">{{ log.F_OperationName }}</el-tag>
                                </div>
                                <div class="history-footer">
                                    <span>{{ log.F_TaskUserName }}</span>
                                    <span>{{ log.F_CreateDate }}</span>
                                </div>
                            </div>
                            <div v-if="taskLogs.length > 3" class="history-more">
                                <el-link type="primary" @click="activeTab = 'auditinfo'">查看更多...</el-link>
                            </div>
                        </div>

                        <!-- 返回按钮 -->
                        <div class="back-btn">
                            <el-button type="default" @click="handleBack">返回列表</el-button>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </fs-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, shallowRef, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Loading } from '@element-plus/icons-vue';
import { getFormInfo } from './FormRegistry';
import { GetProcessDetails, AuditFlow, ReferFlow } from '../api/process';
import WorkflowDesigner from '../components/Designer/index.vue';

const route = useRoute();
const router = useRouter();

// 状态
const loading = ref(false);
const submitting = ref(false);
const activeTab = ref('forminfo');
const isFinished = ref(false);
const currentNodeName = ref('');
const currentNodeId = ref('');
const parentProcessId = ref('');
const showPrintBtn = ref(true);
const showSignBtn = ref(false);

// 路由参数
const processId = ref(route.query.processId as string || '');
const taskId = ref(route.query.taskId as string || '');
const mode = ref(route.query.type as string || 'look');
const schemeCode = ref(route.query.shcemeCode as string || route.query.schemeCode as string || '');

// 表单相关
const formRef = ref();
const formComponent = shallowRef<any>(null);
const formData = ref({});
const formParams = ref<Record<string, string>>({});
const isReadOnly = computed(() => ['look', 'childlook', 'lookParent'].includes(mode.value));

// 流程信息
const processInfo = ref({
    schemeName: '',
    schemeCode: '',
    title: '',
    creatorName: '',
    createTime: '',
    isFinished: 0
});

// 流程模板内容
const schemeContent = ref<any>(null);
const currentNodeConfig = ref<any>(null);

// 流转记录（原始数据）
const taskLogs = ref<any[]>([]);

// 当前待办任务列表
const currentTasks = ref<any[]>([]);

// 流程图节点（旧版，保留用于兼容）
const flowNodes = ref<any[]>([]);

// 节点映射（用于获取节点名称）
const nodeMap = ref<Record<string, any>>({});

// 流程图设计器数据（用于 lrworkflow 渲染）
const flowSchemeData = ref<any>(null);
const workflowDesignerRef = ref();

// 创建表单
const processForm = ref({
    title: '',
    level: 0
});

// 审批表单
const auditForm = ref({
    des: ''
});

// 流转记录时间线（合并当前待办 + 历史记录）
// 按照力软的格式：当前待办在前，历史记录在后
const timelineItems = computed(() => {
    const items: any[] = [];

    // 1. 当前待办任务（显示在最前面）
    currentTasks.value.forEach((task: any) => {
        const userNames = (task.nWFUserInfoList || [])
            .filter((u: any) => u.Mark === 0)
            .map((u: any) => u.Name || u.Id)
            .join(', ');

        items.push({
            type: 'current',
            title: (task.F_NodeName || task.nodeName || '') + '【正在处理节点】',
            userName: userNames || '待分配',
            content: '需要其审核',
            time: '当前',
            nodeId: task.F_NodeId || task.nodeId
        });
    });

    // 2. 历史审核记录
    taskLogs.value.forEach((log: any) => {
        let content = log.F_OperationName || '';
        if (log.F_Des) {
            content += `<br/>【审批意见】：${log.F_Des}`;
        }

        // 获取节点名称
        let nodeName = log.F_NodeName || '';
        if (!nodeName && log.F_NodeId && nodeMap.value[log.F_NodeId]) {
            nodeName = nodeMap.value[log.F_NodeId].name || '';
        }

        items.push({
            type: 'history',
            title: nodeName,
            userName: log.F_TaskUserName || log.F_CreateUserName || '',
            content: content,
            time: log.F_CreateDate || '',
            nodeId: log.F_NodeId,
            operationCode: log.F_OperationCode,
            signImg: log.F_SignImg,
            stampImg: log.F_StampImg
        });
    });

    return items;
});

// 审批信息卡片（用于查看模式右侧面板，仿力软 tab-flow-audit）
// 按节点+用户去重，只显示已处理的审批记录
const auditInfoCards = computed(() => {
    const cards: any[] = [];
    const seen = new Set<string>();

    // 倒序遍历（最新的在前面）
    const logs = [...taskLogs.value].reverse();

    logs.forEach((log: any) => {
        // 跳过创建类型的日志（F_TaskType: 0=创建, 4=子流程, 5=传阅发起, 6=加签发起）
        if (['0', '4', '5', '6'].includes(String(log.F_TaskType))) {
            return;
        }

        // 按节点+用户去重
        const key = `${log.F_NodeId}_${log.F_CreateUserId}`;
        if (seen.has(key)) return;
        seen.add(key);

        // 构建审批内容
        let content = log.F_OperationName || '';
        if (log.F_Des) {
            content += `<br/>【审批意见】：${log.F_Des}`;
        }

        cards.push({
            nodeName: log.F_NodeName || '',
            content: content,
            userName: log.F_TaskUserName || log.F_CreateUserName || '',
            date: log.F_CreateDate || '',
            signImg: log.F_SignImg,
            stampImg: log.F_StampImg
        });
    });

    return cards;
});

// 当前节点的审批按钮列表
const auditButtons = computed(() => {
    const btnList = currentNodeConfig.value?.btnList || [];
    // 如果节点没有配置按钮，使用默认按钮
    if (btnList.length === 0) {
        return [
            { id: '1', name: '同意', code: 'agree', isHide: '2', isSign: '2', next: '1' },
            { id: '2', name: '不同意', code: 'disagree', isHide: '2', isSign: '2', next: '1' }
        ];
    }
    return btnList;
});

// 获取按钮样式类型
const getButtonType = (code: string): string => {
    const typeMap: Record<string, string> = {
        agree: 'success',
        disagree: 'danger',
        reject: 'warning',
        transfer: 'info',
        recall: 'warning',
        save: 'primary',
        cancel: 'danger'
    };
    return typeMap[code] || 'default';
};

// 按钮点击处理（按力软模式：验证 → 审批 → 保存）
const handleButtonClick = async (btn: any) => {
    const operationCode = btn.code;
    const operationName = btn.name;

    // 对于需要确认的操作（如不同意），检查是否填写了意见
    if (operationCode === 'disagree' && !auditForm.value.des) {
        ElMessage.warning('请输入拒绝理由');
        return;
    }

    try {
        // 1. 表单验证（如果有表单组件且暴露了 validate 方法）
        if (formRef.value?.validate) {
            const valid = await formRef.value.validate();
            if (!valid) {
                ElMessage.warning('表单验证未通过，请检查输入');
                return;
            }
        }

        // 2. 调用 onBeforeAudit（如果表单有此方法，可用于审批前的业务逻辑）
        if (formRef.value?.onBeforeAudit) {
            const canProceed = await formRef.value.onBeforeAudit(operationCode, operationName);
            if (canProceed === false) {
                return;
            }
        }

        // 3. 确认对话框
        await ElMessageBox.confirm(`确定要${operationName}此流程吗？`, '确认', {
            type: 'warning',
            confirmButtonText: '确定',
            cancelButtonText: '取消'
        });

        submitting.value = true;

        // 4. 调用审批API
        await AuditFlow({
            processId: processId.value,
            taskId: taskId.value,
            operationCode: operationCode,
            operationName: operationName,
            des: auditForm.value.des || operationName
        });

        // 5. 审批成功后保存表单（按力软模式：审批成功才保存表单数据）
        if (formRef.value?.save) {
            try {
                await formRef.value.save();
            } catch (saveError: any) {
                console.error('表单保存失败:', saveError);
                // 审批已成功，表单保存失败只是警告
                ElMessage.warning('审批已提交，但表单数据保存失败：' + (saveError.message || '未知错误'));
            }
        }

        // 6. 调用 onAfterAudit（如果表单有此方法，可用于审批后的回调）
        if (formRef.value?.onAfterAudit) {
            await formRef.value.onAfterAudit(operationCode, operationName, true);
        }

        ElMessage.success('审批成功');
        handleBack();
    } catch (e: any) {
        if (e !== 'cancel') {
            ElMessage.error(e.message || '审批失败');

            // 审批失败时也调用 onAfterAudit（用于错误处理）
            if (formRef.value?.onAfterAudit) {
                try {
                    await formRef.value.onAfterAudit(operationCode, operationName, false);
                } catch (afterError) {
                    console.error('onAfterAudit 回调失败:', afterError);
                }
            }
        }
    } finally {
        submitting.value = false;
    }
};

// 初始化
const init = async () => {
    if (!processId.value && !schemeCode.value) {
        ElMessage.error('缺少流程参数');
        return;
    }

    loading.value = true;
    try {
        await loadProcessDetails();
    } catch (e) {
        console.error(e);
        ElMessage.error('加载流程信息失败');
    } finally {
        loading.value = false;
    }
};

// 加载流程详情
const loadProcessDetails = async () => {
    const res: any = await GetProcessDetails({
        processId: processId.value,
        taskId: taskId.value,
        schemeCode: schemeCode.value
    });

    const data = res.data || res;

    if (data.info) {
        isFinished.value = data.info.isFinished === 1;
        taskLogs.value = data.info.TaskLogList || [];
        parentProcessId.value = data.info.F_ParentProcessId || '';

        processInfo.value.schemeCode = data.info.schemeCode || data.info.F_SchemeCode || '';
        processInfo.value.title = data.info.title || data.info.F_Title || '';
        processInfo.value.creatorName = data.info.creatorName || data.info.F_CreateUserName || '';
        processInfo.value.createTime = data.info.createTime || data.info.F_CreateDate || '';
        processInfo.value.isFinished = data.info.isFinished ?? data.info.F_IsFinished ?? 0;

        // 解析流程模板
        if (data.info.Scheme || data.info.F_Scheme) {
            try {
                const schemeStr = data.info.Scheme || data.info.F_Scheme;
                const scheme = JSON.parse(schemeStr);
                schemeContent.value = scheme;
                processInfo.value.schemeName = scheme.name || '';
                if (!processInfo.value.schemeCode) {
                    processInfo.value.schemeCode = scheme.schemeCode || '';
                }
                parseFlowNodes(scheme, data);
            } catch (e) {
                console.error('解析流程模板失败:', e);
            }
        }
    }

    // 获取当前任务节点
    const tasks = data.task || [];
    currentTasks.value = tasks;  // 保存当前待办任务列表
    if (tasks.length > 0) {
        currentNodeName.value = tasks.map((t: any) => t.F_NodeName || t.nodeName).join(', ');
        currentNodeId.value = tasks[0]?.F_NodeId || tasks[0]?.nodeId || '';
    }

    // 查找当前节点配置
    if (schemeContent.value && currentNodeId.value) {
        const nodes = schemeContent.value.nodes || [];
        currentNodeConfig.value = nodes.find((n: any) => n.id === currentNodeId.value) || null;
    }

    // 加载表单组件和业务数据
    await loadFormComponent();

    // 如果还没有表单数据，尝试从流程信息中获取（FormData字段）
    if (Object.keys(formData.value).length === 0) {
        if (data.info?.FormData || data.info?.F_FormData) {
            try {
                const formDataStr = data.info.FormData || data.info.F_FormData;
                formData.value = JSON.parse(formDataStr);
            } catch (e) {
                // ignore
            }
        }
    }
};

// 解析流程图节点
const parseFlowNodes = (scheme: any, data: any) => {
    const nodes = scheme.nodes || [];
    const logs = taskLogs.value;

    // 当前任务节点ID列表
    const tasks = data.task || [];
    const currentNodeIds = tasks.map((t: any) => t.F_NodeId || t.nodeId);
    const strcurrentIds = currentNodeIds.join(',');

    // 构建节点历史信息映射
    const nodeInfoes: Record<string, any[]> = {};
    // 当前节点处理人信息
    tasks.forEach((task: any) => {
        const nameList = (task.nWFUserInfoList || [])
            .filter((u: any) => u.Mark === 0)
            .map((u: any) => u.Name || u.Id);
        nodeInfoes[task.F_NodeId || task.nodeId] = nodeInfoes[task.F_NodeId || task.nodeId] || [];
        nodeInfoes[task.F_NodeId || task.nodeId].push({ namelist: nameList });
    });
    // 历史处理信息
    logs.forEach((log: any) => {
        nodeInfoes[log.F_NodeId] = nodeInfoes[log.F_NodeId] || [];
        nodeInfoes[log.F_NodeId].push(log);
    });

    // 构建节点映射并处理节点
    const newNodeMap: Record<string, any> = {};

    flowNodes.value = nodes
        .filter((n: any) => ['startround', 'endround', 'auditornode', 'stepnode', 'conditionnode', 'confluencenode', 'childwfnode'].includes(n.type))
        .map((n: any) => {
            // 计算节点状态：0=正在处理, 1=已处理同意, 2=已处理不同意, 3=未处理
            let status = 'pending';  // 3=未处理
            if (nodeInfoes[n.id]) {
                // 检查是否有不同意的操作
                const nodeLog = logs.find((l: any) => l.F_NodeId === n.id);
                if (nodeLog?.F_OperationCode === 'disagree') {
                    status = 'rejected';  // 2=已处理不同意
                } else {
                    status = 'done';  // 1=已处理同意
                }
            }
            if (strcurrentIds.indexOf(n.id) > -1) {
                status = 'current';  // 0=正在处理
            }

            // 构建节点名称（添加多人审核标识）
            let nodeName = n.name || n.text?.value || '未命名节点';
            if (n.isAllAuditor === '2') {
                // 多人审核节点
                if (n.auditorType === '1') {
                    nodeName += '\n【多人审核: 并行】';
                } else {
                    nodeName += '\n【多人审核: 串行】';
                }
            }

            // 获取处理人
            let handler = '';
            const log = logs.find((l: any) => l.F_NodeId === n.id);
            if (log) {
                handler = log.F_TaskUserName || '';
            } else if (status === 'current') {
                // 当前节点显示待处理人
                const task = tasks.find((t: any) => (t.F_NodeId || t.nodeId) === n.id);
                if (task?.nWFUserInfoList) {
                    handler = task.nWFUserInfoList
                        .filter((u: any) => u.Mark === 0)
                        .map((u: any) => u.Name || u.Id)
                        .join(', ');
                }
            }

            const nodeData = {
                id: n.id,
                name: nodeName,
                type: n.type,
                status,
                handler,
                history: nodeInfoes[n.id] || null
            };

            newNodeMap[n.id] = nodeData;
            return nodeData;
        });

    nodeMap.value = newNodeMap;

    // 构建用于 lrworkflow 渲染的数据（包含节点状态和历史记录）
    // 力软格式：node.state = '0'正在处理, '1'已处理, '2'不同意, '3'未处理
    const processedNodes = nodes.map((n: any) => {
        const nodeData = newNodeMap[n.id];
        let state = '3';  // 默认未处理
        let history = null;
        if (nodeData) {
            if (nodeData.status === 'current') state = '0';
            else if (nodeData.status === 'done') state = '1';
            else if (nodeData.status === 'rejected') state = '2';
            history = nodeData.history;  // 传递历史记录，用于双击查看
        }
        return { ...n, state, history };
    });

    // 设置流程图数据
    flowSchemeData.value = {
        nodes: processedNodes,
        lines: scheme.lines || []
    };
};


// 加载表单组件
const loadFormComponent = async () => {
    // 只使用当前节点的表单配置，没有配置就不显示表单
    const nodeConfig = currentNodeConfig.value;
    console.log('[Workflow] 当前节点配置:', nodeConfig);

    // 如果当前节点没有wfForms配置，不加载表单
    if (!nodeConfig?.wfForms?.length) {
        console.log('[Workflow] 当前节点没有配置表单');
        formComponent.value = null;
        formParams.value = {};
        return;
    }

    // 获取表单信息（包含组件和URL参数）
    const formInfo = getFormInfo(nodeConfig, '0');
    console.log('[Workflow] 表单信息:', formInfo);

    if (formInfo.component) {
        formComponent.value = formInfo.component;
        // 将URL参数与processId合并，processId作为业务数据ID注入
        // 这样表单组件可以通过 formParams.id 获取到业务数据ID并加载数据
        formParams.value = {
            ...formInfo.params,
            id: processId.value  // 自动注入：processId = 业务数据ID
        };
        console.log('[Workflow] 表单参数（含processId）:', formParams.value);
    } else {
        // 表单组件未找到
        console.warn('[Workflow] 未找到表单组件:', formInfo.formPath);
        formComponent.value = null;
        formParams.value = {};
    }
};

// 获取日志标签类型
const getLogTagType = (log: any) => {
    if (log.F_OperationCode === 'agree') return 'success';
    if (log.F_OperationCode === 'disagree') return 'danger';
    if (log.F_OperationCode === 'create') return 'primary';
    return 'info';
};

// 获取时间线节点样式类
const getTimelineDotClass = (item: any) => {
    if (item.type === 'current') return 'is-current';
    if (item.operationCode === 'agree') return 'is-agree';
    if (item.operationCode === 'disagree') return 'is-disagree';
    if (item.operationCode === 'create') return 'is-create';
    return 'is-default';
};

// 获取印章图片URL
const getStampUrl = (stampId: string) => {
    if (!stampId) return '';
    // TODO: 根据实际API调整
    return `/api/workflow/stamp/${stampId}`;
};

// 获取签名图片URL
const getSignUrl = (signId: string) => {
    if (!signId) return '';
    // TODO: 根据实际API调整
    return `/api/system/img/${signId}`;
};

// 节点双击事件处理（查看审批记录）
const handleNodeDoubleClick = (node: any) => {
    console.log('[Workflow] 节点双击:', node);

    // 子流程节点：打开子流程查看
    if (node.type === 'childwfnode') {
        if (node.childFlow) {
            // TODO: 打开子流程查看页面
            ElMessage.info('子流程查看功能开发中');
        }
        return;
    }

    // 其他节点：如果有历史记录，显示审批记录
    if (node.history && Array.isArray(node.history) && node.history.length > 0) {
        // 查找该节点的审批记录
        const nodeLogs = taskLogs.value.filter((l: any) => l.F_NodeId === node.id);

        if (nodeLogs.length > 0) {
            // 构建审批记录HTML
            let html = '<div class="node-audit-records">';
            nodeLogs.forEach((log: any) => {
                html += `
                    <div class="audit-record-item" style="margin-bottom: 15px; padding: 10px; border: 1px solid #eee; border-radius: 4px;">
                        <p><strong>处理人：</strong>${log.F_TaskUserName || log.F_CreateUserName || '-'}</p>
                        <p><strong>操作：</strong>${log.F_OperationName || '-'}</p>
                        <p><strong>意见：</strong>${log.F_Des || '无'}</p>
                        <p><strong>时间：</strong>${log.F_CreateDate || '-'}</p>
                    </div>
                `;
            });
            html += '</div>';

            ElMessageBox.alert(html, `审批记录查看【${node.name}】`, {
                dangerouslyUseHTMLString: true,
                customClass: 'node-audit-dialog'
            });
        } else {
            ElMessage.info('该节点暂无审批记录');
        }
    } else {
        // 未处理的节点
        ElMessage.info('该节点尚未处理');
    }
};

// 创建流程
const handleCreate = async () => {
    ElMessage.info('创建流程功能开发中');
};

// 保存草稿
const handleSaveDraft = async () => {
    ElMessage.info('保存草稿功能开发中');
};

// 加签
const handleSign = () => {
    ElMessage.info('加签功能开发中');
};

// 传阅确认
const handleRefer = async () => {
    submitting.value = true;
    try {
        await ReferFlow({
            processId: processId.value,
            taskId: taskId.value,
            des: auditForm.value.des || '已阅'
        });
        ElMessage.success('操作成功');
        handleBack();
    } catch (e: any) {
        ElMessage.error(e.message || '操作失败');
    } finally {
        submitting.value = false;
    }
};

// 重新创建
const handleAgainCreate = () => {
    ElMessage.info('重新创建功能开发中');
};

// 打印表单
const handlePrint = () => {
    ElMessage.info('打印功能开发中');
};

// 查看父流程
const handleViewParent = () => {
    if (parentProcessId.value) {
        router.push({
            path: '/workflow/work',
            query: { processId: parentProcessId.value, type: 'lookParent' }
        });
    }
};

// 返回
const handleBack = () => {
    router.push('/workflow/process');
};

onMounted(() => {
    init();
});
</script>

<style lang="scss" scoped>
.workflow-work-page {
    height: 100%;
    padding: 5px;
    background: transparent;
}

.lr-layout-panel {
    position: relative;
    height: 100%;
    width: 100%;
    border: 1px solid #dcdfe6;
    background: #fff;
    padding-right: 360px;
}

.lr-layout-left {
    position: relative;
    height: 100%;
    width: 100%;
}

.lr-toolbar {
    position: absolute;
    top: 5px;
    right: 10px;
    z-index: 2;
}

.lr-tabs {
    height: 100%;

    :deep(.el-tabs__header) {
        margin: 0;
        padding: 0 10px;
        border-bottom: 1px solid #e4e7ed;
    }

    :deep(.el-tabs__content) {
        height: calc(100% - 40px);
        padding: 0;
    }

    :deep(.el-tab-pane) {
        height: 100%;
    }
}

.tab-content {
    height: 100%;
    overflow: auto;
    padding: 15px;
}

/* 右侧审批信息 */
.lr-layout-right {
    position: absolute;
    top: 0;
    right: 0;
    height: 100%;
    width: 360px;
    border-left: 1px solid #dcdfe6;
    background: #fff;
}

.right-header {
    height: 40px;
    line-height: 39px;
    padding: 0 15px;
    font-weight: bold;
    color: #606266;
    border-bottom: 1px solid #e4e7ed;
}

.right-body {
    height: calc(100% - 40px);
    overflow: auto;
    padding: 15px;
}

.audit-form {
    :deep(.el-form-item__label) {
        font-weight: 500;
        color: #606266;
    }
}

.action-buttons {
    margin-top: 15px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.back-btn {
    margin-top: 20px;
    padding-top: 15px;
    border-top: 1px solid #ebeef5;
}

/* 流程图样式 */
.flow-content {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.flow-diagram-area {
    flex: 1;
    overflow: hidden;
    position: relative;
}

/* 图例样式（与力软一致） */
.flow-legend {
    position: absolute;
    left: 0;
    bottom: 0;
    width: 100%;
    height: 40px;
    border-top: 1px solid #ddd;
    line-height: 39px;
    text-align: right;
    padding-right: 10px;
    font-size: 14px;
    background: #fff;
    z-index: 1;

    .legend-item {
        display: inline-block;
        margin-left: 15px;
    }

    .legend-color {
        display: inline-block;
        width: 14px;
        height: 14px;
        margin-right: 5px;
        vertical-align: middle;

        &.current {
            background: #5bc0de; // 力软：正在处理-蓝色
        }

        &.done {
            background: #5cb85c; // 力软：已处理-绿色
        }

        &.pending {
            background: #999; // 力软：未处理-灰色
        }
    }
}

/* 流转记录时间线样式（仿力软 lrtimeline） */
.lr-timeline {
    padding: 10px 0;

    .timeline-item {
        position: relative;
        padding-left: 25px;
        padding-bottom: 20px;

        &:last-child {
            padding-bottom: 0;
        }

        // 连接线
        &::before {
            content: '';
            position: absolute;
            left: 7px;
            top: 14px;
            bottom: 0;
            width: 2px;
            background: #e4e7ed;
        }

        &:last-child::before {
            display: none;
        }

        // 当前待办项特殊样式
        &.is-current {
            .timeline-content {
                background: #ecf5ff;
                border-color: #409eff;
            }

            .timeline-title {
                color: #409eff;
            }
        }
    }

    .timeline-dot {
        position: absolute;
        left: 0;
        top: 5px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #e4e7ed;
        border: 2px solid #fff;
        box-shadow: 0 0 0 2px #e4e7ed;

        &.is-current {
            background: #409eff;
            box-shadow: 0 0 0 2px #409eff;
            animation: dotPulse 1.5s infinite;
        }

        &.is-agree {
            background: #67c23a;
            box-shadow: 0 0 0 2px #67c23a;
        }

        &.is-disagree {
            background: #f56c6c;
            box-shadow: 0 0 0 2px #f56c6c;
        }

        &.is-create {
            background: #409eff;
            box-shadow: 0 0 0 2px #409eff;
        }
    }

    @keyframes dotPulse {

        0%,
        100% {
            transform: scale(1);
        }

        50% {
            transform: scale(1.2);
        }
    }

    .timeline-content {
        background: #fff;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
        padding: 12px 15px;
    }

    .timeline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .timeline-title {
        font-weight: 500;
        color: #303133;
        font-size: 14px;
    }

    .timeline-time {
        font-size: 12px;
        color: #909399;
    }

    .timeline-body {
        .timeline-user {
            font-size: 13px;
            color: #606266;
            margin-bottom: 5px;
        }

        .timeline-desc {
            font-size: 13px;
            color: #909399;
            line-height: 1.6;
        }
    }

    .timeline-sign {
        margin-top: 10px;
        display: flex;
        gap: 10px;

        .stamp-img,
        .sign-img {
            max-height: 60px;
            max-width: 120px;
        }
    }
}

/* 审批历史摘要 */
.audit-history-summary {
    margin-top: 20px;

    .history-item {
        padding: 10px 0;
        border-bottom: 1px dashed #ebeef5;

        &:last-child {
            border-bottom: none;
        }
    }

    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;

        .history-node {
            font-weight: 500;
            color: #303133;
            font-size: 13px;
        }
    }

    .history-footer {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #909399;
    }

    .history-more {
        text-align: center;
        padding-top: 10px;
    }
}

/* 查看模式 - 流程信息摘要（紧凑版） */
.process-summary-compact {
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;

    .summary-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .summary-title {
            font-size: 14px;
            font-weight: 600;
            color: #303133;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            flex: 1;
            margin-right: 10px;
        }
    }

    .summary-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 4px 12px;

        .summary-item {
            font-size: 12px;
            color: #606266;

            .label {
                font-style: normal;
                color: #909399;
                margin-right: 4px;

                &::after {
                    content: '：';
                }
            }
        }
    }
}

/* 查看模式 - 审批信息卡片（仿力软 tab-flow-audit） */
.tab-flow-audit {
    margin-top: 8px;

    .auditinfo {
        position: relative;
        width: 100%;
        min-height: 100px;
        border: 1px solid #dcdfe6;
        padding-left: 90px;
        margin-bottom: -1px;  // 合并边框

        &:first-child {
            border-radius: 4px 4px 0 0;
        }

        &:last-child {
            border-radius: 0 0 4px 4px;
            margin-bottom: 0;
        }

        &:only-child {
            border-radius: 4px;
        }
    }

    .auditinfo-h {
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 90px;
        border-right: 1px solid #dcdfe6;
        padding: 8px;
        background: #f5f7fa;
        font-size: 13px;
        font-weight: 500;
        color: #606266;
        display: flex;
        align-items: center;
        word-break: break-all;
    }

    .auditinfo-b {
        position: relative;
        width: 100%;
        min-height: 100px;
        padding: 8px 10px 32px 10px;
    }

    .auditinfo-content {
        font-size: 13px;
        color: #606266;
        line-height: 1.6;
        margin: 0;
        padding-right: 70px;  // 给签章留空间
    }

    .auditinfo-s {
        position: absolute;
        top: 8px;
        right: 8px;
        max-height: 60px;

        img {
            max-height: 60px;
            max-width: 80px;
        }
    }

    .auditinfo-sg {
        position: absolute;
        top: 8px;
        right: 8px;
        max-height: 36px;

        img {
            max-height: 36px;
            max-width: 80px;
        }
    }

    .auditinfo-n,
    .auditinfo-d {
        position: absolute;
        right: 10px;
        font-size: 12px;
        color: #909399;
    }

    .auditinfo-n {
        bottom: 24px;
    }

    .auditinfo-d {
        bottom: 8px;
    }
}

/* 加载状态 */
.loading-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    color: #909399;

    .el-icon {
        font-size: 36px;
        margin-bottom: 15px;
    }
}
</style>
