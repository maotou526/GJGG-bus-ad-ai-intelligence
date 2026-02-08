import { defineStore } from 'pinia'

// 车辆类型：与 ScheduleCalendar 中使用的结构保持一致
export interface Vehicle {
  id: string
  plateNumber: string
  route: string
}

// 排期类型：与 ScheduleCalendar 中使用的结构保持一致
export interface AdSchedule {
  id: string
  vehicleId: string
  advertiser: string
  adType: string
  status: 'reserved' | 'active' | 'finished'
  startDate: string // 格式：YYYY-MM-DD
  endDate: string   // 格式：YYYY-MM-DD
  base_media_type_id?: string // 媒体类型ID，用于冲突检测
  // 用于判断到期未下刊的字段
  off_air_date?: string // 下刊日期，格式：YYYY-MM-DD
  scheduled_end_date?: string // 投放结束日期，格式：YYYY-MM-DD
}

export const useAdScheduleStore = defineStore('adSchedule', {
  state: () => ({
    vehicles: [] as Vehicle[],
    schedules: [] as AdSchedule[],
  }),
  actions: {
    // 同步外部传入的数据（由组件负责调用）
    setData(vehicles: Vehicle[], schedules: AdSchedule[]) {
      this.vehicles = vehicles || []
      this.schedules = schedules || []
    },

    // 根据车辆 ID 获取车辆信息（用于抽屉中展示）
    getVehicleById(id: string) {
      return this.vehicles.find((v) => v.id === id)
    },

    // 检查排期是否与当前已有排期冲突
    // 冲突规则：相同 vehicle_id 且相同 base_media_type_id 的日期段会冲突
    // 相同 vehicle_id 但不同 base_media_type_id 的日期段不冲突
    checkConflict(target: AdSchedule): boolean {
      if (!target) return false

      const tStart = target.startDate
      const tEnd = target.endDate
      const tMediaTypeId = target.base_media_type_id

      return this.schedules.some((s) => {
        if (!s) return false
        if (s.id === target.id) return false
        // 必须相同车辆
        if (s.vehicleId !== target.vehicleId) return false
        // 必须相同媒体类型ID才会冲突
        if (s.base_media_type_id !== tMediaTypeId) return false

        const sStart = s.startDate
        const sEnd = s.endDate

        // 日期格式为 YYYY-MM-DD，可以安全使用字符串比较
        // 检查日期区间是否有交集
        const noOverlap = sEnd < tStart || sStart > tEnd
        return !noOverlap
      })
    },

    // 更新排期：如果冲突则抛出异常，在组件中捕获并提示
    updateSchedule(newSchedule: AdSchedule) {
      if (this.checkConflict(newSchedule)) {
        throw new Error('schedule conflict')
      }

      const idx = this.schedules.findIndex((s) => s.id === newSchedule.id)
      if (idx !== -1) {
        this.schedules[idx] = { ...this.schedules[idx], ...newSchedule }
      } else {
        this.schedules.push(newSchedule)
      }
    },
  },
})


