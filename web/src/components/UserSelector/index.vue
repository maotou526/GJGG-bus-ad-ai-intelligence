<template>
    <el-dialog v-model="visible" :title="title" width="900px" @close="handleClose" append-to-body destroy-on-close
            class="user-selector-dialog">
        <el-container class="selector-container" style="height: 500px; border: 1px solid #eee">
            <!-- 左侧部门树 -->
            <el-aside width="280px"
                    style="border-right: 1px solid #eee; padding: 10px; display: flex; flex-direction: column;">
                <el-input v-model="filterText" placeholder="输入部门名称过滤" clearable class="mb-2" />
                <el-scrollbar>
                    <el-tree ref="treeRef" :data="deptTree" :props="defaultProps" :filter-node-method="filterNode"
                            node-key="id" highlight-current default-expand-all @node-click="handleNodeClick" />
                </el-scrollbar>
            </el-aside>

            <!-- 右侧人员列表 -->
            <el-main style="padding: 10px; display: flex; flex-direction: column;">
                <div class="search-box mb-2" style="display: flex; gap: 10px;">
                    <el-input v-model="searchKeyword" placeholder="输入姓名/账号/手机号搜索" style="width: 250px;"
                            @keyup.enter="handleSearch" clearable @clear="handleSearch" />
                    <el-button type="primary" @click="handleSearch">搜索</el-button>
                </div>

                <el-table ref="tableRef" :data="userList" style="width: 100%; flex: 1;" v-loading="loading" row-key="id"
                        @selection-change="handleSelectionChange" height="100%">
                    <el-table-column type="selection" width="55" :reserve-selection="true" />
                    <el-table-column prop="name" label="姓名" width="120" show-overflow-tooltip />
                    <el-table-column prop="username" label="账号" width="120" show-overflow-tooltip />
                    <el-table-column prop="dept_name" label="部门" show-overflow-tooltip />
                    <el-table-column prop="mobile" label="手机号" width="120" show-overflow-tooltip />
                </el-table>

                <div class="pagination-box mt-2" style="text-align: right;">
                    <el-pagination v-model:current-page="pagination.current" v-model:page-size="pagination.size"
                            :total="pagination.total" layout="total, prev, pager, next"
                            @current-change="handlePageChange" />
                </div>
            </el-main>
        </el-container>

        <div class="selected-tags mt-2" v-if="multiple && selectedUsers.length > 0">
            <span class="label">已选人员({{ selectedUsers.length }}): </span>
            <el-tag v-for="(user, index) in selectedUsers" :key="user.id" closable class="mr-1 mb-1"
                    @close="removeUser(user)">
                {{ user.name }}
            </el-tag>
        </div>

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="visible = false">取消</el-button>
                <el-button type="primary" @click="handleConfirm">确定</el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElTree, ElTable } from 'element-plus'
import { getAllDeptList, getDeptUserList } from '/@/views/system/dept/api'
import { getAllCompanies } from '/@/api/company/index'
import XEUtils from 'xe-utils'

const props = defineProps({
    modelValue: {
        type: [String, Array],
        default: () => []
    },
    visible: {
        type: Boolean,
        default: false
    },
    title: {
        type: String,
        default: '选择人员'
    },
    multiple: {
        type: Boolean,
        default: true
    }
})

const emit = defineEmits(['update:visible', 'update:modelValue', 'confirm'])

const visible = computed({
    get: () => props.visible,
    set: (val) => emit('update:visible', val)
})

// 部门树相关
const deptTree = ref([])
const filterText = ref('')
const treeRef = ref<InstanceType<typeof ElTree>>()
const defaultProps = {
    children: 'children',
    label: 'name'
}

// 人员列表相关
const userList = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const currentDeptId = ref<string | null>(null)
const tableRef = ref<InstanceType<typeof ElTable>>()

// 分页
const pagination = reactive({
    current: 1,
    size: 20,
    total: 0
})

// 选中的用户
const selectedUsers = ref<any[]>([])

// 监听部门过滤
watch(filterText, (val) => {
    treeRef.value!.filter(val)
})

const filterNode = (value: string, data: any) => {
    if (!value) return true
    return data.name.includes(value)
}

// 加载部门树数据
const loadDeptTree = async () => {
    try {
        const [companyRes, deptRes] = await Promise.all([
            getAllCompanies(),
            getAllDeptList()
        ])

        console.log('API Response - Company:', companyRes)
        console.log('API Response - Dept:', deptRes)

        if (companyRes.code === 2000 && deptRes.code === 2000) {
            // 兼容可能的分页结构 data.data
            const companies = Array.isArray(companyRes.data) ? companyRes.data : companyRes.data?.data || []
            const depts = Array.isArray(deptRes.data) ? deptRes.data : deptRes.data?.data || []

            console.log('Processed List - Companies:', companies)
            console.log('Processed List - Depts:', depts)


            // 构造树形结构
            // 1. 先把部门转成树，按 company_belong_id 分组
            const deptParams = { parentKey: 'parent', strict: false }
            const resultTree: any[] = []

            // 遍历所有公司
            companies.forEach((comp: any) => {
                const compNode = {
                    id: `company_${comp.id}`, // 防止ID冲突
                    realId: comp.id,
                    name: comp.name || comp.shortname,
                    type: 'company',
                    children: [] as any[]
                }

                // 筛选出属于该公司的部门
                const companyDepts = depts.filter((d: any) => (d.company_belong === comp.id || d.company_belong_id === comp.id))
                // 转树
                const deptTree = XEUtils.toArrayTree(companyDepts, deptParams)
                compNode.children = deptTree

                resultTree.push(compNode)
            })

            console.log('Final Tree:', resultTree)
            deptTree.value = resultTree as any
        }
    } catch (error) {
        console.error('加载组织架构树失败:', error)
        ElMessage.error('加载组织架构数据失败')
    }
}

// 加载用户数据
const loadUserList = async () => {
    loading.value = true
    try {
        const params: any = {
            page: pagination.current,
            limit: pagination.size,
            search: searchKeyword.value
        }

        // 处理部门/公司筛选
        if (currentDeptId.value) {
            if (typeof currentDeptId.value === 'string' && currentDeptId.value.startsWith('company_')) {
                // 如果是公司节点
                params.company_belong_id = currentDeptId.value.replace('company_', '')
            } else {
                // 如果是部门节点
                params.dept = currentDeptId.value
            }
        }

        const res = await getDeptUserList(params)
        if (res.code === 2000) {
            userList.value = res.data
            pagination.total = res.total

            // 回显选中状态 (如果需要在单页内回显)
            // 注意：ElTable 的 reserve-selection 需要 row-key 配合
        }
    } catch (error) {
        console.error('加载用户列表失败:', error)
    } finally {
        loading.value = false
    }
}

// 部门点击
const handleNodeClick = (data: any) => {
    currentDeptId.value = data.id
    pagination.current = 1
    loadUserList()
}

// 搜索
const handleSearch = () => {
    pagination.current = 1
    loadUserList()
}

// 翻页
const handlePageChange = (val: number) => {
    pagination.current = val
    loadUserList()
}

// 表格选择变化
const handleSelectionChange = (selection: any[]) => {
    // 这里处理多选逻辑。
    // 由于使用了 reserve-selection，selection 包含了跨页的所有选中项
    // 注意：如果是单选模式，ElTable 还是会返回数组，需要手动处理
    if (!props.multiple && selection.length > 1) {
        // 单选模式强行只留最后一个
        const last = selection.pop()
        tableRef.value?.clearSelection()
        tableRef.value?.toggleRowSelection(last, true)
        selectedUsers.value = [last]
    } else {
        selectedUsers.value = selection
    }
}

// 移除已选标签
const removeUser = (user: any) => {
    tableRef.value?.toggleRowSelection(user, false)
    // 强制触发更新（有时 toggleRowSelection 不会触发 selection-change 如果不在当前页）
    const index = selectedUsers.value.findIndex(u => u.id === user.id)
    if (index > -1) {
        selectedUsers.value.splice(index, 1)
    }
}


// 初始化
watch(() => props.visible, (val) => {
    if (val) {
        // 打开时加载
        if (deptTree.value.length === 0) {
            loadDeptTree()
        }
        // 默认加载全部用户
        loadUserList()
        // 清空选中或根据 modelValue 回显 (这里简化处理，暂不根据 modelValue 反查用户信息，通常需要专门 ID->User 接口)
        selectedUsers.value = []
        tableRef.value?.clearSelection()
    }
})

const handleClose = () => {
    emit('update:visible', false)
}

const handleConfirm = () => {
    if (selectedUsers.value.length === 0) {
        ElMessage.warning('请选择人员')
        return
    }

    if (props.multiple) {
        emit('confirm', selectedUsers.value)
    } else {
        emit('confirm', selectedUsers.value[0])
    }

    emit('update:visible', false)
}
</script>

<style scoped lang="scss">
.mb-2 {
    margin-bottom: 10px;
}

.mt-2 {
    margin-top: 10px;
}

.mr-1 {
    margin-right: 5px;
}

.search-box {
    display: flex;
    align-items: center;
}

.selected-tags {
    padding: 0 20px;
    max-height: 100px;
    overflow-y: auto;

    .label {
        font-weight: bold;
        margin-right: 10px;
    }
}
</style>
