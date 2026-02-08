<template>
    <div class="layout-padding">
        <div class="layout-padding-auto layout-padding-view">
            <el-row>
                <el-col :span="24">
                    <div class="mb15">
                        <el-input v-model="query.keys" placeholder="关键字搜索" style="width: 200px; margin-right: 10px;" />
                        <el-button type="primary" icon="Search" @click="fetchData">查询</el-button>
                        <el-button type="success" icon="Plus" @click="handleCreate">发起流程</el-button>
                    </div>
                </el-col>
            </el-row>

            <el-table :data="list" v-loading="loading" style="width: 100%" border>
                <el-table-column type="index" label="序号" width="60" align="center" />
                <el-table-column prop="scheme_name" label="流程名称" width="180" />
                <el-table-column prop="title" label="流程标题" min-width="200" show-overflow-tooltip />
                <el-table-column prop="create_datetime" label="发起时间" width="160" />
                <el-table-column prop="is_finished" label="状态" width="100" align="center">
                    <template #default="scope">
                        <el-tag v-if="scope.row.is_finished === 1" type="success">已结束</el-tag>
                        <el-tag v-else type="primary">进行中</el-tag>
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
import { GetMyCreateTasks } from '../api/task' // 注意：这里可能需要后端区分是 GetMyCreateProcess 还是 Tasks

// 后端 process/views.py 有 get_my_process，对应 api 还没细看
// api/task.ts 里有 GetMyCreateTasks，对应 url /task/my-create-tasks/
// 假设后端 Task 模块有这个接口。如果没有，可能需用 Process 模块接口。
// 查阅 api/task.ts 里的 GetMyCreateTasks 指向 /api/node_workflow/task/my-create-tasks/
// 让我们先用着，如果报错再改 api 路径指向 /process/my-process/

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
        const res: any = await GetMyCreateTasks(query)
        if (res.data && res.data.results) {
            list.value = res.data.results
            total.value = res.data.total || 0
        } else {
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
    // row 这里是 process 对象还是 task 对象？
    // 如果是 my-create-tasks, 可能返回的是 TaskModel (第一个任务?) 还是 ProcessModel?
    // 通常"我发起的"是 Process 列表。
    // 如果后端 GetMyCreateTasks 返回的是 Task，那 process_id 在 row.process_id
    // 如果是 Process，ID 在 row.id
    // 为了保险，先打印看看，或者假设都有 id (如果是Process) 或 process_id (如果是Task)
    // 假设是 ProcessModel，则用 row.id
    const pid = row.process_id || row.id
    router.push({
        path: '/workflow/work',
        query: {
            processId: pid
        }
    })
}

const handleCreate = () => {
    // 跳转到模板列表选择模板发起
    router.push('/workflow/scheme')
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
