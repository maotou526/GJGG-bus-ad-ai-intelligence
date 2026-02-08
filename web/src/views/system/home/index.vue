<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-800">数据概览</h1>
      <el-date-picker v-model="selectedDate" type="date" placeholder="选择日期" format="YYYY-MM-DD"
        value-format="YYYY-MM-DD" size="default" @change="handleDateChange" />
    </div>

    <!-- 关键指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <div v-for="(metric, index) in keyMetrics" :key="index" v-loading="loading"
        :class="`bg-gradient-to-br ${metric.gradientBg} rounded-lg p-6 border ${metric.borderColor}`">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 mb-1">{{ metric.title }}</p>
            <p class="text-2xl font-bold" :class="metric.textColor">{{ metric.value }}</p>
            <p class="text-sm text-gray-500 mt-1">{{ metric.subtitle }}</p>
          </div>
          <div :class="`w-12 h-12 rounded-lg flex items-center justify-center ${metric.iconBgColor}`">
            <el-icon :size="24" class="text-white">
              <component :is="metric.icon" />
            </el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- 客流趋势分析 -->
      <el-card class="shadow-sm" shadow="never">
        <template #header>
          <span class="text-lg font-semibold text-gray-800">客流趋势</span>
        </template>
        <div v-loading="loading" ref="passengerFlowChartRef" class="h-80"></div>
      </el-card>

      <!-- 热门线路客流Top10 -->
      <el-card class="shadow-sm" shadow="never">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold text-gray-800">热门线路客流 TOP 10</span>
            <el-button type="primary" size="small" @click="refreshRouteStatus" :loading="loading">
              <el-icon>
                <Refresh />
              </el-icon>
              刷新
            </el-button>
          </div>
        </template>
        <div v-loading="loading" ref="routeStatusChartRef" class="h-80"></div>
      </el-card>
    </div>

    <!-- 实时数据表格 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- 热门线路 -->
      <el-card class="shadow-sm" shadow="never">
        <template #header>
          <span class="text-lg font-semibold text-gray-800">热门线路 TOP 10</span>
        </template>
        <div v-loading="loading" class="space-y-3">
          <div v-for="(route, index) in topRoutes" :key="route.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex items-center space-x-3">
              <div
                class="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                {{ index + 1 }}
              </div>
              <div>
                <p class="font-medium text-gray-800">{{ route.route_name }}</p>
                <p class="text-sm text-gray-500">{{ route.company_name }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="font-semibold text-gray-800">{{ route.flow }}</p>
              <p class="text-sm text-gray-500">人次</p>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 热门站点 -->
      <el-card class="shadow-sm" shadow="never">
        <template #header>
          <span class="text-lg font-semibold text-gray-800">客流热门站点 TOP 10</span>
        </template>
        <div v-loading="loading" class="space-y-3">
          <div v-for="(stop, index) in topStops" :key="stop.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex items-center space-x-3">
              <div
                class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                {{ index + 1 }}
              </div>
              <div>
                <p class="font-medium text-gray-800">{{ stop.stop_name }}</p>
                <p class="text-sm text-gray-500">{{ stop.district }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="font-semibold text-gray-800">{{ stop.flow }}</p>
              <p class="text-sm text-gray-500">人次</p>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 热门区域 -->
      <el-card class="shadow-sm" shadow="never">
        <template #header>
          <span class="text-lg font-semibold text-gray-800">客流热门区域</span>
        </template>
        <div v-loading="loading" class="space-y-3">
          <div v-for="(area, index) in topAreas" :key="area.id"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex items-center space-x-3">
              <div
                class="w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                {{ index + 1 }}
              </div>
              <div>
                <p class="font-medium text-gray-800">{{ area.district_name }}</p>
                <p class="text-sm text-gray-500">{{ area.district_level }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="font-semibold text-gray-800">{{ area.monthly_avg_flow }}</p>
              <p class="text-sm text-gray-500">日均客流</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  User,
  Location,
  Timer,
  Refresh,
  Warning,
  InfoFilled,
  CircleCheckFilled
} from '@element-plus/icons-vue'
import {
  GetDashboardData,
  GetFlowTrendData,
  GetRoadlineStatus,
  GetHotStops,
  GetHotDistricts,
  type DashboardData,
  type FlowTrendData,
  type RoadlineStatus,
  type HotStop,
  type HotDistrict
} from './api'



// 图表引用
const passengerFlowChartRef = ref<HTMLDivElement>()
const routeStatusChartRef = ref<HTMLDivElement>()
let passengerFlowChart: ECharts | null = null
let routeStatusChart: ECharts | null = null

// 加载状态
const loading = ref(false)

// 日期选择
const selectedDate = ref<string>('')

// 关键指标数据
const keyMetrics = ref([
  {
    title: '总客流量',
    value: '156,842',
    subtitle: '今日累计',
    icon: 'User',
    gradientBg: 'from-blue-50 to-blue-100',
    borderColor: 'border-blue-200',
    textColor: 'text-blue-600',
    iconBgColor: 'bg-blue-500',
    trend: 12.5
  },
  {
    title: '运营线路',
    value: '48',
    subtitle: '条线路在运营',
    icon: 'Location',
    gradientBg: 'from-green-50 to-green-100',
    borderColor: 'border-green-200',
    textColor: 'text-green-600',
    iconBgColor: 'bg-green-500',
    trend: 2.1
  },
  {
    title: '运营车辆',
    value: '186',
    subtitle: '辆车在线',
    icon: 'TrendCharts',
    gradientBg: 'from-orange-50 to-orange-100',
    borderColor: 'border-orange-200',
    textColor: 'text-orange-600',
    iconBgColor: 'bg-orange-500',
    trend: -1.2
  },
  {
    title: '平均载客率',
    value: '68.5%',
    subtitle: '当前载客率',
    icon: 'Timer',
    gradientBg: 'from-purple-50 to-purple-100',
    borderColor: 'border-purple-200',
    textColor: 'text-purple-600',
    iconBgColor: 'bg-purple-500',
    trend: 5.8
  }
])

// 热门线路数据
const topRoutes = ref([

])

// 热门站点数据
const topStops = ref([

])

// 热门区域数据
const topAreas = ref([])

// 格式化数字
const formatNumber = (num: number): string => {
  return num.toLocaleString('zh-CN')
}

// 格式化百分比
const formatPercent = (num: number): string => {
  return num.toFixed(1) + '%'
}

// 获取当前日期（YYYY-MM-DD）
const getCurrentDate = (): string => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 获取当前月份（YYYY-MM）
const getCurrentMonth = (): string => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

// 加载仪表板数据
const loadDashboardData = async () => {
  if (!selectedDate.value) return

  try {
    const response: any = await GetDashboardData(selectedDate.value)

    if (response.code === 2000 && response.data) {
      const data = response.data

      // 更新关键指标
      keyMetrics.value = [
        {
          title: '总客流量',
          value: formatNumber(data.card_data?.total_flow || 0),
          subtitle: '今日累计',
          icon: 'User',
          gradientBg: 'from-blue-50 to-blue-100',
          borderColor: 'border-blue-200',
          textColor: 'text-blue-600',
          iconBgColor: 'bg-blue-500',
          trend: 0
        },
        {
          title: '运营线路',
          value: String(data.card_data?.operating_routes || 0),
          subtitle: '条线路在运营',
          icon: 'Location',
          gradientBg: 'from-green-50 to-green-100',
          borderColor: 'border-green-200',
          textColor: 'text-green-600',
          iconBgColor: 'bg-green-500',
          trend: 0
        },
        {
          title: '运营车辆',
          value: String(data.card_data?.total_vehicles || 0),
          subtitle: '辆车在线',
          icon: 'TrendCharts',
          gradientBg: 'from-orange-50 to-orange-100',
          borderColor: 'border-orange-200',
          textColor: 'text-orange-600',
          iconBgColor: 'bg-orange-500',
          trend: 0
        },
        {
          title: '平均载客率',
          value: String(data.card_data?.avg_comfort || 0) + '%',
          subtitle: '当前载客率',
          icon: 'Timer',
          gradientBg: 'from-purple-50 to-purple-100',
          borderColor: 'border-purple-200',
          textColor: 'text-purple-600',
          iconBgColor: 'bg-purple-500',
          trend: 0
        }
      ]

      // 更新热门线路
      if (data.hot_routes && data.hot_routes.length > 0) {
        topRoutes.value = data.hot_routes.slice(0, 10)
        // 更新线路运营状态图表（柱状图）
        updateRouteStatusChart()
      }
    } else {
      ElMessage.error(`获取仪表板数据失败: ${response?.msg || '未知错误'}`)
    }
  } catch (error: any) {
    console.error('加载仪表板数据失败:', error)
    ElMessage.error('加载仪表板数据失败，请稍后重试')
  }
}

// 加载客流趋势数据
const loadFlowTrendData = async () => {
  if (!selectedDate.value) return

  try {
    const response: any = await GetFlowTrendData(selectedDate.value)
    console.log('加载客流趋势数据', response)
    if (response.code === 2000 && response.data) {
      const data = response.data

      // 更新图表数据
      if (passengerFlowChart && data.trend_data) {
        const hours = data.trend_data.map((item: any) => item.hour)
        const inCountData = data.trend_data.map((item: any) => item.hourly_in_count)
        const outCountData = data.trend_data.map((item: any) => item.hourly_out_count)

        passengerFlowChart.setOption({
          xAxis: {
            data: hours
          },
          series: [
            {
              name: '上车人数',
              data: inCountData
            },
            {
              name: '下车人数',
              data: outCountData
            }
          ]
        })
      }
    } else {
      ElMessage.error(`获取客流趋势数据失败: ${response?.msg || '未知错误'}`)
    }
  } catch (error: any) {
    console.error('加载客流趋势数据失败:', error)
    ElMessage.error('加载客流趋势数据失败，请稍后重试')
  }
}

// 更新线路运营状态图表（使用热门线路Top10数据）
const updateRouteStatusChart = () => {
  if (!routeStatusChart || !topRoutes.value || topRoutes.value.length === 0) return

  // 取前10条线路数据（纵向柱状图从左到右显示，保持原顺序）
  const top10Routes = topRoutes.value.slice(0, 10)

  const routeNames = top10Routes.map(route => route.route_name || '未知线路')
  const flowData = top10Routes.map(route => Number(route.flow) || 0)

  routeStatusChart.setOption({
    xAxis: {
      data: routeNames
    },
    series: [{
      data: flowData
    }]
  })
}

// 加载线路状态数据（改为加载热门线路数据并更新图表）
const loadRoadlineStatus = async () => {
  // 该函数现在由 loadDashboardData 中的热门线路数据更新触发
  // 直接调用更新图表函数
  updateRouteStatusChart()
}

// 加载热门站点数据
const loadHotStops = async () => {
  if (!selectedDate.value) return

  try {
    const response: any = await GetHotStops(selectedDate.value)

    if (response.code === 2000 && response.data) {
      const data = response.data
      if (data.hot_stops && Array.isArray(data.hot_stops)) {
        topStops.value = data.hot_stops.slice(0, 10)
      }
    } else {
      ElMessage.error(`获取热门站点数据失败: ${response?.msg || '未知错误'}`)
    }
  } catch (error: any) {
    console.error('加载热门站点数据失败:', error)
    ElMessage.error('加载热门站点数据失败，请稍后重试')
  }
}

// 加载热门区域数据
const loadHotDistricts = async () => {
  const month = getCurrentMonth()

  try {
    const response: any = await GetHotDistricts(month)

    if (response.code === 2000 && response.data) {
      const data = response.data
      if (data.hot_districts && Array.isArray(data.hot_districts)) {
        topAreas.value = data.hot_districts.slice(0, 10)
      }
    } else {
      ElMessage.error(`获取热门区域数据失败: ${response?.msg || '未知错误'}`)
    }
  } catch (error: any) {
    console.error('加载热门区域数据失败:', error)
    ElMessage.error('加载热门区域数据失败，请稍后重试')
  }
}

// 加载所有数据
const loadAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadDashboardData(),
      loadFlowTrendData(),
      loadRoadlineStatus(),
      loadHotStops(),
      loadHotDistricts()
    ])
  } finally {
    loading.value = false
  }
}

// 日期变化处理
const handleDateChange = () => {
  loadAllData()
}

// 刷新线路状态
const refreshRouteStatus = async () => {
  loading.value = true
  try {
    // 重新加载仪表板数据以获取最新的热门线路数据
    await loadDashboardData()
    ElMessage.success('刷新成功')
  } finally {
    loading.value = false
  }
}

// 初始化客流趋势图
const initPassengerFlowChart = () => {
  if (!passengerFlowChartRef.value) return

  passengerFlowChart = echarts.init(passengerFlowChartRef.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: 0,
      right: 0,
      top: '10%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
    },
    yAxis: {
      type: 'value',
      name: '客流人次'
    },
    series: [
      {
        name: '上车人数',
        type: 'line',
        smooth: true,
        data: [1200, 3200, 2100, 2800, 2400, 3100, 4200, 2800, 1500],
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '下车人数',
        type: 'line',
        smooth: true,
        data: [800, 2800, 2300, 2600, 2200, 2900, 3800, 3200, 1800],
        itemStyle: {
          color: '#52c41a'
        }
      }
    ]
  }

  passengerFlowChart.setOption(option)
}

// 初始化线路状态图
const initRouteStatusChart = () => {
  if (!routeStatusChartRef.value) return

  routeStatusChart = echarts.init(routeStatusChartRef.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}<br/>客流量: {c} 人次'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: [],
      axisLabel: {
        interval: 0,
        rotate: 45,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      name: '客流量（人次）',
      nameTextStyle: {
        color: '#666',
        fontSize: 12
      },
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 10000) {
            return (value / 10000).toFixed(1) + 'w'
          }
          return value.toString()
        }
      }
    },
    series: [
      {
        name: '客流量',
        type: 'bar',
        data: [],
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 1, 0, 0, [
            { offset: 0, color: '#4facfe' },
            { offset: 1, color: '#00f2fe' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: {
          show: true,
          position: 'top',
          formatter: (params: any) => {
            const value = params.value
            if (value >= 10000) {
              return (value / 10000).toFixed(1) + 'w'
            }
            return value.toString()
          },
          fontSize: 11,
          color: '#666'
        }
      }
    ]
  }

  routeStatusChart.setOption(option)
}

// 生命周期
onMounted(async () => {
  // 初始化日期为今天
  selectedDate.value = getCurrentDate()

  // 延迟初始化图表，确保DOM已渲染
  await nextTick()

  initPassengerFlowChart()
  initRouteStatusChart()
  // 加载数据
  await loadAllData()

  // 监听窗口大小变化
  const handleResize = () => {
    passengerFlowChart?.resize()
    routeStatusChart?.resize()
  }
  window.addEventListener('resize', handleResize)

    // 保存resize处理函数以便清理
    ; (window as any).__homeResizeHandler = handleResize
})

onUnmounted(() => {
  passengerFlowChart?.dispose()
  routeStatusChart?.dispose()
  const handleResize = (window as any).__homeResizeHandler
  if (handleResize) {
    window.removeEventListener('resize', handleResize)
    delete (window as any).__homeResizeHandler
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  @apply min-h-screen;
  font-size: 14px;
}


.el-card {
  border-radius: 8px;
}

.el-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.el-card :deep(.el-card__body) {
  padding: 20px;
}
</style>