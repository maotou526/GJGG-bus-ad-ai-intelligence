<template>
    <div class="workflow-page">
        <el-row class="workflow-row" :gutter="15">
            <el-col :span="3">
                <el-card shadow="hover" class="workflow-left-card">
                    <ul class="lr-left-list">
                        <li :class="{ active: activeCategory === '2' }" @click="handleSelectCategory('2')">待办任务</li>
                        <li :class="{ active: activeCategory === '3' }" @click="handleSelectCategory('3')">已办任务</li>
                        <li :class="{ active: activeCategory === '1' }" @click="handleSelectCategory('1')">我的流程</li>
                    </ul>
                </el-card>
            </el-col>

            <el-col :span="21">
                <el-card shadow="hover" class="workflow-right-card">
                    <!-- 工具栏 -->
                    <div class="workflow-toolbar">
                        <div class="toolbar-left">
                            <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
                                    start-placeholder="开始日期" end-placeholder="结束日期" value-format="YYYY-MM-DD"
                                    size="default" style="width: 240px" @change="handleSearch" />
                            <el-input v-model="keyword" placeholder="请输入要查询关键字" clearable size="default"
                                    style="width: 200px" @keyup.enter="handleSearch" />
                            <el-button type="primary" size="default" @click="handleSearch">
                                <el-icon>
                                    <Search />
                                </el-icon>
                                <span>查询</span>
                            </el-button>
                        </div>
                        <div class="toolbar-right">
                            <el-button @click="handleRefresh">
                                <el-icon>
                                    <Refresh />
                                </el-icon>
                            </el-button>
                        </div>
                    </div>

                    <!-- 表格 -->
                    <div class="workflow-table">
                        <el-table ref="tableRef" :data="tableData" v-loading="loading" border
                                @row-dblclick="handleRowDblClick" height="100%">
                            <el-table-column prop="nodeName" label="任务" min-width="180">
                                <template #default="{ row }">
                                    <!-- 我的流程 -->
                                    <template v-if="activeCategory === '1'">
                                        <template v-if="row.isAgain === 1">
                                            <el-tag type="danger" class="action-tag"
                                                    @click.stop="handleAgainCreate(row)">重新发起</el-tag>
                                        </template>
                                        <template v-else-if="row.isFinished === 0">
                                            <el-tag type="primary" class="action-tag"
                                                    @click.stop="handleUrge(row)">催办审核</el-tag>
                                            <el-tag v-if="row.isStart === 0" type="warning" class="action-tag"
                                                    @click.stop="handleRevoke(row)">撤销流程</el-tag>
                                        </template>
                                        <template v-else>
                                            <span>本人发起</span>
                                        </template>
                                    </template>
                                    <!-- 待办/已办 -->
                                    <template v-else>
                                        <template v-if="row.type === 3">
                                            <span>【加签】{{ row.nodeName }}</span>
                                        </template>
                                        <template v-else-if="row.type === 5 && activeCategory === '2'">
                                            <el-tag type="danger" class="action-tag"
                                                    @click.stop="handleAgainCreate(row)">重新发起</el-tag>
                                        </template>
                                        <template v-else-if="row.type === 5">
                                            <span>重新发起</span>
                                        </template>
                                        <template
                                                v-else-if="activeCategory === '3' && row.type === 1 && row.status === 0">
                                            <el-tag type="warning" class="action-tag"
                                                    @click.stop="handleRevokeAudit(row)">撤销审核</el-tag>
                                            <span>{{ row.nodeName }}</span>
                                        </template>
                                        <template v-else>
                                            <span>{{ row.nodeName }}</span>
                                        </template>
                                    </template>
                                </template>
                            </el-table-column>
                            <el-table-column prop="title" label="标题" min-width="300">
                                <template #default="{ row }">
                                    {{ formatTitle(row) }}
                                </template>
                            </el-table-column>
                            <el-table-column prop="level" label="等级" width="80">
                                <template #default="{ row }">
                                    {{ formatLevel(row.level) }}
                                </template>
                            </el-table-column>
                            <el-table-column label="状态" width="100">
                                <template #default="{ row }">
                                    <el-tag :type="getStatusType(row)" size="small">{{ formatStatus(row) }}</el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column prop="creator" label="发起者" width="100" />
                            <el-table-column prop="createTime" label="创建时间" width="160" />
                            <el-table-column label="操作" width="140" fixed="right">
                                <template #default="{ row }">
                                    <el-button v-if="activeCategory === '2'" type="primary" link size="small"
                                            @click="handleAuditRow(row)">
                                        {{ getAuditButtonText(row) }}
                                    </el-button>
                                    <el-button type="info" link size="small" @click="handleViewRow(row)">查看</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>

                    <!-- 分页 -->
                    <div class="workflow-pagination">
                        <el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.limit"
                                :page-sizes="[10, 20, 50, 100]" :total="pagination.total"
                                layout="total, sizes, prev, pager, next, jumper" @size-change="handleSearch"
                                @current-change="handleSearch" />
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Refresh } from '@element-plus/icons-vue';
import * as api from '../api/process';

const router = useRouter();

// 侧边栏状态
const activeCategory = ref('2'); // 默认待办

// 搜索条件
const dateRange = ref<string[]>([]);
const keyword = ref('');

// 表格数据
const tableRef = ref();
const tableData = ref<any[]>([]);
const loading = ref(false);

// 分页
const pagination = ref({
    page: 1,
    limit: 20,
    total: 0
});

// 获取审核按钮文字（行级别）
const getAuditButtonText = (row: any) => {
    if (row.type === 5) return '重新发起';
    if (row.type === 3) return '加签审批';
    return '审核';
};

// 处理侧边栏切换
const handleSelectCategory = (index: string) => {
    activeCategory.value = index;
    pagination.value.page = 1;
    handleSearch();
};

// 刷新
const handleRefresh = () => {
    handleSearch();
};

// 搜索
const handleSearch = async () => {
    loading.value = true;
    try {
        const params: any = {
            page: pagination.value.page,
            limit: pagination.value.limit,
            categoryId: activeCategory.value
        };
        if (keyword.value) {
            params.keyword = keyword.value;
        }
        if (dateRange.value && dateRange.value.length === 2) {
            params.StartTime = dateRange.value[0] + ' 00:00:00';
            params.EndTime = dateRange.value[1] + ' 23:59:59';
        }

        const res: any = await api.GetTaskPageList(params);
        // 后端返回 { data: { total, data: [...] } }
        const result = res.data || res;
        tableData.value = result.data || [];
        pagination.value.total = result.total || 0;
    } finally {
        loading.value = false;
    }
};

// 双击行
const handleRowDblClick = (row: any) => {
    if (activeCategory.value === '2') {
        handleAuditRow(row);
    } else {
        handleViewRow(row);
    }
};

// 审核行
const handleAuditRow = (row: any) => {
    const processId = row.processId || row.id;
    const taskId = row.taskId || row.id;

    // 1审批 2传阅 3加签 4子流程 5重新创建 6重新创建子流程
    switch (row.type) {
        case 1: // 审批
            router.push({ path: '/workflow/work', query: { processId, taskId, type: 'audit' } });
            break;
        case 2: // 传阅
            router.push({ path: '/workflow/work', query: { processId, taskId, type: 'refer' } });
            break;
        case 3: // 加签
            router.push({ path: '/workflow/work', query: { processId, taskId, type: 'signAudit' } });
            break;
        case 4: // 子流程
            router.push({ path: '/workflow/work', query: { processId, taskId, type: 'child' } });
            break;
        case 5: // 重新创建
            router.push({ path: '/workflow/work', query: { processId, type: 'againCreate' } });
            break;
        case 6: // 重新创建子流程
            router.push({ path: '/workflow/work', query: { processId, taskId, type: 'againChild' } });
            break;
        default:
            router.push({ path: '/workflow/work', query: { processId, taskId, type: 'audit' } });
    }
};

// 查看行
const handleViewRow = (row: any) => {
    const processId = row.processId || row.id;
    const taskId = row.taskId || row.id;

    if (row.type === 4 || row.type === 6) {
        router.push({ path: '/workflow/work', query: { processId, taskId, type: 'childlook' } });
    } else {
        router.push({ path: '/workflow/work', query: { processId, taskId, type: 'look' } });
    }
};

// 催办
const handleUrge = async (row: any) => {
    try {
        await ElMessageBox.confirm('是否确认催办审核？', '提示', { type: 'warning' });
        await api.UrgeFlow({ processId: row.processId || row.id });
        ElMessage.success('催办成功');
    } catch (e) {
        // cancel
    }
};

// 撤销流程
const handleRevoke = async (row: any) => {
    try {
        await ElMessageBox.confirm('是否确认撤销流程？', '提示', { type: 'warning' });
        await api.RevokeFlow({ processId: row.processId || row.id });
        ElMessage.success('撤销成功');
        handleSearch();
    } catch (e) {
        // cancel
    }
};

// 撤销审核
const handleRevokeAudit = async (row: any) => {
    try {
        await ElMessageBox.confirm('是否确认撤销审核？', '提示', { type: 'warning' });
        await api.RevokeAudit({ processId: row.processId || row.id, taskId: row.taskId || row.id });
        ElMessage.success('撤销成功');
        handleSearch();
    } catch (e: any) {
        if (e.response?.data?.info) {
            ElMessage.error(e.response.data.info);
        }
    }
};

// 重新发起
const handleAgainCreate = (row: any) => {
    const processId = row.processId || row.id;
    router.push({ path: '/workflow/work', query: { processId, type: 'againCreate' } });
};

// 格式化标题
const formatTitle = (row: any) => {
    if (row.schemeName && row.title && row.schemeName !== row.title) {
        return `${row.schemeName}(${row.title})`;
    }
    return row.schemeName || row.title || '';
};

// 格式化等级
const formatLevel = (level: number) => {
    switch (level) {
        case 1: return '重要';
        case 2: return '紧急';
        default: return '普通';
    }
};

// 格式化状态
const formatStatus = (row: any) => {
    // 我的流程用 isFinished
    if (activeCategory.value === '1') {
        return row.isFinished === 1 ? '已结束' : '运行中';
    }
    // 待办/已办用 status 或根据 isUrge 判断
    if (row.type === 4) {
        return row.status === 0 ? (row.isUrge === 1 ? '催办加急' : '运行中') : '结束';
    }
    if (row.status === 1) return '已结束';
    return row.isUrge === 1 ? '催办加急' : '运行中';
};

// 获取状态类型
const getStatusType = (row: any) => {
    if (activeCategory.value === '1') {
        return row.isFinished === 1 ? 'warning' : 'success';
    }
    if (row.status === 1) return 'warning';
    if (row.isUrge === 1) return 'danger';
    return 'success';
};

onMounted(() => {
    handleSearch();
});
</script>

<style lang="scss" scoped>
.workflow-page {
    width: 100%;
    height: 100%;
    padding: 10px;
    box-sizing: border-box;
}

.workflow-row {
    height: 100%;
    overflow: hidden;

    .el-col {
        height: 100%;
        box-sizing: border-box;
    }
}

.workflow-left-card {
    height: 100%;

    :deep(.el-card__body) {
        padding: 0;
        height: 100%;
    }
}

.workflow-right-card {
    height: 100%;
    display: flex;
    flex-direction: column;

    :deep(.el-card__body) {
        flex: 1;
        display: flex;
        flex-direction: column;
        padding: 0;
        overflow: hidden;
    }
}

.lr-left-list {
    list-style: none;
    padding: 10px 0;
    margin: 0;

    li {
        padding: 12px 20px;
        cursor: pointer;
        color: var(--el-text-color-regular);
        font-size: 14px;
        transition: all 0.3s;

        &:hover {
            background-color: var(--el-color-primary-light-9);
            color: var(--el-color-primary);
        }

        &.active {
            background-color: var(--el-color-primary);
            color: #fff;
        }
    }
}

.workflow-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    border-bottom: 1px solid var(--el-border-color-light);
    flex-shrink: 0;

    .toolbar-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .toolbar-right {
        display: flex;
        align-items: center;
        gap: 10px;
    }
}

.workflow-table {
    flex: 1;
    overflow: hidden;
    padding: 15px;
}

.workflow-pagination {
    padding: 15px;
    border-top: 1px solid var(--el-border-color-light);
    display: flex;
    justify-content: flex-end;
    flex-shrink: 0;
}

.action-tag {
    cursor: pointer;
    margin-right: 5px;

    &:hover {
        opacity: 0.8;
    }
}
</style>
