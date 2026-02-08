<template>
    <div class="layout-padding">
        <div class="layout-padding-auto layout-padding-view">
            <el-row>
                <el-col :span="24">
                    <div class="mb15">
                        <el-input v-model="query.keys" placeholder="关键字搜索" style="width: 200px; margin-right: 10px;" />
                        <el-button type="primary" icon="Search" @click="fetchData">查询</el-button>
                    </div>
                </el-col>
            </el-row>

            <el-table :data="list" v-loading="loading" style="width: 100%" border>
                <el-table-column type="index" label="序号" width="60" align="center" />
                <el-table-column prop="scheme_name" label="流程名称" width="180" />
                <el-table-column prop="title" label="任务标题" min-width="200" show-overflow-tooltip />
                <el-table-column prop="node_name" label="办理节点" width="120" />
                <el-table-column prop="creator_name" label="发起人" width="100" />
                <el-table-column prop="create_datetime" label="接收时间" width="160" />
                <el-table-column prop="end_time" label="办理时间" width="160">
                    <template #default="scope">
                        {{ scope.row.update_datetime }}
                    </template>
                </el-table-column>
                <el-table-column label="操作" width="100" fixed="right" align="center">
                    <template #default="scope">
                        <el-button link type="primary" icon="View" @click="handleView(scope.row)">查看</el-button>
                    </template>
                </el-table-column>
            </el-table>

            <el-pagination class="mt15" v-model:current-page="query.page" v-model:page-size="query.limit" :total="total"
                    layout="total, prev, pager, next, jumper" @current-change="fetchData" @size-change="fetchData" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { GetFinishedTasks } from '../api/task'

const router = useRouter()
const list = ref([])
const total = ref(0)
const loading = ref(false)
const query = reactive({
    page: 1,
    limit: 20,
    keys: ''
})

const fetchData = async () => {
    loading.value = true
    try {
        const res: any = await GetFinishedTasks(query)
        if (res.data && res.data.results) {
            list.value = res.data.results
            total.value = res.data.total || 0
        } else {
            // 兼容非分页或不同结构
            list.value = res.data || []
            total.value = list.value.length
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const handleView = (row: any) => {
    // 传递 processId 查看详情
    router.push({
        path: '/workflow/work',
        query: {
            processId: row.process_id
        }
    })
}

onMounted(() => {
    fetchData()
})

</script>

<style scoped>
.mb15 {
    margin-bottom: 15px;
}

.mt15 {
    margin-top: 15px;
}
</style>
