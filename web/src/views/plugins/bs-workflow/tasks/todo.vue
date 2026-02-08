<template>
    <div class="layout-padding">
        <div class="layout-padding-auto layout-padding-view">
            <el-card shadow="hover" class="layout-padding-auto">
                <div class="mb15">
                    <el-input v-model="listQuery.search" placeholder="请输入流程名称/编号" style="width: 250px" class="mr10"
                            clearable @keyup.enter="handleFilter" />
                    <el-button type="primary" icon="Search" @click="handleFilter">查询</el-button>
                </div>

                <el-table :data="list" v-loading="listLoading" border stripe style="width: 100%">
                    <el-table-column prop="scheme_name" label="流程模板" width="150" />
                    <el-table-column prop="title" label="任务标题" min-width="200" show-overflow-tooltip />
                    <el-table-column prop="node_name" label="当前节点" width="150">
                        <template #default="{ row }">
                            <el-tag>{{ row.node_name }}</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="sender_name" label="发起人" width="120" />
                    <el-table-column prop="create_datetime" label="接收时间" width="180" />
                    <el-table-column prop="level" label="等级" width="100" align="center">
                        <template #default="{ row }">
                            <el-tag v-if="row.level === 1" type="danger">重要</el-tag>
                            <el-tag v-else-if="row.level === 2" type="warning">紧急</el-tag>
                            <el-tag v-else type="info">普通</el-tag>
                        </template>
                    </el-table-column>

                    <el-table-column label="操作" width="100" fixed="right" align="center">
                        <template #default="{ row }">
                            <el-button type="primary" link icon="Edit" @click="handleWork(row)">办理</el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <el-pagination v-show="total > 0" v-model:current-page="listQuery.page"
                        v-model:page-size="listQuery.limit" :total="total" :page-sizes="[10, 20, 30, 50]"
                        layout="total, sizes, prev, pager, next, jumper" class="mt15" @size-change="getList"
                        @current-change="getList" />
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { GetMyTasks } from '../api/task'

const router = useRouter()
const list = ref([])
const total = ref(0)
const listLoading = ref(false)
const listQuery = reactive({
    page: 1,
    limit: 20,
    search: ''
})

const getList = () => {
    listLoading.value = true
    GetMyTasks(listQuery).then((res: any) => {
        // 适配后端返回格式，假设是标准的 DRF 分页
        list.value = res.data.results || res.data
        total.value = res.data.count || 0
    }).finally(() => {
        listLoading.value = false
    })
}

const handleFilter = () => {
    listQuery.page = 1
    getList()
}

const handleWork = (row: any) => {
    // 跳转到办理页面
    // 传递 taskId, processId, 以及可能需要的 schemeCode
    router.push({
        path: '/workflow/work',
        query: {
            taskId: row.id,
            processId: row.process,
            nodeId: row.node_id
        }
    })
}

onMounted(() => {
    getList()
})
</script>
