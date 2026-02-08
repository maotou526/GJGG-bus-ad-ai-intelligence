<template>
    <el-dialog v-model="visible" :title="dialogTitle" width="600px" @close="handleClose" append-to-body
            destroy-on-close>
        <el-form :model="form" label-width="100px">
            <!-- 岗位选择 -->
            <template v-if="selectorType === 'post'">
                <el-form-item label="岗位" required>
                    <el-select v-model="form.auditorId" placeholder="请选择岗位" filterable>
                        <el-option v-for="item in postList" :key="item.id" :label="item.name" :value="item.code" />
                    </el-select>
                </el-form-item>

                <el-form-item label="附加条件">
                    <el-radio-group v-model="form.condition">
                        <el-radio label="">无</el-radio>
                        <el-radio label="1">同一个部门</el-radio>
                        <el-radio label="2">同一个公司</el-radio>
                    </el-radio-group>
                </el-form-item>
            </template>

            <!-- 角色选择 -->
            <template v-if="selectorType === 'role'">
                <el-form-item label="角色" required>
                    <el-select v-model="form.auditorId" placeholder="请选择角色" filterable>
                        <el-option v-for="item in roleList" :key="item.id" :label="item.name" :value="item.code" />
                    </el-select>
                </el-form-item>

                <el-form-item label="附加条件">
                    <el-radio-group v-model="form.condition">
                        <el-radio label="">无</el-radio>
                        <el-radio label="1">同一个部门</el-radio>
                        <el-radio label="2">同一个公司</el-radio>
                    </el-radio-group>
                </el-form-item>
            </template>

            <!-- 用户选择 -->
            <template v-if="selectorType === 'user'">
                <el-form-item label="用户" required>
                    <el-select v-model="form.auditorId" placeholder="请选择用户" filterable>
                        <el-option v-for="item in userList" :key="item.id" :label="item.name" :value="item.id" />
                    </el-select>
                </el-form-item>
            </template>

            <!-- 上下级选择 -->
            <template v-if="selectorType === 'level'">
                <el-form-item label="上下级类型" required>
                    <el-radio-group v-model="form.condition">
                        <el-radio label="3">发起人上级</el-radio>
                        <el-radio label="4">发起人下级</el-radio>
                    </el-radio-group>
                </el-form-item>
            </template>

            <!-- 节点执行人 -->
            <template v-if="selectorType === 'node'">
                <el-form-item label="节点" required>
                    <el-select v-model="form.auditorId" placeholder="请选择节点">
                        <el-option v-for="item in nodeList" :key="item.id" :label="item.name" :value="item.id" />
                    </el-select>
                </el-form-item>
            </template>

            <!-- 表字段 -->
            <template v-if="selectorType === 'field'">
                <el-form-item label="字段名" required>
                    <el-input v-model="form.auditorId" placeholder="请输入字段名" />
                </el-form-item>

                <el-form-item label="字段说明">
                    <el-input v-model="form.auditorName" placeholder="请输入字段说明" />
                </el-form-item>
            </template>

            <!-- IOC注入 -->
            <template v-if="selectorType === 'ioc'">
                <el-form-item label="DI名称" required>
                    <el-input v-model="form.iocMethodName" placeholder="请输入注入方法" />
                </el-form-item>

                <el-form-item label="自定义参数">
                    <el-input v-model="form.cparam" placeholder="Json格式" />
                </el-form-item>

                <el-form-item label="过滤方式" required>
                    <el-radio-group v-model="form.iocFilterType">
                        <el-radio label="1">DI为审核人来源</el-radio>
                        <el-radio label="2">不包含DI人员</el-radio>
                        <el-radio label="3">合并DI人员</el-radio>
                    </el-radio-group>
                </el-form-item>
            </template>
        </el-form>

        <template #footer>
            <el-button @click="visible = false">取消</el-button>
            <el-button type="primary" @click="handleConfirm">确定</el-button>
        </template>
    </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoleApi } from '/@/api/role/index'
import { useUserApi } from '/@/api/user/index'

interface AuditorForm {
    type: string
    auditorId: string
    auditorName: string
    condition?: string
    cparam?: string
    iocMethodName?: string
    iocFilterType?: string
}

const visible = ref(false)
const selectorType = ref<string>('post') // post, role, user, level, node, field, ioc
const form = reactive<AuditorForm>({
    type: '1',
    auditorId: '',
    auditorName: '',
    condition: '',
    cparam: '',
    iocMethodName: '',
    iocFilterType: '1'
})

const postList = ref<any[]>([])
const roleList = ref<any[]>([])
const userList = ref<any[]>([])
const nodeList = ref<any[]>([])

const dialogTitle = computed(() => {
    const titles: Record<string, string> = {
        post: '添加岗位',
        role: '添加角色',
        user: '添加人员',
        level: '添加上下级',
        node: '添加节点执行人',
        field: '添加表字段',
        ioc: 'IOC注入添加'
    }
    return titles[selectorType.value] || '添加审核者'
})

const emit = defineEmits<{
    confirm: [data: any]
}>()

// 打开对话框
const open = (type: string, nodes?: any[]) => {
    selectorType.value = type

    if (type === 'post') {
        ElMessage.warning('岗位功能暂未实现')
        return
    }

    // 设置类型编号
    const typeMap: Record<string, string> = {
        post: '1',
        role: '2',
        user: '3',
        level: '4',
        field: '5',
        node: '6',
        ioc: '8'
    }
    form.type = typeMap[type] || '1'

    // 重置表单
    form.auditorId = ''
    form.auditorName = ''
    form.condition = ''
    form.cparam = ''
    form.iocMethodName = ''
    form.iocFilterType = '1'

    // 加载数据
    if (type === 'role') {
        loadRoleList()
    } else if (type === 'user') {
        loadUserList()
    } else if (type === 'node' && nodes) {
        nodeList.value = nodes.filter(n => n.type !== 'startround' && n.type !== 'endround')
    }

    visible.value = true
}

// 加载岗位列表
const loadPostList = async () => {
    try {

    } catch (error) {
        console.error('加载岗位列表失败:', error)
    }
}

// 加载角色列表
const loadRoleList = async () => {
    try {
        const res = await useRoleApi().getRole({
            limit: 9999,
            status: true
        })

        if (res && res.data) {
            roleList.value = res.data.map((item: any) => ({
                id: item.id,
                code: item.key, // 使用key作为code
                name: item.name
            }))
        }
    } catch (error) {
        console.error('加载角色列表失败:', error)
    }
}

// 加载用户列表
const loadUserList = async () => {
    try {
        const res = await useUserApi().getUser({
            limit: 9999,
            status: true
        })
        if (res && res.data) {
            userList.value = res.data.map((item: any) => ({
                id: item.id,
                name: item.name || item.username
            }))
        }
    } catch (error) {
        console.error('加载用户列表失败:', error)
    }
}

// 确认
const handleConfirm = () => {
    // IOC类型需要检查方法名
    if (selectorType.value === 'ioc') {
        if (!form.iocMethodName) {
            ElMessage.warning('请选择或输入IOC方法名')
            return
        }
    } else if (!form.auditorId && selectorType.value !== 'level') {
        ElMessage.warning('请选择或填写必填项')
        return
    }

    // 构造审核者数据
    let auditorName = form.auditorName
    let auditorId = form.auditorId

    if (selectorType.value === 'post') {
        const post = postList.value.find(p => p.code === form.auditorId)
        auditorName = post?.name || form.auditorId
    } else if (selectorType.value === 'role') {
        const role = roleList.value.find(r => r.code === form.auditorId)
        auditorName = role?.name || form.auditorId
    } else if (selectorType.value === 'user') {
        const user = userList.value.find(u => u.id === form.auditorId)
        auditorName = user?.name || form.auditorId
    } else if (selectorType.value === 'level') {
        const levelMap: Record<string, string> = {
            '3': '发起人上级',
            '4': '发起人下级'
        }
        auditorName = levelMap[form.condition || ''] || '上下级'
        auditorId = 'level_' + form.condition
    } else if (selectorType.value === 'node') {
        const node = nodeList.value.find(n => n.id === form.auditorId)
        auditorName = node?.name || form.auditorId
    } else if (selectorType.value === 'ioc') {
        // IOC格式: "方法名|过滤类型"
        auditorId = `${form.iocMethodName}|${form.iocFilterType || '1'}`
        // auditorName格式与力软一致: 【方法名】注入cparam:参数
        auditorName = `【${form.iocMethodName}】注入` + (form.cparam ? `cparam:${form.cparam}` : '')
    }

    const data = {
        id: learun.newGuid(), // 生成UUID
        type: form.type,
        auditorId: auditorId,
        auditorName: auditorName,
        condition: form.condition,
        cparam: form.cparam
    }

    emit('confirm', data)
    visible.value = false
}

const handleClose = () => {
    visible.value = false
}

defineExpose({
    open
})
</script>

<style scoped lang="scss">
.el-form {
    padding: 20px 20px 0;
}
</style>
