<template>
  <el-date-picker
    v-model="internalValue"
    type="daterange"
    :range-separator="rangeSeparator"
    :start-placeholder="startPlaceholder"
    :end-placeholder="endPlaceholder"
    :format="format"
    :value-format="valueFormat"
    :disabled-date="disabledDate"
    :disabled="disabled"
    :size="size"
    :class="className"
    :style="style"
    @change="handleChange"
    @blur="handleBlur"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  modelValue?: [string, string] | null
  rangeSeparator?: string
  startPlaceholder?: string
  endPlaceholder?: string
  format?: string
  valueFormat?: string
  disabled?: boolean
  size?: 'large' | 'default' | 'small'
  className?: string
  style?: string | Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  rangeSeparator: '至',
  startPlaceholder: '开始日期',
  endPlaceholder: '结束日期',
  format: 'YYYY-MM-DD',
  valueFormat: 'YYYY-MM-DD',
  disabled: false,
  size: 'default',
  className: '',
  style: () => ({})
})

const emit = defineEmits<{
  'update:modelValue': [value: [string, string] | null]
  'change': [value: [string, string] | null]
  'blur': [event: FocusEvent]
}>()

// 内部值
const internalValue = ref<[string, string] | null>(props.modelValue || null)

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  internalValue.value = newVal || null
}, { immediate: true })

// 获取月份的第一天
const getMonthFirstDay = (date: Date): Date => {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

// 获取月份的最后一天
const getMonthLastDay = (date: Date): Date => {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0)
}

const handlePanelChange = (value: [string, string] | null) => {
  console.log('处理面板变化', value);
}
// 禁用日期函数：确保开始和结束日期不能跨月
const disabledDate = (time: Date) => {
  // 如果还没有选择开始日期，不禁用任何日期
  if (!internalValue.value || !internalValue.value[0]) {
    return false
  }
  
  // 如果已经选择了完整的日期范围，需要检查重新选择时是否跨月
  if (internalValue.value[0] && internalValue.value[1]) {
    const startDate = new Date(internalValue.value[0])
    const startYear = startDate.getFullYear()
    const startMonth = startDate.getMonth()
    
    const timeYear = time.getFullYear()
    const timeMonth = time.getMonth()
    
    // 如果重新选择的日期与已选择的开始日期不在同一个月，则禁用
    // 这样可以防止用户选择跨月的日期范围
    if (timeYear !== startYear || timeMonth !== startMonth) {
      return true
    }
    
    return false
  }
  
  // 如果只选择了开始日期，限制结束日期只能选择同一个月内的日期
  if (internalValue.value[0] && !internalValue.value[1]) {
    const startDate = new Date(internalValue.value[0])
    const startYear = startDate.getFullYear()
    const startMonth = startDate.getMonth()
    const startDay = startDate.getDate()
    
    const timeYear = time.getFullYear()
    const timeMonth = time.getMonth()
    const timeDay = time.getDate()
    
    // 禁用不在同一年同一月的日期（核心限制：不能跨月）
    if (timeYear !== startYear || timeMonth !== startMonth) {
      return true
    }
    
    // 禁用早于开始日期的日期
    if (timeDay < startDay) {
      return true
    }
    
    return false
  }
  
  return false
}

// 验证日期区间是否跨月
const validateTimeRange = (value: [string, string] | null): boolean => {
  if (!value || !value[0] || !value[1]) {
    return true // 空值视为有效
  }
  
  const start = new Date(value[0])
  const end = new Date(value[1])
  
  const startMonth = start.getMonth()
  const startYear = start.getFullYear()
  const endMonth = end.getMonth()
  const endYear = end.getFullYear()
  
  // 检查是否跨月
  if (startMonth !== endMonth || startYear !== endYear) {
    return false
  }
  
  // 检查开始日期是否早于或等于结束日期
  if (start > end) {
    return false
  }
  
  return true
}

// 处理值变化
const handleChange = (value: [string, string] | null) => {
  // 如果选择了完整的日期范围，验证是否跨月
  if (value && value[0] && value[1]) {
    // 验证日期区间是否跨月
    if (!validateTimeRange(value)) {
      ElMessage.warning('日期区间不能跨月，且开始日期必须早于或等于结束日期，请重新选择')
      internalValue.value = null
      emit('update:modelValue', null)
      emit('change', null)
      return
    }
  }
  
  internalValue.value = value
  emit('update:modelValue', value)
  emit('change', value)
}

// 处理失焦事件
const handleBlur = (event: FocusEvent) => {
  emit('blur', event)
}

// 暴露方法供父组件调用
defineExpose({
  clear: () => {
    internalValue.value = null
    emit('update:modelValue', null)
    emit('change', null)
  },
  validate: () => {
    return validateTimeRange(internalValue.value)
  }
})
</script>

<style scoped>
/* 组件样式 */
</style>

