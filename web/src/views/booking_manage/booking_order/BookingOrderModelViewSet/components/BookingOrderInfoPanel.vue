<template>
  <el-card shadow="never" class="info-panel">
    <template #header>
      <div class="panel-header">
        <span class="panel-title">预订单信息</span>
        <el-tag :type="statusTagType" size="default" effect="plain">{{ statusText }}</el-tag>
      </div>
    </template>

    <el-descriptions :column="3" border size="default">
      <el-descriptions-item label="预订单号" :span="1">
        <span class="booking-no">{{ order.booking_no || '-' }}</span>
      </el-descriptions-item>
      <el-descriptions-item label="预订类型" :span="1">
        <el-tag size="small" :type="bookingTypeTag">{{ bookingTypeText }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="当前节点" :span="1">
        <el-tag v-if="order.current_approval_node" size="small" type="warning">
          {{ approvalNodeText }}
        </el-tag>
        <span v-else>-</span>
      </el-descriptions-item>

      <el-descriptions-item label="客户名称" :span="1">
        {{ order.customer_name || getCustomerName(order.customer_id) || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="代理商" :span="1">
        {{ getAgentName(order.agent_id) || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="提交人" :span="1">
        {{ order.submitter_name || '-' }}
      </el-descriptions-item>

      <el-descriptions-item label="广告内容" :span="3">
        {{ order.ad_content || '-' }}
      </el-descriptions-item>

      <el-descriptions-item label="订单金额" :span="1">
        <span v-if="order.total_amount" class="amount">{{ formatAmount(order.total_amount) }}</span>
        <span v-else>-</span>
      </el-descriptions-item>
      <el-descriptions-item label="已支付" :span="1">
        <span v-if="order.paid_amount" class="amount">{{ formatAmount(order.paid_amount) }}</span>
        <span v-else>0.00</span>
      </el-descriptions-item>
      <el-descriptions-item label="提交时间" :span="1">
        {{ order.submit_time || '-' }}
      </el-descriptions-item>

      <!-- 驳回信息 -->
      <template v-if="order.booking_status === 7">
        <el-descriptions-item label="驳回原因" :span="2">
          <el-text type="danger">{{ order.reject_reason || '-' }}</el-text>
        </el-descriptions-item>
        <el-descriptions-item label="驳回时间" :span="1">
          {{ order.reject_time || '-' }}
        </el-descriptions-item>
      </template>

      <el-descriptions-item label="备注" :span="3">
        <div class="remark-content">{{ order.remark || '-' }}</div>
      </el-descriptions-item>
    </el-descriptions>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  order: Record<string, any>
  customers?: Record<string, any>[]
  agents?: Record<string, any>[]
}>()

const STATUS_MAP: Record<number, { text: string; type: string }> = {
  1: { text: '草稿', type: 'info' },
  2: { text: '待媒体部初审', type: 'warning' },
  3: { text: '待营运公司审核', type: 'warning' },
  4: { text: '待媒体部复审', type: 'warning' },
  5: { text: '已通过', type: 'success' },
  6: { text: '已完成', type: 'success' },
  7: { text: '已驳回', type: 'danger' },
  8: { text: '已取消', type: 'info' },
}

const BOOKING_TYPE_MAP: Record<number, { text: string; type: string }> = {
  1: { text: '新预订', type: '' },
  2: { text: '续期', type: 'success' },
  3: { text: '变更', type: 'warning' },
  4: { text: '重新发起', type: 'info' },
}

const NODE_MAP: Record<number, string> = {
  1: '媒体部初审',
  2: '营运公司审核',
  3: '媒体部复审',
}

const statusText = computed(() => STATUS_MAP[props.order.booking_status]?.text || '未知')
const statusTagType = computed(() => STATUS_MAP[props.order.booking_status]?.type || 'info')
const bookingTypeText = computed(() => BOOKING_TYPE_MAP[props.order.booking_type]?.text || '未知')
const bookingTypeTag = computed(() => BOOKING_TYPE_MAP[props.order.booking_type]?.type || '')
const approvalNodeText = computed(() => NODE_MAP[props.order.current_approval_node] || '')

const getCustomerName = (id: string) => {
  if (!id || !props.customers) return ''
  const c = props.customers.find((c: any) => c.id === id)
  return c?.customer_name || c?.name || ''
}

const getAgentName = (id: string) => {
  if (!id || !props.agents) return ''
  const a = props.agents.find((a: any) => a.id === id)
  return a?.agent_name || a?.name || ''
}

const formatAmount = (val: any) => {
  const num = parseFloat(val)
  return isNaN(num) ? '-' : `¥ ${num.toFixed(2)}`
}
</script>

<style scoped lang="scss">
.info-panel {
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
.booking-no {
  font-weight: 600;
  color: var(--el-color-primary);
  font-family: monospace;
}
.amount {
  font-weight: 600;
  color: var(--el-color-danger);
}
.remark-content {
  white-space: pre-wrap;
  max-height: 80px;
  overflow-y: auto;
}
</style>
