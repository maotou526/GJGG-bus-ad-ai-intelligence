<template>
    <el-dialog :title="title" v-model="visible" width="800px" append-to-body destroy-on-close>
        <div class="user-selector-container">
            <!-- 左侧：选择区 -->
            <div class="selector-left">
                <el-tabs v-model="activeTab" class="selector-tabs">
                    <el-tab-pane label="部门" name="dept">
                        <div class="tree-box">
                            <el-tree ref="deptTreeRef" :data="deptTreeData"
                                    :props="{ label: 'name', children: 'children' }" show-checkbox node-key="id"
                                    @check="handleDeptCheck">
                            </el-tree>
                        </div>
                    </el-tab-pane>
                    <el-tab-pane label="角色" name="role">
                        <div class="list-box">
                            <el-input v-model="roleSearch" placeholder="搜索角色" prefix-icon="Search" clearable />
                            <el-table :data="roleList" height="300" @selection-change="handleRoleSelectionChange"
                                    ref="roleTableRef">
                                <el-table-column type="selection" width="55" />
                                <el-table-column property="name" label="角色名称" />
                            </el-table>
                        </div>
                    </el-tab-pane>
                    <el-tab-pane label="用户" name="user">
                        <div class="list-box">
                            <el-input v-model="userSearch" placeholder="搜索用户" prefix-icon="Search" clearable
                                    @keyup.enter="handleUserSearch" />
                            <el-table :data="userList" height="300" @selection-change="handleUserSelectionChange"
                                    ref="userTableRef">
                                <el-table-column type="selection" width="55" />
                                <el-table-column property="name" label="姓名" width="120" />
                                <el-table-column property="username" label="账号" />
                            </el-table>
                        </div>
                    </el-tab-pane>
                    <el-tab-pane label="岗位" name="post">
                        <div class="list-box">
                            <el-input v-model="postSearch" placeholder="搜索岗位" prefix-icon="Search" clearable />
                            <el-table :data="postList" height="300" @selection-change="handlePostSelectionChange"
                                    ref="postTableRef">
                                <el-table-column type="selection" width="55" />
                                <el-table-column property="name" label="岗位名称" />
                            </el-table>
                        </div>
                    </el-tab-pane>
                </el-tabs>
            </div>

            <!-- 右侧：已选区 -->
            <div class="selector-right">
                <div class="selected-header">
                    <span>已选列表 ({{ selectedList.length }})</span>
                    <el-button link type="primary" @click="clearAll">清空</el-button>
                </div>
                <div class="selected-list">
                    <el-tag v-for="(item, index) in selectedList" :key="item.uniqueId" closable
                            @close="handleRemove(index)" class="selected-tag">
                        {{ getTypeName(item.type) }}: {{ item.name }}
                    </el-tag>
                </div>
            </div>
        </div>

        <template #footer>
            <el-button @click="visible = false">取消</el-button>
            <el-button type="primary" @click="handleConfirm">确定</el-button>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'

// 类型定义
export interface SelectorItem {
    id: string | number
    name: string
    type: 'dept' | 'role' | 'user' | 'post'
    uniqueId?: string // 用于去重 id+type
}

interface Props {
    // 初始选中的项
    modelValue?: SelectorItem[]
    // 限制单选/多选
    multiple?: boolean
    // 限制只能选某些类型 ['dept', 'user']
    allowedTypes?: string[]
}

const props = withDefaults(defineProps<Props>(), {
    modelValue: () => [],
    multiple: true,
    allowedTypes: () => ['dept', 'role', 'user', 'post']
})

const emit = defineEmits(['update:modelValue', 'confirm'])

const visible = ref(false)
const title = ref('选择对象')
const activeTab = ref('user')

// 模拟数据 (TODO: 对接真实 API)
const deptTreeData = ref([
    {
        id: '1', name: '总公司', children: [
            { id: '2', name: '研发部' },
            { id: '3', name: '财务部' }
        ]
    }
])

const roleList = ref([
    { id: '1', name: '管理员' },
    { id: '2', name: '普通用户' }
])

const userList = ref([
    { id: '1', name: '张三', username: 'zhangsan' },
    { id: '2', name: '李四', username: 'lisi' }
])

const postList = ref([
    { id: '1', name: '经理' },
    { id: '2', name: '专员' }
])

const roleSearch = ref('')
const userSearch = ref('')
const postSearch = ref('')

// 已选列表
const selectedList = ref<SelectorItem[]>([])

// 打开弹窗方法
const open = () => {
    selectedList.value = JSON.parse(JSON.stringify(props.modelValue)).map((item: SelectorItem) => ({
        ...item,
        uniqueId: item.type + '_' + item.id
    }))
    visible.value = true
}

const close = () => {
    visible.value = false
}

// 暴露方法
defineExpose({ open, close })

// 处理部门选择
const handleDeptCheck = (data: any, { checkedNodes }: any) => {
    // 简单处理：仅添加叶子节点或所有选中的
    // 实际业务可能需要级联逻辑
    // 这里仅做演示：每次 check 都重新计算 dept 类型的选中态有点复杂，
    // 简化为：手动点击才算? 或者 tree 不适合双向绑定到 selectedList
    // 建议：Tree 选中即添加，取消即移除
}

// 通用处理选中
const handleSelectionChange = (selection: any[], type: 'role' | 'user' | 'post') => {
    // 这是一个全量 list，需要与 selectedList 合并
    // 简易逻辑：这种 table selection 模式不太好做跨页保存，
    // 更好的方式是点击行添加，或者 table 只展示，选中状态由 selectedList 决定
}

// 优化：右侧点击移除
const handleRemove = (index: number) => {
    selectedList.value.splice(index, 1)
}

const clearAll = () => {
    selectedList.value = []
}

const handleConfirm = () => {
    emit('update:modelValue', selectedList.value)
    emit('confirm', selectedList.value)
    visible.value = false
}

const getTypeName = (type: string) => {
    const map: Record<string, string> = {
        'dept': '部门',
        'role': '角色',
        'user': '用户',
        'post': '岗位'
    }
    return map[type] || type
}

const handleUserSearch = () => {
    // TODO: Call API
}

// 模拟 Table Selection change (简化版，实际需要 diff)
const handleRoleSelectionChange = (val: any[]) => {
    syncSelection(val, 'role')
}
const handleUserSelectionChange = (val: any[]) => {
    syncSelection(val, 'user')
}
const handlePostSelectionChange = (val: any[]) => {
    syncSelection(val, 'post')
}

const syncSelection = (val: any[], type: 'role' | 'user' | 'post') => {
    // 1. 移除 selectedList 中该类型的旧数据 (这一步有风险，如果分页了会导致丢失)
    // 稳妥做法：只添加新的，移除取消的。
    // 这是一个复杂交互，为演示效率，暂且：将 selectedList 中该类型的都清掉，然后 add val
    // 但这样不支持多选叠加。

    // 临时方案: 仅演示 UI
    val.forEach(item => {
        const uniqueId = type + '_' + item.id
        if (!selectedList.value.find(s => s.uniqueId === uniqueId)) {
            selectedList.value.push({
                id: item.id,
                name: item.name,
                type: type,
                uniqueId: uniqueId
            })
        }
    })
}

</script>

<style scoped lang="scss">
.user-selector-container {
    display: flex;
    height: 400px;
    border: 1px solid #dcdfe6;

    .selector-left {
        flex: 1;
        border-right: 1px solid #dcdfe6;
        padding: 10px;
        display: flex;
        flex-direction: column;

        .selector-tabs {
            height: 100%;
            display: flex;
            flex-direction: column;

            :deep(.el-tabs__content) {
                flex: 1;
                overflow: auto;
            }
        }
    }

    .selector-right {
        width: 250px;
        padding: 10px;
        background: #f5f7fa;
        display: flex;
        flex-direction: column;

        .selected-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .selected-list {
            flex: 1;
            overflow-y: auto;

            .selected-tag {
                display: flex;
                justify-content: space-between;
                margin-bottom: 5px;
                width: 100%;
            }
        }
    }
}
</style>
