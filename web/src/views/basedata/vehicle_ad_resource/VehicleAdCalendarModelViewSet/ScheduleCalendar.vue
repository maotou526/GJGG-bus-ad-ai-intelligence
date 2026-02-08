<template>
  <div class="schedule-calendar" v-loading="loading">
    <!-- Summary Section -->
    <div class="summary-panel">
      <div class="summary-item">
        <div class="label">车辆总数</div>
        <div class="value">{{ vehicles.length }}</div>
      </div>
      <div class="summary-item">
        <div class="label">预订中</div>
        <div class="value reserved">{{ reservedCount }}</div>
      </div>
      <div class="summary-item">
        <div class="label">已上刊</div>
        <div class="value active">{{ activeCount }}</div>
      </div>
      <div class="summary-item">
        <div class="label">到期未下刊</div>
        <div class="value expired">{{ expiredCount }}</div>
      </div>
      <div class="summary-item">
        <div class="label">已下刊</div>
        <div class="value finished">{{ finishedCount }}</div>
      </div>
      <div class="summary-item">
        <div class="label">排期占用率</div>
        <div class="value">{{ occupancyRate }}%</div>
      </div>
    </div>

    <!-- Controls -->

    <!-- Gantt Chart -->
    <div class="gantt-container" ref="ganttContainer">
      <!-- Header Row (Days) -->
      <div class="gantt-header" :style="{ width: totalWidth + 'px' }">
        <div class="gantt-col vehicle-col">车辆 / 时间轴</div>
        <div 
          v-for="day in timeAxis" 
          :key="day.dateStr" 
          class="gantt-col day-col"
          :class="{ today: day.isToday }"
          :style="{ width: colWidth + 'px' }"
          @click="openDayDrawer(day.dateStr)"
        >
          <div class="day-label">{{ day.label }}</div>
          <div v-if="getDayCount(day.dateStr) > 0" class="day-count">{{ getDayCount(day.dateStr) }}个广告</div>
        </div>
      </div>

      <!-- Vehicle Rows -->
      <div class="gantt-body" :style="{ width: totalWidth + 'px' }">
        <div v-for="vehicle in vehicles" :key="vehicle.id" class="gantt-row">
          <div class="gantt-col vehicle-col">
            <div class="plate">{{ vehicle.plateNumber }}</div>
            <div class="model">{{ vehicle.route }}</div>
          </div>
          <div class="gantt-timeline" @mousemove="handleMouseMove" @mouseup="handleMouseUp" @mouseleave="handleMouseUp">
            <!-- Grid lines -->
            <div 
              v-for="day in timeAxis" 
              :key="day.dateStr" 
              class="grid-cell"
              :style="{ width: colWidth + 'px' }"
            ></div>
            
            <!-- Schedule Bars -->
            <div 
              v-for="schedule in getSchedulesForVehicle(vehicle.id)" 
              :key="schedule.id"
              class="schedule-bar"
              :class="[
                schedule.status, 
                { 
                  dragging: dragState.scheduleId === schedule.id,
                  conflict: isConflict(schedule)
                }
              ]"
              :style="getBarStyle(schedule)"
              @mousedown.stop="handleMouseDown($event, schedule)"
              @click.stop="$emit('view', schedule)"
            >
              <el-tooltip :content="getTooltipContent(schedule)" placement="top">
                <div class="bar-content">
                  <span class="bar-text">{{ getAdvertiserWithDate(schedule) }}</span>
                  <span v-if="schedule.status === 'reserved'" class="resize-handle"></span>
                </div>
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 按天排期列表弹窗：样式与“广告投放详情”一致，展示车位资源明细 -->
    <el-dialog
      v-model="dayDrawerVisible"
      :title="dayDrawerTitle"
      width="1400px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div v-loading="dayDetailLoading">
        <template v-if="dayDetailPositions.length > 0">
          <el-divider content-position="left">
            广告排期 ({{ dayDetailPositions.length }}个)
          </el-divider>
          <el-table
            :data="dayDetailPositions"
            border
            stripe
            max-height="700"
            style="width: 100%"
          >
            <el-table-column
              type="index"
              label="序号"
              width="60"
              align="center"
              fixed="left"
            />
            <el-table-column
              prop="resourceCode"
              label="资源编码"
              width="150"
              show-overflow-tooltip
            />
            <el-table-column
              prop="vehiclePlate"
              label="车牌号"
              width="120"
            />
            <el-table-column
              prop="vehicleNo"
              label="车辆自编号"
              width="120"
            />
            <el-table-column
              prop="mediaTypeName"
              label="媒体类型"
              width="120"
            />
            <el-table-column
              prop="roadlineName"
              label="线路名称"
              width="150"
              show-overflow-tooltip
            />
            <el-table-column
              prop="roadlineCompanyName"
              label="营运公司"
              width="150"
              show-overflow-tooltip
            />

            <el-table-column
              prop="actualOnDate"
              label="实际上刊日期"
              width="130"
              align="center"
            >
              <template #default="{ row }">
                {{ row.actualOnDate || '-' }}
              </template>
            </el-table-column>
            <el-table-column
              prop="reservedStartDate"
              label="预订开始日期"
              width="130"
              align="center"
            />
            <el-table-column
              prop="reservedEndDate"
              label="预订结束日期"
              width="130"
              align="center"
            />
            <el-table-column
              prop="actualOffDate"
              label="实际下刊日期"
              width="130"
              align="center"
            >
              <template #default="{ row }">
                {{ row.actualOffDate || '-' }}
              </template>
            </el-table-column>
            <el-table-column
              prop="resourceStatusDisplay"
              label="资源状态"
              width="100"
              align="center"
              fixed="right"
            >
              <template #default="{ row }">
                <el-tag :type="getResourceStatusTagType(row.resourceStatusDisplay)" size="small">
                  {{ row.resourceStatusDisplay }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </template>
        <el-empty
          v-else-if="!dayDetailLoading"
          description="当日暂无排期"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { type AdSchedule, type Vehicle, useAdScheduleStore } from '/@/stores/adSchedule'
import { ElMessage } from 'element-plus'
import { request } from '/@/utils/service'

const props = defineProps<{
  vehicles: Vehicle[]
  schedules: AdSchedule[]
  loading?: boolean
}>()

const emit = defineEmits<{
  view: [schedule: AdSchedule]
  update: [schedule: AdSchedule]
}>()
const store = useAdScheduleStore()

// 将外部传入的数据同步到 store，供冲突检查和抽屉等逻辑使用
watch(
  () => ({ vehicles: props.vehicles, schedules: props.schedules }),
  (val) => {
    store.setData(val.vehicles || [], val.schedules || [])
  },
  { deep: true, immediate: true }
)

// State
const viewMode = ref<'day' | 'week' | 'month'>('month')
const currentDate = ref(new Date())
const ganttContainer = ref<HTMLElement | null>(null)
const containerWidth = ref(0)

// Drag State
const dragState = reactive({
  isDragging: false,
  scheduleId: '',
  startX: 0,
  originalStart: 0, // timestamp
  originalEnd: 0, // timestamp
  currentOffsetDays: 0
})

// Constants
const COL_WIDTHS = {
  day: 100,
  week: 60,
  month: 49
}

const colWidth = computed(() => COL_WIDTHS[viewMode.value])

// Time Axis Computation
const timeRange = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const date = currentDate.value.getDate()

  let start: Date, end: Date, days: number

  if (viewMode.value === 'month') {
    start = new Date(year, month, 1)
    end = new Date(year, month + 1, 0)
    days = end.getDate()
  } else if (viewMode.value === 'week') {
    const dayOfWeek = currentDate.value.getDay() || 7
    start = new Date(year, month, date - dayOfWeek + 1)
    end = new Date(start)
    end.setDate(start.getDate() + 13) // Show 2 weeks
    days = 14
  } else { // day
    start = new Date(year, month, date - 2) // Start 2 days ago
    end = new Date(start)
    end.setDate(start.getDate() + 6) // Show 1 week total
    days = 7
  }
  return { start, end, days }
})

const timeAxis = computed(() => {
  const { start, days } = timeRange.value
  const axis = []
  const today = new Date()
  
  for (let i = 0; i < days; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    axis.push({
      dateStr: formatDate(d),
      label: viewMode.value === 'month' ? `${d.getDate()}` : `${d.getMonth()+1}/${d.getDate()}`,
      isToday: d.toDateString() === today.toDateString(),
      obj: d
    })
  }
  return axis
})

const totalWidth = computed(() => {
  const calculatedWidth = timeAxis.value.length * colWidth.value + 120 // + vehicle col width
  // 确保甘特图至少占满容器宽度
  return Math.max(calculatedWidth, containerWidth.value || calculatedWidth)
})

const dateDisplay = computed(() => {
  const { start, end } = timeRange.value
  return `${formatDate(start)} ~ ${formatDate(end)}`
})

// Summary Statistics
const activeCount = computed(() => props.schedules.filter(s => s.status === 'active').length)
const reservedCount = computed(() => props.schedules.filter(s => s.status === 'reserved').length)
const finishedCount = computed(() => props.schedules.filter(s => s.status === 'finished').length)
// 到期未下刊：判断条件为 off_air_date > scheduled_end_date
const expiredCount = computed(() => {
  return props.schedules.filter(s => {
    // 如果 schedule 对象有 off_air_date 和 scheduled_end_date 字段
    const schedule = s as any
    if (schedule.off_air_date && schedule.scheduled_end_date) {
      return schedule.off_air_date > schedule.scheduled_end_date
    }
    return false
  }).length
})
const occupancyRate = computed(() => {
  if (props.vehicles.length === 0) return 0
  // Simple calculation: % of vehicles with active ads
  const activeVehicleIds = new Set(props.schedules.filter(s => s.status === 'active').map(s => s.vehicleId))
  return Math.round((activeVehicleIds.size / props.vehicles.length) * 100)
})

// Helpers
const formatDate = (d: Date) => {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 格式化日期为简洁格式（MM-DD）
const formatDateShort = (d: Date) => {
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${month}-${day}`
}

// 获取广告名称和日期的组合显示
const getAdvertiserWithDate = (schedule: AdSchedule) => {
  let sStart = new Date(schedule.startDate)
  let sEnd = new Date(schedule.endDate)
  if (dragState.isDragging && dragState.scheduleId === schedule.id) {
    sStart.setDate(sStart.getDate() + dragState.currentOffsetDays)
    sEnd.setDate(sEnd.getDate() + dragState.currentOffsetDays)
  }
  const startStr = formatDateShort(sStart)
  const endStr = formatDateShort(sEnd)
  return `${schedule.advertiser} (${startStr}~${endStr})`
}

const changeDate = (delta: number) => {
  const d = new Date(currentDate.value)
  if (viewMode.value === 'month') {
    d.setMonth(d.getMonth() + delta)
  } else if (viewMode.value === 'week') {
    d.setDate(d.getDate() + delta * 7)
  } else {
    d.setDate(d.getDate() + delta)
  }
  currentDate.value = d
}

const getSchedulesForVehicle = (vehicleId: string) => {
  const { start, end } = timeRange.value
  return props.schedules.filter(s => {
    if (s.vehicleId !== vehicleId) return false
    
    // Calculate effective dates (considering drag)
    let sStart = new Date(s.startDate)
    let sEnd = new Date(s.endDate)
    
    if (dragState.isDragging && dragState.scheduleId === s.id) {
      sStart.setDate(sStart.getDate() + dragState.currentOffsetDays)
      sEnd.setDate(sEnd.getDate() + dragState.currentOffsetDays)
    }

    return sStart <= end && sEnd >= start
  })
}

const getBarStyle = (schedule: AdSchedule) => {
  const { start, end } = timeRange.value
  
  let sStart = new Date(schedule.startDate)
  let sEnd = new Date(schedule.endDate)
  
  // Apply drag offset
  if (dragState.isDragging && dragState.scheduleId === schedule.id) {
    sStart.setDate(sStart.getDate() + dragState.currentOffsetDays)
    sEnd.setDate(sEnd.getDate() + dragState.currentOffsetDays)
  }

  // Clip to view range
  const visibleStart = sStart < start ? start : sStart
  const visibleEnd = sEnd > end ? end : sEnd
  
  if (visibleStart > visibleEnd) return { display: 'none' }

  const diffDays = (visibleEnd.getTime() - visibleStart.getTime()) / (1000 * 3600 * 24) + 1
  const startOffset = (visibleStart.getTime() - start.getTime()) / (1000 * 3600 * 24)
  
  const left = startOffset * colWidth.value
  const width = diffDays * colWidth.value - 4

  return {
    left: `${left}px`,
    width: `${width}px`
  }
}

const getTooltipContent = (schedule: AdSchedule) => {
  let sStart = new Date(schedule.startDate)
  let sEnd = new Date(schedule.endDate)
  if (dragState.isDragging && dragState.scheduleId === schedule.id) {
    sStart.setDate(sStart.getDate() + dragState.currentOffsetDays)
    sEnd.setDate(sEnd.getDate() + dragState.currentOffsetDays)
  }
  return `${schedule.advertiser}: ${formatDate(sStart)} ~ ${formatDate(sEnd)}`
}

const isConflict = (schedule: AdSchedule) => {
  // If dragging, check conflict with temp dates
  if (dragState.isDragging && dragState.scheduleId === schedule.id) {
    const sStart = new Date(schedule.startDate)
    const sEnd = new Date(schedule.endDate)
    sStart.setDate(sStart.getDate() + dragState.currentOffsetDays)
    sEnd.setDate(sEnd.getDate() + dragState.currentOffsetDays)
    
    // Create temp object
    const tempSchedule = {
      ...schedule,
      startDate: formatDate(sStart),
      endDate: formatDate(sEnd)
    }
    return store.checkConflict(tempSchedule)
  }
  return store.checkConflict(schedule)
}

const getVehicle = (id: string) => store.getVehicleById(id)

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    reserved: 'warning',
    active: 'success',
    finished: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    reserved: '预订中',
    active: '已上刊',
    finished: '已下刊'
  }
  return map[status] || status
}

// 根据资源状态显示文本返回对应的 el-tag type，与摘要面板颜色保持一致
const getResourceStatusTagType = (statusDisplay: string) => {
  if (!statusDisplay) return 'info'
  const status = String(statusDisplay).trim()
  
  // 预订 -> warning (橙色 #e6a23c) - 对应 reserved
  if (status === '预订') return 'warning'
  // 在刊 -> success (绿色 #67c23a) - 对应 active
  if (status === '在刊') return 'success'
  // 下刊 -> info (灰色 #909399) - 对应 finished
  if (status === '下刊') return 'info'
  // 到期未下刊 -> danger (红色) - 对应 expired
  if (status === '到期未下刊') return 'danger'
  // 空闲 -> info (默认灰色)
  if (status === '空闲') return 'info'
  // 维修中 -> warning (橙色)
  if (status === '维修中') return 'warning'
  // 不可用 -> danger (红色)
  if (status === '不可用') return 'danger'
  
  return 'info'
}

const isScheduleOnDate = (schedule: AdSchedule, dateStr: string) => {
  return schedule.startDate <= dateStr && schedule.endDate >= dateStr
}

const dayCountMap = computed(() => {
  const map = new Map<string, number>()
  for (const day of timeAxis.value) {
    const count = props.schedules.reduce((acc, s) => acc + (isScheduleOnDate(s, day.dateStr) ? 1 : 0), 0)
    map.set(day.dateStr, count)
  }
  return map
})

const getDayCount = (dateStr: string) => {
  return dayCountMap.value.get(dateStr) || 0
}

const dayDrawerVisible = ref(false)
const selectedDateStr = ref('')

// 当天排期对应的车位资源明细（与“广告投放详情”弹窗字段一致）
const dayDetailPositions = ref<any[]>([])
const dayDetailLoading = ref(false)

const openDayDrawer = async (dateStr: string) => {
  selectedDateStr.value = dateStr
  dayDrawerVisible.value = true
  await nextTick()
  loadDayDetailPositions()
}

const dayDrawerTitle = computed(() => {
  return selectedDateStr.value ? `${selectedDateStr.value} 排期列表` : '排期列表'
})

const dayDrawerSchedules = computed(() => {
  if (!selectedDateStr.value) return []
  return props.schedules.filter(s => isScheduleOnDate(s, selectedDateStr.value))
})

// 根据当天的排期记录，批量查询车位资源明细
const loadDayDetailPositions = async () => {
  const schedules = dayDrawerSchedules.value as any[]
  if (!schedules.length) {
    dayDetailPositions.value = []
    return
  }

  dayDetailLoading.value = true
  dayDetailPositions.value = []

  // 按 vehicleId + bookingOrderId 去重，避免重复请求
  const pairMap = new Map<string, { vehicleId: string; bookingOrderId: string }>()
  for (const s of schedules) {
    const vehicleId = s.vehicleId
    let bookingOrderId = (s as any).bookingOrderId
    if (!bookingOrderId && s.id && String(s.id).includes('_')) {
      bookingOrderId = String(s.id).split('_')[1]
    }
    if (!vehicleId || !bookingOrderId) continue
    const key = `${vehicleId}_${bookingOrderId}`
    if (!pairMap.has(key)) {
      pairMap.set(key, { vehicleId, bookingOrderId })
    }
  }

  const positions: any[] = []

  try {
    for (const { vehicleId, bookingOrderId } of pairMap.values()) {
      const res: any = await request({
        url: '/api/VehicleAdResourceModelViewSet/get_positions_by_booking/',
        method: 'get',
        params: {
          vehicle_id: vehicleId,
          booking_order_id: bookingOrderId,
        },
      })

      if (res.code === 2000 && res.data && Array.isArray(res.data.positions)) {
        positions.push(...res.data.positions)
      }
    }

    dayDetailPositions.value = positions
  } catch (error: any) {
    ElMessage.error(error?.message || '获取排期明细失败')
  } finally {
    dayDetailLoading.value = false
  }
}

// Drag Handlers
const handleMouseDown = (e: MouseEvent, schedule: AdSchedule) => {
  // Only allow dragging reserved items
  if (schedule.status !== 'reserved') return

  dragState.isDragging = true
  dragState.scheduleId = schedule.id
  dragState.startX = e.clientX
  dragState.originalStart = new Date(schedule.startDate).getTime()
  dragState.originalEnd = new Date(schedule.endDate).getTime()
  dragState.currentOffsetDays = 0
}

const handleMouseMove = (e: MouseEvent) => {
  if (!dragState.isDragging) return
  
  const diffX = e.clientX - dragState.startX
  const diffDays = Math.round(diffX / colWidth.value)
  
  if (diffDays !== dragState.currentOffsetDays) {
    dragState.currentOffsetDays = diffDays
  }
}

const handleMouseUp = () => {
  if (!dragState.isDragging) return
  
  if (dragState.currentOffsetDays !== 0) {
    // Commit change
    const schedule = props.schedules.find(s => s.id === dragState.scheduleId)
    if (schedule) {
      const sStart = new Date(schedule.startDate)
      const sEnd = new Date(schedule.endDate)
      sStart.setDate(sStart.getDate() + dragState.currentOffsetDays)
      sEnd.setDate(sEnd.getDate() + dragState.currentOffsetDays)
      
      const newSchedule = {
        ...schedule,
        startDate: formatDate(sStart),
        endDate: formatDate(sEnd)
      }
      
      // Check conflict before updating
      if (store.checkConflict(newSchedule)) {
        ElMessage.error('排期冲突，调整失败')
      } else {
        // Emit update event to parent component
        emit('update', newSchedule)
        ElMessage.success('排期调整成功')
      }
    }
  }

  // Reset
  dragState.isDragging = false
  dragState.scheduleId = ''
  dragState.currentOffsetDays = 0
}

// Global mouse up listener to catch drops outside component
const handleGlobalMouseUp = () => {
  if (dragState.isDragging) handleMouseUp()
}

// 更新容器宽度
const updateContainerWidth = () => {
  if (ganttContainer.value) {
    containerWidth.value = ganttContainer.value.offsetWidth
  }
}

// 监听容器引用变化
watch(ganttContainer, (newVal) => {
  if (newVal) {
    nextTick(() => {
      updateContainerWidth()
    })
  }
}, { immediate: true })

onMounted(() => {
  window.addEventListener('mouseup', handleGlobalMouseUp)
  updateContainerWidth()
  // 监听窗口大小变化
  window.addEventListener('resize', updateContainerWidth)
  // 延迟更新一次，确保 DOM 完全渲染
  setTimeout(updateContainerWidth, 100)
})

onUnmounted(() => {
  window.removeEventListener('mouseup', handleGlobalMouseUp)
  window.removeEventListener('resize', updateContainerWidth)
})
</script>

<style scoped>
.schedule-calendar {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background: white;
  display: flex;
  flex-direction: column;
}

/* Summary Panel */
.summary-panel {
  display: flex;
  padding: 15px 20px;
  background: #fcfcfc;
  border-bottom: 1px solid #ebeef5;
  gap: 40px;
  flex-wrap: wrap;
}
.summary-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.summary-item .label {
  font-size: 12px;
  color: #909399;
}
.summary-item .value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
}
.summary-item .value.active { color: #67c23a; }
.summary-item .value.reserved { color: #e6a23c; }
.summary-item .value.finished { color: #909399; }
.summary-item .value.expired { color: #f56c6c; }

/* Header */
.calendar-header {
  padding: 10px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ebeef5;
}
.left-controls {
  display: flex;
  gap: 15px;
  align-items: center;
}
.date-display {
  width: 220px;
  text-align: center;
  color: #606266;
}

/* Legend */
.legend {
  display: flex;
  gap: 15px;
}
.legend-item {
  display: flex;
  align-items: center;
  font-size: 12px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 5px;
  border: 1px solid transparent;
}
.dot.active { background: #67c23a; }
.dot.reserved { 
  background: rgba(230, 162, 60, 0.3);
  border-color: #e6a23c;
  border-style: dashed;
}
.dot.finished { background: #909399; }
.dot.conflict { background: #f56c6c; }

/* Gantt Chart */
.gantt-container {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
  position: relative;
  user-select: none; /* Prevent text selection during drag */
  min-height: 570px;
  max-height: calc(100vh - 400px);
  width: 100%;
}

.gantt-header {
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  position: sticky;
  top: 0;
  z-index: 20;
  min-width: 100%;
  width: 100%;
}

.gantt-body {
  min-width: 100%;
  width: 100%;
}

.gantt-col {
  flex-shrink: 0;
  border-right: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
}

.vehicle-col {
  width: 120px;
  position: sticky;
  left: 0;
  background: #f5f7fa;
  z-index: 30;
  flex-direction: column;
  align-items: flex-start;
  padding-left: 10px;
  border-right: 2px solid #dcdfe6;
}
.gantt-row .vehicle-col {
  background: #fff;
}

.day-col {
  font-size: 12px;
  flex-direction: column;
  gap: 2px;
  cursor: pointer;
}
.day-col.today {
  background: #ecf5ff;
  color: #409eff;
  font-weight: bold;
}

.day-label {
  line-height: 14px;
}

.day-count {
  font-size: 11px;
  color: #909399;
  line-height: 12px;
}

.gantt-row {
  display: flex;
  border-bottom: 1px solid #ebeef5;
  height: 50px;
}

.gantt-timeline {
  display: flex;
  position: relative;
  height: 100%;
}

.grid-cell {
  height: 100%;
  border-right: 1px solid #f2f6fc;
  flex-shrink: 0;
}

/* Bars */
.schedule-bar {
  position: absolute;
  top: 10px;
  height: 30px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  padding: 0 5px;
  cursor: pointer;
  overflow: hidden;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: opacity 0.2s, top 0.2s, box-shadow 0.2s;
  z-index: 10;
}

.schedule-bar.active { 
  background: #67c23a; 
  color: white;
}

.schedule-bar.reserved { 
  background: rgba(230, 162, 60, 0.2); 
  border: 1px dashed #e6a23c;
  color: #e6a23c;
  cursor: grab;
}
.schedule-bar.reserved:active {
  cursor: grabbing;
}

.schedule-bar.finished { 
  background: #909399; 
  color: white;
  opacity: 0.6;
}

.schedule-bar.dragging {
  opacity: 0.8;
  z-index: 50;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  transform: scale(1.02);
}

.schedule-bar.conflict {
  background: #f56c6c !important;
  border: 1px solid #f56c6c !important;
  color: white !important;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.bar-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.bar-text {
  overflow: hidden;
  text-overflow: ellipsis;
}

.drawer-vehicle .plate {
  font-weight: 600;
}
.drawer-vehicle .sub {
  font-size: 12px;
  color: #909399;
}
</style>
