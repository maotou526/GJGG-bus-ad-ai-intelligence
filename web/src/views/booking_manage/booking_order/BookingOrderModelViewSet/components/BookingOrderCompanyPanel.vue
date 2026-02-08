<template>
  <el-card shadow="never" class="company-panel">
    <template #header>
      <div class="panel-header">
        <span class="panel-title">营运公司审核</span>
        <div class="panel-stats">
          <el-tag size="small" type="warning">待确认 {{ stats.pending }}</el-tag>
          <el-tag size="small" type="success">已确认 {{ stats.confirmed }}</el-tag>
          <el-tag size="small" type="danger">已剔除 {{ stats.excluded }}</el-tag>
        </div>
      </div>
    </template>

    <!-- 按公司分组的 Tabs -->
    <el-tabs v-model="activeCompany" type="border-card">
      <el-tab-pane
        v-for="group in companyGroups"
        :key="group.companyId"
        :label="`${group.companyName} (${group.positions.length})`"
        :name="group.companyId"
      >
        <!-- 公司级操作栏 -->
        <div v-if="!readonly" class="company-actions">
          <el-button
            v-if="group.stats.pending > 0"
            type="primary"
            size="small"
            @click="handleBatchConfirm(group.companyId)"
            :loading="batchLoading"
          >
            全部确认 ({{ group.stats.pending }})
          </el-button>
          <span class="company-stat-text">
            {{ group.stats.confirmed }} 已确认 / {{ group.stats.excluded }} 已剔除 / {{ group.stats.pending }} 待处理
          </span>
        </div>

        <!-- 车位列表 -->
        <el-table :data="group.positions" border size="small" style="width: 100%">
          <el-table-column type="index" label="#" width="45" align="center" />
          <el-table-column label="线路" min-width="100">
            <template #default="{ row }">
              {{ row.roadline_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="车辆编号" min-width="90">
            <template #default="{ row }">
              <span class="vehicle-no">{{ row.vehicle_no || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="车牌号" min-width="100">
            <template #default="{ row }">
              {{ row.vehicle_plate || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="媒体类型" min-width="100">
            <template #default="{ row }">
              {{ row.media_type_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="日期" min-width="160">
            <template #default="{ row }">
              {{ row.reserved_start_date }} ~ {{ row.reserved_end_date }}
            </template>
          </el-table-column>
          <el-table-column label="确认状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag size="small" :type="confirmStatusType(row.confirm_status)">
                {{ confirmStatusText(row.confirm_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="!readonly" label="操作" width="200" align="center" fixed="right">
            <template #default="{ row }">
              <template v-if="row.confirm_status === 1">
                <el-button link type="success" size="small" @click="handleConfirm(row)">确认</el-button>
                <el-button link type="warning" size="small" @click="handleSwap(row)">换车</el-button>
                <el-button link type="danger" size="small" @click="handleExclude(row)">剔除</el-button>
              </template>
              <template v-else-if="row.confirm_status === 3">
                <el-text type="danger" size="small">{{ row.exclude_reason || '已剔除' }}</el-text>
              </template>
              <template v-else>
                <el-text type="success" size="small">已确认</el-text>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 换车弹窗 -->
    <el-dialog v-model="swapDialogVisible" title="换车" width="480px" append-to-body>
      <el-form label-width="90px">
        <el-form-item label="当前车辆">
          <el-input :model-value="swapForm.currentVehicleNo" disabled />
        </el-form-item>
        <el-form-item label="新车辆" required>
          <el-select
            v-model="swapForm.newVehicleId"
            filterable
            placeholder="请选择新车辆"
            style="width: 100%"
          >
            <el-option
              v-for="v in availableVehicles"
              :key="v.id"
              :label="`${v.vehicle_no} (${v.license_plate || '-'})`"
              :value="v.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="换车原因">
          <el-input v-model="swapForm.reason" type="textarea" :rows="2" placeholder="请输入换车原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="swapDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSwap" :loading="swapLoading">确认换车</el-button>
      </template>
    </el-dialog>

    <!-- 剔除弹窗 -->
    <el-dialog v-model="excludeDialogVisible" title="剔除车位" width="420px" append-to-body>
      <el-form label-width="90px">
        <el-form-item label="车辆">
          <el-input :model-value="excludeForm.vehicleNo" disabled />
        </el-form-item>
        <el-form-item label="剔除原因" required>
          <el-input v-model="excludeForm.reason" type="textarea" :rows="3" placeholder="请输入剔除原因（必填）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="excludeDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmExclude" :loading="excludeLoading">确认剔除</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as api from '../api'

const props = defineProps<{
  orderId: string
  positions: Record<string, any>[]
  vehicles?: Record<string, any>[]
  readonly?: boolean
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const activeCompany = ref('')
const batchLoading = ref(false)

// 统计
const stats = computed(() => {
  let pending = 0, confirmed = 0, excluded = 0
  for (const p of props.positions) {
    if (p.confirm_status === 1) pending++
    else if (p.confirm_status === 2) confirmed++
    else if (p.confirm_status === 3) excluded++
  }
  return { pending, confirmed, excluded }
})

// 按公司分组
interface CompanyGroup {
  companyId: string
  companyName: string
  positions: Record<string, any>[]
  stats: { pending: number; confirmed: number; excluded: number }
}

const companyGroups = computed<CompanyGroup[]>(() => {
  const map: Record<string, CompanyGroup> = {}
  for (const pos of props.positions) {
    const cid = pos.roadline_company_id?.id || pos.roadline_company_id || 'unknown'
    const cname = pos.roadline_company_name || '未知公司'
    if (!map[cid]) {
      map[cid] = { companyId: cid, companyName: cname, positions: [], stats: { pending: 0, confirmed: 0, excluded: 0 } }
    }
    map[cid].positions.push(pos)
    if (pos.confirm_status === 1) map[cid].stats.pending++
    else if (pos.confirm_status === 2) map[cid].stats.confirmed++
    else if (pos.confirm_status === 3) map[cid].stats.excluded++
  }
  const groups = Object.values(map)
  if (groups.length > 0 && !activeCompany.value) {
    activeCompany.value = groups[0].companyId
  }
  return groups
})

// 确认状态
const CONFIRM_MAP: Record<number, { text: string; type: string }> = {
  1: { text: '待确认', type: 'warning' },
  2: { text: '已确认', type: 'success' },
  3: { text: '已剔除', type: 'danger' },
}
const confirmStatusText = (s: number) => CONFIRM_MAP[s]?.text || '未知'
const confirmStatusType = (s: number) => CONFIRM_MAP[s]?.type || 'info'

// 确认
const handleConfirm = async (row: any) => {
  try {
    await api.companyConfirmPosition(props.orderId, { position_id: row.id })
    ElMessage.success('确认成功')
    emit('refresh')
  } catch (e: any) {
    ElMessage.error(e.message || '确认失败')
  }
}

// 批量确认
const handleBatchConfirm = async (companyId: string) => {
  try {
    await ElMessageBox.confirm('确定要批量确认该公司所有待确认车位吗？', '批量确认')
    batchLoading.value = true
    await api.companyBatchConfirm(props.orderId, { company_id: companyId })
    ElMessage.success('批量确认成功')
    emit('refresh')
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '批量确认失败')
  } finally {
    batchLoading.value = false
  }
}

// 换车
const swapDialogVisible = ref(false)
const swapLoading = ref(false)
const swapForm = reactive({ positionId: '', currentVehicleNo: '', newVehicleId: '', reason: '', roadlineId: '' })

const availableVehicles = computed(() => {
  if (!props.vehicles || !swapForm.roadlineId) return props.vehicles || []
  return props.vehicles.filter((v: any) => {
    const rl = v.roadline_id?.id || v.roadline_id
    return rl === swapForm.roadlineId
  })
})

const handleSwap = (row: any) => {
  swapForm.positionId = row.id
  swapForm.currentVehicleNo = row.vehicle_no || '-'
  swapForm.newVehicleId = ''
  swapForm.reason = ''
  swapForm.roadlineId = row.roadline_id?.id || row.roadline_id || ''
  swapDialogVisible.value = true
}

const confirmSwap = async () => {
  if (!swapForm.newVehicleId) {
    ElMessage.warning('请选择新车辆')
    return
  }
  try {
    swapLoading.value = true
    await api.companySwapVehicle(props.orderId, {
      position_id: swapForm.positionId,
      new_vehicle_id: swapForm.newVehicleId,
      swap_reason: swapForm.reason || '营运公司换车',
    })
    ElMessage.success('换车成功')
    swapDialogVisible.value = false
    emit('refresh')
  } catch (e: any) {
    ElMessage.error(e.message || '换车失败')
  } finally {
    swapLoading.value = false
  }
}

// 剔除
const excludeDialogVisible = ref(false)
const excludeLoading = ref(false)
const excludeForm = reactive({ positionId: '', vehicleNo: '', reason: '' })

const handleExclude = (row: any) => {
  excludeForm.positionId = row.id
  excludeForm.vehicleNo = row.vehicle_no || '-'
  excludeForm.reason = ''
  excludeDialogVisible.value = true
}

const confirmExclude = async () => {
  if (!excludeForm.reason) {
    ElMessage.warning('请输入剔除原因')
    return
  }
  try {
    excludeLoading.value = true
    await api.companyExcludePosition(props.orderId, {
      position_id: excludeForm.positionId,
      exclude_reason: excludeForm.reason,
    })
    ElMessage.success('剔除成功')
    excludeDialogVisible.value = false
    emit('refresh')
  } catch (e: any) {
    ElMessage.error(e.message || '剔除失败')
  } finally {
    excludeLoading.value = false
  }
}
</script>

<style scoped lang="scss">
.company-panel {
  margin-bottom: 12px;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.panel-title {
  font-weight: 600;
  font-size: 15px;
}
.panel-stats {
  display: flex;
  gap: 6px;
}
.company-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.company-stat-text {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.vehicle-no {
  font-weight: 600;
  font-family: monospace;
}
</style>
