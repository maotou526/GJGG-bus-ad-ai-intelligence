<template>
  <div class="booking-order-form">
    <!-- 审批流程进度 -->
    <el-card shadow="never" class="progress-card">
      <el-steps :active="currentStep" finish-status="success" align-center size="small">
        <el-step title="草稿" />
        <el-step title="媒体部初审" />
        <el-step title="营运公司审核" />
        <el-step title="媒体部复审" />
        <el-step title="已通过" />
      </el-steps>
    </el-card>

    <!-- 主订单信息 -->
    <BookingOrderInfoPanel
      :order="mainOrder"
      :customers="refData.customers"
      :agents="refData.agents"
    />

    <!-- 预订明细（主细表的"细"） -->
    <BookingOrderDetailPanel
      :details="detailList"
      :roadlines="refData.roadlines"
      :companies="refData.companies"
      :media-types="refData.mediaTypes"
      :show-amount="true"
      @select-detail="handleDetailSelect"
    />

    <!-- 车位分配面板 -->
    <BookingOrderPositionPanel
      :positions="positionList"
      :filter-detail-id="selectedDetailId"
      :media-types="refData.mediaTypes"
      :show-exclude-reason="mainOrder.booking_status >= 3"
    />

    <!-- 营运公司审核面板（仅在营运公司审核阶段显示） -->
    <BookingOrderCompanyPanel
      v-if="mainOrder.booking_status === 3"
      :order-id="orderId"
      :positions="positionList"
      :vehicles="refData.vehicles"
      :readonly="isReadonly"
      @refresh="loadAllData"
    />

    <!-- 变更记录 -->
    <BookingOrderChangeLog
      v-if="changeList.length > 0"
      :changes="changeList"
    />

    <!-- 审批操作区（非只读模式显示，且不在工作流容器中时显示） -->
    <el-card v-if="!isReadonly && !isInWorkflowContainer" shadow="never" class="action-card">
      <template #header>
        <span class="panel-title">审批操作</span>
      </template>

      <el-form label-width="90px">
        <el-form-item
          v-if="requiresComment"
          :label="mainOrder.booking_status === 3 ? '审核意见' : '审批意见'"
        >
          <el-input
            v-model="reviewComment"
            type="textarea"
            :rows="3"
            :placeholder="commentPlaceholder"
          />
        </el-form-item>
      </el-form>

      <div class="action-buttons">
        <!-- 媒体部初审 -->
        <template v-if="mainOrder.booking_status === 2">
          <el-button type="success" @click="handleFirstReviewApprove" :loading="actionLoading">
            初审通过
          </el-button>
          <el-button type="danger" @click="handleFirstReviewReject" :loading="actionLoading">
            初审驳回
          </el-button>
        </template>

        <!-- 营运公司审核 -->
        <template v-if="mainOrder.booking_status === 3">
          <el-button type="primary" @click="handleCompanyReviewComplete" :loading="actionLoading">
            营运审核完成
          </el-button>
        </template>

        <!-- 媒体部复审 -->
        <template v-if="mainOrder.booking_status === 4">
          <el-button type="success" @click="handleFinalReviewApprove" :loading="actionLoading">
            复审通过
          </el-button>
          <el-button type="danger" @click="handleFinalReviewReject" :loading="actionLoading">
            复审驳回
          </el-button>
        </template>
      </div>
    </el-card>

    <!-- 全局 Loading -->
    <div v-if="loading" class="loading-mask">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'

import BookingOrderInfoPanel from './BookingOrderInfoPanel.vue'
import BookingOrderDetailPanel from './BookingOrderDetailPanel.vue'
import BookingOrderPositionPanel from './BookingOrderPositionPanel.vue'
import BookingOrderCompanyPanel from './BookingOrderCompanyPanel.vue'
import BookingOrderChangeLog from './BookingOrderChangeLog.vue'

import * as bookingApi from '../api'
import { GetList as getBookingDetailList } from '/@/views/booking_manage/booking_order_detail/BookingOrderDetailModelViewSet/api'
import { GetList as getPositionList } from '/@/views/booking_manage/vehicle_ad_position/VehicleAdPositionModelViewSet/api'
import { GetList as getChangeList } from '/@/views/booking_manage/vehicle_ad_position_change/VehicleAdPositionChangeModelViewSet/api'
import { GetList as getRoadlineList } from '/@/views/basedata/roadline/RoadlineModelViewSet/api'
import { GetList as getCompanyList } from '/@/views/basedata/company/CompanyModelViewSet/api'
import { GetList as getMediaTypeList } from '/@/views/basedata/media_type/AdMediaTypeModelViewSet/api'
import { GetList as getVehicleList } from '/@/views/basedata/vehicle/VehicleModelViewSet/api'
import { GetList as getCustomerList } from '/@/views/booking_manage/customer/CustomerModelViewSet/api'
import { GetList as getAgentList } from '/@/views/booking_manage/agent/AgentModelViewSet/api'

// ========== Props ==========
interface WorkflowButton {
  id: string
  name: string
  code: string
  isHide: '1' | '2'
  isSign: '1' | '2'
  next: '1' | '2'
}

const props = withDefaults(defineProps<{
  readonly?: boolean
  data?: Record<string, any>
  nodeId?: string
  formParams?: Record<string, any>
  buttons?: WorkflowButton[]
}>(), {
  readonly: false,
  data: () => ({}),
  nodeId: '',
  formParams: () => ({}),
  buttons: () => [],
})

// ========== 核心状态 ==========
const loading = ref(false)
const actionLoading = ref(false)
const mainOrder = ref<Record<string, any>>({})
const detailList = ref<Record<string, any>[]>([])
const positionList = ref<Record<string, any>[]>([])
const changeList = ref<Record<string, any>[]>([])
const selectedDetailId = ref<string | null>(null)
const reviewComment = ref('')

// 判断是否在工作流容器 work/index.vue 中
const isInWorkflowContainer = computed(() => !!props.nodeId || !!props.buttons?.length)

const isReadonly = computed(() => {
  if (props.readonly) return true
  if (props.formParams?.viewFlag === '1' || props.formParams?.viewFlag === 1) return true
  return false
})

// 参考数据缓存
const refData = reactive<{
  roadlines: any[]
  companies: any[]
  mediaTypes: any[]
  vehicles: any[]
  customers: any[]
  agents: any[]
}>({
  roadlines: [],
  companies: [],
  mediaTypes: [],
  vehicles: [],
  customers: [],
  agents: [],
})

// ========== 计算属性 ==========
const orderId = computed(() => {
  return props.formParams?.id || props.data?.id || mainOrder.value?.id || ''
})

const currentStep = computed(() => {
  const s = mainOrder.value.booking_status
  if (s === 1) return 0
  if (s === 2) return 1
  if (s === 3) return 2
  if (s === 4) return 3
  if (s === 5 || s === 6) return 5
  if (s === 7) return -1  // 驳回状态不高亮
  if (s === 8) return -1  // 取消状态不高亮
  return 0
})

const requiresComment = computed(() => {
  const s = mainOrder.value.booking_status
  return [2, 3, 4].includes(s) && !isReadonly.value
})

const commentPlaceholder = computed(() => {
  const s = mainOrder.value.booking_status
  if (s === 2) return '请输入初审意见（通过时选填，驳回时必填）'
  if (s === 3) return '请输入营运公司审核意见'
  if (s === 4) return '请输入复审意见（通过时选填，驳回时必填）'
  return '请输入审批意见'
})

// ========== 数据加载 ==========
const loadRefData = async () => {
  try {
    const [roadlines, companies, mediaTypes, vehicles, customers, agents] = await Promise.all([
      getRoadlineList({ limit: 999 }).then(r => r.data?.results || r.data || []).catch(() => []),
      getCompanyList({ limit: 999 }).then(r => r.data?.results || r.data || []).catch(() => []),
      getMediaTypeList({ limit: 999 }).then(r => r.data?.results || r.data || []).catch(() => []),
      getVehicleList({ limit: 999 }).then(r => r.data?.results || r.data || []).catch(() => []),
      getCustomerList({ limit: 999 }).then(r => r.data?.results || r.data || []).catch(() => []),
      getAgentList({ limit: 999 }).then(r => r.data?.results || r.data || []).catch(() => []),
    ])
    refData.roadlines = roadlines
    refData.companies = companies
    refData.mediaTypes = mediaTypes
    refData.vehicles = vehicles
    refData.customers = customers
    refData.agents = agents
  } catch (e) {
    console.warn('[BookingOrderForm] 加载参考数据失败:', e)
  }
}

const loadMainOrder = async () => {
  if (!orderId.value) return
  try {
    const res = await bookingApi.GetList({ id: orderId.value, limit: 1 })
    const list = res.data?.results || res.data || []
    if (list.length > 0) {
      mainOrder.value = list[0]
    }
  } catch (e) {
    console.warn('[BookingOrderForm] 加载主订单失败:', e)
  }
}

const loadDetails = async () => {
  if (!orderId.value) return
  try {
    const res = await getBookingDetailList({ booking_order_id: orderId.value, limit: 999 })
    detailList.value = res.data?.results || res.data || []
  } catch (e) {
    console.warn('[BookingOrderForm] 加载明细失败:', e)
  }
}

const loadPositions = async () => {
  if (!orderId.value) return
  try {
    const res = await getPositionList({
      booking_detail_id__booking_order_id: orderId.value,
      limit: 9999,
      delete_mark: 0,
    })
    positionList.value = res.data?.results || res.data || []
  } catch (e) {
    console.warn('[BookingOrderForm] 加载车位失败:', e)
  }
}

const loadChanges = async () => {
  if (!orderId.value) return
  try {
    const res = await getChangeList({ booking_order_id: orderId.value, limit: 999 })
    changeList.value = res.data?.results || res.data || []
  } catch (e) {
    changeList.value = []
  }
}

const loadAllData = async () => {
  loading.value = true
  try {
    await Promise.all([loadMainOrder(), loadDetails(), loadPositions(), loadChanges()])
  } finally {
    loading.value = false
  }
}

// ========== 明细选择 ==========
const handleDetailSelect = (detail: Record<string, any> | null) => {
  selectedDetailId.value = detail?.id || null
}

// ========== 审批操作（独立模式，非工作流容器） ==========
const handleFirstReviewApprove = async () => {
  try {
    await ElMessageBox.confirm('确定初审通过该预订单？', '媒体部初审')
    actionLoading.value = true
    await bookingApi.firstReviewApprove(orderId.value, { review_comment: reviewComment.value })
    ElMessage.success('初审通过')
    reviewComment.value = ''
    await loadAllData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

const handleFirstReviewReject = async () => {
  if (!reviewComment.value) {
    ElMessage.warning('驳回时必须填写原因')
    return
  }
  try {
    await ElMessageBox.confirm('确定驳回该预订单？', '媒体部初审驳回', { type: 'warning' })
    actionLoading.value = true
    await bookingApi.firstReviewReject(orderId.value, { reject_reason: reviewComment.value })
    ElMessage.success('已驳回')
    reviewComment.value = ''
    await loadAllData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

const handleCompanyReviewComplete = async () => {
  try {
    await ElMessageBox.confirm('确定完成营运公司审核？请确保所有车位已处理。', '营运公司审核完成')
    actionLoading.value = true
    await bookingApi.companyReviewComplete(orderId.value, { review_comment: reviewComment.value })
    ElMessage.success('营运审核完成，已转媒体部复审')
    reviewComment.value = ''
    await loadAllData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

const handleFinalReviewApprove = async () => {
  try {
    await ElMessageBox.confirm('确定复审通过？将创建上刊订单。', '媒体部复审')
    actionLoading.value = true
    await bookingApi.finalReviewApprove(orderId.value, { review_comment: reviewComment.value })
    ElMessage.success('复审通过')
    reviewComment.value = ''
    await loadAllData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

const handleFinalReviewReject = async () => {
  if (!reviewComment.value) {
    ElMessage.warning('驳回时必须填写原因')
    return
  }
  try {
    await ElMessageBox.confirm('确定驳回该预订单？', '媒体部复审驳回', { type: 'warning' })
    actionLoading.value = true
    await bookingApi.finalReviewReject(orderId.value, { reject_reason: reviewComment.value })
    ElMessage.success('已驳回')
    reviewComment.value = ''
    await loadAllData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '操作失败')
  } finally {
    actionLoading.value = false
  }
}

// ========== WorkflowFormExpose 接口实现 ==========

/** 验证表单 */
const validate = async (): Promise<boolean> => {
  // 表单是只读展示，验证始终通过
  // 如果在营运公司审核阶段，可以检查是否所有车位都已确认
  if (mainOrder.value.booking_status === 3) {
    const pending = positionList.value.filter(p => p.confirm_status === 1 && p.allocation_status === 1)
    if (pending.length > 0) {
      ElMessage.warning(`还有 ${pending.length} 个车位未处理`)
      return false
    }
  }
  return true
}

/** 获取表单数据 */
const getFormData = async (): Promise<Record<string, any>> => {
  return {
    booking_order_id: orderId.value,
    booking_no: mainOrder.value.booking_no,
    review_comment: reviewComment.value,
    reject_reason: reviewComment.value,
  }
}

/** 保存表单数据 */
const save = async (): Promise<boolean> => {
  // 审批表单本身不需要保存（数据通过各审批API操作）
  return true
}

/** 审批前钩子 */
const onBeforeAudit = async (operationCode: string, operationName: string): Promise<boolean> => {
  // 驳回操作需要填写原因
  if (operationCode === 'disagree' || operationCode === 'reject') {
    if (!reviewComment.value) {
      ElMessage.warning('请填写驳回/不同意的理由')
      return false
    }
  }

  // 营运公司审核完成前检查待确认车位
  if (mainOrder.value.booking_status === 3 && operationCode === 'agree') {
    const pending = positionList.value.filter(p => p.confirm_status === 1 && p.allocation_status === 1)
    if (pending.length > 0) {
      try {
        await ElMessageBox.confirm(
          `还有 ${pending.length} 个车位未处理，确定继续审核？`,
          '提示',
          { type: 'warning' }
        )
      } catch {
        return false
      }
    }
  }

  return true
}

/** 审批后钩子 */
const onAfterAudit = (operationCode: string, operationName: string, success: boolean): void => {
  if (success) {
    ElMessage.success(`${operationName}操作成功`)
    loadAllData()
  }
}

// ========== 初始化 ==========
onMounted(async () => {
  // 从 props.data 初始化
  if (props.data && Object.keys(props.data).length > 0) {
    mainOrder.value = { ...props.data }
  }

  // 加载参考数据和业务数据
  await loadRefData()
  await loadAllData()
})

// 监听 orderId 变化
watch(() => orderId.value, (newId) => {
  if (newId) loadAllData()
})

// ========== 暴露方法 ==========
defineExpose({
  validate,
  getFormData,
  save,
  onBeforeAudit,
  onAfterAudit,
})
</script>

<style scoped lang="scss">
.booking-order-form {
  padding: 12px;
  position: relative;
  min-height: 400px;
}

.progress-card {
  margin-bottom: 12px;

  :deep(.el-card__body) {
    padding: 16px 20px;
  }
}

.action-card {
  .panel-title {
    font-weight: 600;
    font-size: 15px;
  }
}

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.loading-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.8);
  z-index: 10;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
</style>
