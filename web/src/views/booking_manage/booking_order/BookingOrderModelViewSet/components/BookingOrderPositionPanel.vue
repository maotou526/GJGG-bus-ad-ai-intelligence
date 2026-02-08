<template>
  <el-card shadow="never" class="position-panel">
    <template #header>
      <div class="panel-header">
        <span class="panel-title">车位分配</span>
        <div class="panel-header-right">
          <el-radio-group v-model="groupBy" size="small">
            <el-radio-button value="vehicle">按车辆</el-radio-button>
            <el-radio-button value="detail">按明细</el-radio-button>
            <el-radio-button value="flat">平铺</el-radio-button>
          </el-radio-group>
          <el-tag size="small" type="info">共 {{ filteredPositions.length }} 条</el-tag>
        </div>
      </div>
    </template>

    <!-- 按车辆分组视图 -->
    <template v-if="groupBy === 'vehicle'">
      <div v-for="group in vehicleGroups" :key="group.vehicleId" class="vehicle-group">
        <div class="group-header" @click="group.collapsed = !group.collapsed">
          <el-icon class="collapse-icon" :class="{ rotated: !group.collapsed }">
            <ArrowRight />
          </el-icon>
          <span class="vehicle-no">{{ group.vehicleNo }}</span>
          <el-tag size="small" type="info" effect="plain">{{ group.roadlineName }}</el-tag>
          <span class="group-media">{{ group.mediaNames }}</span>
          <span class="group-date">{{ group.minDate }} ~ {{ group.maxDate }}</span>
          <el-tag size="small" :type="group.confirmTag" class="group-status">
            {{ group.confirmText }}
          </el-tag>
        </div>
        <el-collapse-transition>
          <div v-show="!group.collapsed" class="group-body">
            <el-table :data="group.positions" border size="small" style="width: 100%">
              <el-table-column label="媒体类型" min-width="100">
                <template #default="{ row }">
                  {{ row.media_type_name || getMediaTypeName(row.media_type_id) || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="资源位" min-width="120">
                <template #default="{ row }">
                  {{ row.resource_code || '-' }}
                </template>
              </el-table-column>
              <el-table-column label="日期" min-width="160">
                <template #default="{ row }">
                  {{ row.reserved_start_date }} ~ {{ row.reserved_end_date }}
                </template>
              </el-table-column>
              <el-table-column label="分配状态" width="90" align="center">
                <template #default="{ row }">
                  <el-tag size="small" :type="allocationStatusType(row.allocation_status)">
                    {{ allocationStatusText(row.allocation_status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="确认状态" width="90" align="center">
                <template #default="{ row }">
                  <el-tag size="small" :type="confirmStatusType(row.confirm_status)">
                    {{ confirmStatusText(row.confirm_status) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-collapse-transition>
      </div>
      <el-empty v-if="vehicleGroups.length === 0" description="暂无车位分配数据" :image-size="60" />
    </template>

    <!-- 平铺视图 -->
    <template v-else>
      <el-table :data="filteredPositions" border stripe size="small" style="width: 100%" max-height="400">
        <el-table-column type="index" label="#" width="45" align="center" />
        <el-table-column label="线路" min-width="100">
          <template #default="{ row }">
            {{ row.roadline_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="车辆" min-width="90">
          <template #default="{ row }">
            {{ row.vehicle_no || '-' }}
          </template>
        </el-table-column>
        <el-table-column v-if="groupBy === 'detail'" label="车牌号" min-width="100">
          <template #default="{ row }">
            {{ row.vehicle_plate || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="媒体类型" min-width="100">
          <template #default="{ row }">
            {{ row.media_type_name || getMediaTypeName(row.media_type_id) || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="日期" min-width="160">
          <template #default="{ row }">
            {{ row.reserved_start_date }} ~ {{ row.reserved_end_date }}
          </template>
        </el-table-column>
        <el-table-column label="分配状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="allocationStatusType(row.allocation_status)">
              {{ allocationStatusText(row.allocation_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="确认状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="confirmStatusType(row.confirm_status)">
              {{ confirmStatusText(row.confirm_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="showExcludeReason" label="剔除原因" min-width="120">
          <template #default="{ row }">
            {{ row.exclude_reason || '-' }}
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="filteredPositions.length === 0" description="暂无车位分配数据" :image-size="60" />
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  positions: Record<string, any>[]
  filterDetailId?: string | null
  mediaTypes?: Record<string, any>[]
  showExcludeReason?: boolean
}>()

const groupBy = ref<'vehicle' | 'detail' | 'flat'>('vehicle')

const filteredPositions = computed(() => {
  if (!props.filterDetailId) return props.positions
  return props.positions.filter(p => {
    const detailId = p.booking_detail_id?.id || p.booking_detail_id
    return detailId === props.filterDetailId
  })
})

interface VehicleGroup {
  vehicleId: string
  vehicleNo: string
  roadlineName: string
  mediaNames: string
  minDate: string
  maxDate: string
  confirmText: string
  confirmTag: string
  positions: Record<string, any>[]
  collapsed: boolean
}

const vehicleGroups = computed<VehicleGroup[]>(() => {
  const map: Record<string, VehicleGroup> = {}
  for (const pos of filteredPositions.value) {
    const vid = pos.vehicle_id?.id || pos.vehicle_id || 'unknown'
    if (!map[vid]) {
      map[vid] = reactive({
        vehicleId: vid,
        vehicleNo: pos.vehicle_no || '-',
        roadlineName: pos.roadline_name || '-',
        mediaNames: '',
        minDate: '',
        maxDate: '',
        confirmText: '',
        confirmTag: 'info',
        positions: [],
        collapsed: false,
      })
    }
    map[vid].positions.push(pos)
  }

  // 计算汇总信息
  for (const group of Object.values(map)) {
    const names = new Set<string>()
    let minD = '', maxD = ''
    let pending = 0, confirmed = 0, excluded = 0

    for (const p of group.positions) {
      const name = p.media_type_name || getMediaTypeName(p.media_type_id) || ''
      if (name) names.add(name)
      if (!minD || p.reserved_start_date < minD) minD = p.reserved_start_date
      if (!maxD || p.reserved_end_date > maxD) maxD = p.reserved_end_date
      if (p.confirm_status === 1) pending++
      else if (p.confirm_status === 2) confirmed++
      else if (p.confirm_status === 3) excluded++
    }

    group.mediaNames = Array.from(names).join('、')
    group.minDate = minD
    group.maxDate = maxD

    if (excluded === group.positions.length) {
      group.confirmText = '全部剔除'
      group.confirmTag = 'danger'
    } else if (confirmed === group.positions.length) {
      group.confirmText = '全部确认'
      group.confirmTag = 'success'
    } else if (pending > 0) {
      group.confirmText = `待确认(${pending})`
      group.confirmTag = 'warning'
    } else {
      group.confirmText = `确认${confirmed}/剔除${excluded}`
      group.confirmTag = 'info'
    }
  }

  return Object.values(map)
})

const getMediaTypeName = (id: string) => {
  if (!id || !props.mediaTypes) return ''
  const m = props.mediaTypes.find((m: any) => m.id === id)
  return m?.media_name || m?.name || ''
}

const ALLOC_MAP: Record<number, { text: string; type: string }> = {
  1: { text: '已分配', type: 'success' },
  2: { text: '已上刊', type: '' },
  3: { text: '已下刊', type: 'info' },
  4: { text: '已取消', type: 'danger' },
}

const CONFIRM_MAP: Record<number, { text: string; type: string }> = {
  1: { text: '待确认', type: 'warning' },
  2: { text: '已确认', type: 'success' },
  3: { text: '已剔除', type: 'danger' },
}

const allocationStatusText = (s: number) => ALLOC_MAP[s]?.text || '未知'
const allocationStatusType = (s: number) => ALLOC_MAP[s]?.type || 'info'
const confirmStatusText = (s: number) => CONFIRM_MAP[s]?.text || '未知'
const confirmStatusType = (s: number) => CONFIRM_MAP[s]?.type || 'info'
</script>

<style scoped lang="scss">
.position-panel {
  margin-bottom: 12px;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.panel-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.panel-title {
  font-weight: 600;
  font-size: 15px;
}

.vehicle-group {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  margin-bottom: 8px;
  overflow: hidden;

  &:last-child {
    margin-bottom: 0;
  }
}

.group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--el-fill-color-light);
  cursor: pointer;
  font-size: 13px;

  &:hover {
    background: var(--el-fill-color);
  }
}

.collapse-icon {
  transition: transform 0.3s;
  font-size: 12px;

  &.rotated {
    transform: rotate(90deg);
  }
}

.vehicle-no {
  font-weight: 600;
  color: var(--el-color-primary);
  font-family: monospace;
}

.group-media {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.group-date {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-left: auto;
}

.group-status {
  margin-left: 8px;
}

.group-body {
  padding: 0;
}
</style>
