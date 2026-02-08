<template>
  <el-card shadow="never" class="detail-panel">
    <template #header>
      <div class="panel-header">
        <span class="panel-title">预订明细</span>
        <el-tag size="small" type="info">共 {{ details.length }} 条</el-tag>
      </div>
    </template>

    <el-table
      :data="details"
      border
      stripe
      size="small"
      highlight-current-row
      @current-change="handleCurrentChange"
      :row-class-name="getRowClassName"
      style="width: 100%"
    >
      <el-table-column type="index" label="#" width="45" align="center" />
      <el-table-column label="线路" min-width="120">
        <template #default="{ row }">
          {{ row.roadline_name || getRoadlineName(row.roadline_id) || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="营运公司" min-width="120">
        <template #default="{ row }">
          {{ row.roadline_company_name || getCompanyName(row.roadline_company_id) || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="媒体类型" min-width="110">
        <template #default="{ row }">
          <div class="media-cell">
            <el-tag v-if="row.is_composite" size="small" type="warning" effect="plain">组合</el-tag>
            <span>{{ row.media_type_name || getMediaTypeName(row.media_type_id) || '-' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="数量" width="70" align="center" prop="quantity" />
      <el-table-column label="投放日期" min-width="180">
        <template #default="{ row }">
          {{ row.start_date }} ~ {{ row.end_date }}
        </template>
      </el-table-column>
      <el-table-column label="锁定状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="lockStatusType(row.lock_status)" size="small">
            {{ lockStatusText(row.lock_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="showAmount" label="金额" width="100" align="right">
        <template #default="{ row }">
          {{ row.subtotal_amount ? `¥${parseFloat(row.subtotal_amount).toFixed(2)}` : '-' }}
        </template>
      </el-table-column>
    </el-table>

    <div v-if="selectedDetail" class="selected-tip">
      <el-icon><InfoFilled /></el-icon>
      <span>已选中：{{ selectedDetail.roadline_name }} - {{ selectedDetail.media_type_name }}，
        下方车位列表已按此明细过滤</span>
      <el-button link type="primary" size="small" @click="clearSelection">清除筛选</el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  details: Record<string, any>[]
  roadlines?: Record<string, any>[]
  companies?: Record<string, any>[]
  mediaTypes?: Record<string, any>[]
  showAmount?: boolean
}>()

const emit = defineEmits<{
  (e: 'select-detail', detail: Record<string, any> | null): void
}>()

const selectedDetail = ref<Record<string, any> | null>(null)

const handleCurrentChange = (row: Record<string, any> | null) => {
  selectedDetail.value = row
  emit('select-detail', row)
}

const clearSelection = () => {
  selectedDetail.value = null
  emit('select-detail', null)
}

const getRoadlineName = (id: string) => {
  if (!id || !props.roadlines) return ''
  const r = props.roadlines.find((r: any) => r.id === id)
  return r?.roadline_name || r?.name || ''
}

const getCompanyName = (id: string) => {
  if (!id || !props.companies) return ''
  const c = props.companies.find((c: any) => c.id === id)
  return c?.company_name || c?.name || ''
}

const getMediaTypeName = (id: string) => {
  if (!id || !props.mediaTypes) return ''
  const m = props.mediaTypes.find((m: any) => m.id === id)
  return m?.media_name || m?.name || ''
}

const LOCK_STATUS_MAP: Record<number, { text: string; type: string }> = {
  1: { text: '未锁定', type: 'info' },
  2: { text: '已锁定', type: 'success' },
  3: { text: '已释放', type: 'danger' },
}

const lockStatusText = (s: number) => LOCK_STATUS_MAP[s]?.text || '未知'
const lockStatusType = (s: number) => LOCK_STATUS_MAP[s]?.type || 'info'

const getRowClassName = ({ row }: any) => {
  if (selectedDetail.value && row.id === selectedDetail.value.id) {
    return 'selected-row'
  }
  return ''
}
</script>

<style scoped lang="scss">
.detail-panel {
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
.media-cell {
  display: flex;
  align-items: center;
  gap: 4px;
}
.selected-tip {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 6px 12px;
  background: var(--el-color-primary-light-9);
  border-radius: 4px;
  font-size: 13px;
  color: var(--el-color-primary);
}
:deep(.selected-row) {
  background-color: var(--el-color-primary-light-9) !important;
}
</style>
