<template>
    <el-tree-select
        v-model="selectedValue"
        :data="treeData"
        :props="treeProps"
        :placeholder="placeholder"
        :disabled="disabled"
        :clearable="clearable"
        :filterable="filterable"
        :loading="loading"
        check-strictly
        node-key="id"
        style="width: 100%"
        @change="handleChange"
    />
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { request } from '/@/utils/service'

// Props
const props = withDefaults(
    defineProps<{
        modelValue?: string | number
        placeholder?: string
        disabled?: boolean
        clearable?: boolean
        filterable?: boolean
    }>(),
    {
        modelValue: '',
        placeholder: '请选择公司',
        disabled: false,
        clearable: true,
        filterable: true
    }
)

// Emits
const emit = defineEmits<{
    'update:modelValue': [value: string | number | undefined]
    change: [value: string | number | undefined, node: any]
}>()

// 选中值
const selectedValue = ref<string | number | undefined>(props.modelValue)

// 树形数据
const treeData = ref<any[]>([])
const loading = ref(false)

// 树形配置
const treeProps = {
    children: 'children',
    label: 'shortname',
    value: 'id',
    isLeaf: (data: any) => !data.hasChild
}

// 加载公司数据
const loadCompanyData = async () => {
    loading.value = true
    try {
        const res: any = await request({
            url: '/api/CompanyModelViewSet/all_company/',
            method: 'get'
        })
        if (res.data) {
            treeData.value = res.data
        }
    } catch (error) {
        console.error('加载公司数据失败:', error)
    } finally {
        loading.value = false
    }
}

// 查找节点
const findNode = (id: string | number, nodes: any[]): any => {
    for (const node of nodes) {
        if (node.id === id) return node
        if (node.children?.length) {
            const found = findNode(id, node.children)
            if (found) return found
        }
    }
    return null
}

// 值变化处理
const handleChange = (value: string | number | undefined) => {
    emit('update:modelValue', value)
    const node = value ? findNode(value, treeData.value) : null
    emit('change', value, node)
}

// 监听外部值变化
watch(
    () => props.modelValue,
    (newVal) => {
        selectedValue.value = newVal
    }
)

onMounted(() => {
    loadCompanyData()
})

// 暴露方法
defineExpose({
    refresh: loadCompanyData
})
</script>
