<template>
  <div class="booking-customers">
    <div class="layout">
      <div class="left">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <span>客户</span>
              <div class="right">
                <el-input v-model="keyword" size="small" placeholder="搜索客户/行业/标签" style="width: 220px" clearable @keyup.enter="loadCustomerList" />
                <el-button size="small" type="primary" @click="openNewCustomerDialog">
                  <el-icon><Plus /></el-icon>
                  新建客户
                </el-button>
              </div>
            </div>
          </template>

          <div class="filters">
            <div class="filters-row">
              <el-select v-model="filterIndustry" size="small" placeholder="行业分类" clearable style="width: 120px" @change="loadCustomerList">
                <el-option v-for="item in industryOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
              <el-select v-model="filterLevel" size="small" placeholder="客户等级" clearable style="width: 120px" @change="loadCustomerList">
                <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
              <el-select v-model="filterStatus" size="small" placeholder="状态" clearable style="width: 100px" @change="loadCustomerList">
                <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
              </el-select>
              <el-button size="small" @click="clearFilters">清空筛选</el-button>
            </div>
          </div>

          <div v-loading="loading" class="customer-list">
            <div
              v-for="c in customerList"
              :key="c.id"
              class="customer-item"
              :class="selectedCustomerId === c.id ? 'active' : ''"
              @click="selectCustomer(c)"
            >
              <div class="row">
                <div class="name">{{ c.company_name }}</div>
                <el-tag size="small" :type="getLevelTagType(c.customer_level)">
                  {{ getLevelText(c.customer_level) }}
                </el-tag>
              </div>
              <div class="subrow">
                <span class="muted">{{ getIndustryText(c.industry) }}</span>
                <span class="dot">·</span>
                <span class="muted">最近合作：{{ c.last_cooperation_date || '—' }}</span>
              </div>
              <div class="tags" v-if="c.industry_tags">
                <el-tag v-for="t in getTagsArray(c.industry_tags).slice(0, 6)" :key="t" size="small" type="info" effect="plain">{{ t }}</el-tag>
                <el-tag v-if="getTagsArray(c.industry_tags).length > 6" size="small" type="info" effect="plain">
                  +{{ getTagsArray(c.industry_tags).length - 6 }}
                </el-tag>
              </div>
            </div>
            <div v-if="!loading && customerList.length === 0" class="empty">没有匹配的客户</div>
          </div>

          <!-- 分页 -->
          <div class="pagination-wrap" v-if="total > 0">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              size="small"
              @size-change="loadCustomerList"
              @current-change="loadCustomerList"
            />
          </div>
        </el-card>
      </div>

      <div class="right">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <span>客户 360°</span>
              <div class="right">
                <el-tag v-if="selectedCustomer" size="small" type="info">{{ getIndustryText(selectedCustomer.industry) }}</el-tag>
                <el-tag
                  v-if="selectedCustomer"
                  size="small"
                  :type="getLevelTagType(selectedCustomer.customer_level)"
                >
                  {{ getLevelText(selectedCustomer.customer_level) }}
                </el-tag>
                <el-button v-if="selectedCustomer && !profileEdit" size="small" @click="startEditProfile">编辑档案</el-button>
                <el-button v-if="selectedCustomer && profileEdit" size="small" @click="cancelEditProfile">取消</el-button>
                <el-button v-if="selectedCustomer && profileEdit" size="small" type="primary" :loading="saving" @click="saveProfile">保存档案</el-button>
                <el-button v-if="selectedCustomer" size="small" @click="createOrderFromCustomer">
                  <el-icon><ShoppingCart /></el-icon>
                  为该客户创建订单
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="!selectedCustomer" class="empty">请选择一个客户查看详情</div>
          <div v-else class="customer-360">
            <el-tabs v-model="customerTab" class="main-tabs">
              <el-tab-pane name="profile" label="客户档案">
                <div class="grid-2">
                  <el-card shadow="never" class="subpanel">
                    <template #header>
                      <div class="subhead">档案信息</div>
                    </template>
                    <div class="kv">
                      <div class="k">公司名称</div>
                      <div class="v">
                        <el-input v-if="profileEdit" v-model="profileDraft.company_name" size="small" />
                        <span v-else>{{ selectedCustomer.company_name }}</span>
                      </div>
                      <div class="k">客户编码</div>
                      <div class="v">
                        <span>{{ selectedCustomer.customer_code }}</span>
                      </div>
                      <div class="k">行业分类</div>
                      <div class="v">
                        <el-select v-if="profileEdit" v-model="profileDraft.industry" size="small" style="width: 100%">
                          <el-option v-for="x in industryOptions" :key="x.value" :label="x.label" :value="x.value" />
                        </el-select>
                        <span v-else>{{ getIndustryText(selectedCustomer.industry) }}</span>
                      </div>
                      <div class="k">统一社会信用代码</div>
                      <div class="v">
                        <el-input v-if="profileEdit" v-model="profileDraft.credit_code" size="small" placeholder="请输入" />
                        <span v-else>{{ selectedCustomer.credit_code || '—' }}</span>
                      </div>
                      <div class="k">公司地址</div>
                      <div class="v">
                        <el-input v-if="profileEdit" v-model="profileDraft.company_address" size="small" placeholder="请输入" />
                        <span v-else>{{ selectedCustomer.company_address || '—' }}</span>
                      </div>
                      <div class="k">联系人</div>
                      <div class="v">
                        <el-input v-if="profileEdit" v-model="profileDraft.contact_name" size="small" placeholder="姓名" />
                        <span v-else>{{ selectedCustomer.contact_name || '—' }}</span>
                      </div>
                      <div class="k">联系电话</div>
                      <div class="v">
                        <el-input v-if="profileEdit" v-model="profileDraft.contact_phone" size="small" placeholder="手机号/座机" />
                        <span v-else>{{ selectedCustomer.contact_phone || '—' }}</span>
                      </div>
                      <div class="k">联系邮箱</div>
                      <div class="v">
                        <el-input v-if="profileEdit" v-model="profileDraft.contact_email" size="small" placeholder="邮箱" />
                        <span v-else>{{ selectedCustomer.contact_email || '—' }}</span>
                      </div>
                      <div class="k">客户等级</div>
                      <div class="v">
                        <el-select v-if="profileEdit" v-model="profileDraft.customer_level" size="small" style="width: 100%">
                          <el-option v-for="x in levelOptions" :key="x.value" :label="x.label" :value="x.value" />
                        </el-select>
                        <el-tag
                          v-else
                          size="small"
                          :type="getLevelTagType(selectedCustomer.customer_level)"
                        >
                          {{ getLevelText(selectedCustomer.customer_level) }}
                        </el-tag>
                      </div>
                      <div class="k">状态</div>
                      <div class="v">
                        <el-select v-if="profileEdit" v-model="profileDraft.status" size="small" style="width: 100%">
                          <el-option v-for="x in statusOptions" :key="x.value" :label="x.label" :value="x.value" />
                        </el-select>
                        <el-tag
                          v-else
                          size="small"
                          :type="getStatusTagType(selectedCustomer.status)"
                        >
                          {{ getStatusText(selectedCustomer.status) }}
                        </el-tag>
                      </div>
                      <div class="k">行业标签</div>
                      <div class="v">
                        <el-input v-if="profileEdit" v-model="profileDraft.industry_tags" size="small" placeholder="多个标签用逗号分隔" />
                        <span v-else>{{ selectedCustomer.industry_tags || '—' }}</span>
                      </div>
                      <div class="k">备注</div>
                      <div class="v">
                        <el-input v-if="profileEdit" v-model="profileDraft.remark" type="textarea" :rows="2" size="small" placeholder="请输入备注" />
                        <span v-else>{{ selectedCustomer.remark || '—' }}</span>
                      </div>
                    </div>
                  </el-card>

                  <el-card shadow="never" class="subpanel">
                    <template #header>
                      <div class="subhead">合作概览</div>
                    </template>
                    <div class="kpi-row">
                      <div class="kpi">
                        <div class="k">累计消费</div>
                        <div class="v">{{ formatAmount(selectedCustomer.total_amount) }}</div>
                      </div>
                      <div class="kpi">
                        <div class="k">合作次数</div>
                        <div class="v">{{ customerOrders.length }} 次</div>
                      </div>
                      <div class="kpi">
                        <div class="k">最近合作</div>
                        <div class="v">{{ selectedCustomer.last_cooperation_date || '—' }}</div>
                      </div>
                    </div>
                    <div class="coop-extra">
                      <div class="coop-item">
                        <div class="k">首次合作</div>
                        <div class="v">{{ selectedCustomer.first_cooperation_date || '—' }}</div>
                      </div>
                      <div class="coop-item">
                        <div class="k">创建时间</div>
                        <div class="v">{{ formatDateTime(selectedCustomer.create_datetime) }}</div>
                      </div>
                    </div>
                  </el-card>
                </div>
              </el-tab-pane>

              <el-tab-pane name="orders" label="历史订单">
                <el-card shadow="never" class="subpanel">
                  <template #header>
                    <div class="subhead">关联预订单</div>
                  </template>
                  <div v-loading="ordersLoading">
                    <el-table :data="customerOrders" size="small" height="400" empty-text="暂无订单">
                      <el-table-column prop="booking_no" label="订单号" width="180" />
                      <el-table-column prop="booking_status_display" label="状态" width="100">
                        <template #default="{ row }">
                          <el-tag size="small" :type="getOrderStatusType(row.booking_status)">{{ row.booking_status_display || '—' }}</el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="total_amount" label="金额(元)" width="120">
                        <template #default="{ row }">
                          {{ formatAmount(row.total_amount) }}
                        </template>
                      </el-table-column>
                      <el-table-column prop="ad_content" label="广告内容" min-width="200" show-overflow-tooltip />
                      <el-table-column prop="start_date" label="投放开始日期" width="120">
                        <template #default="{ row }">
                          {{ row.start_date ? formatDate(row.start_date) : '—' }}
                        </template>
                      </el-table-column>
                      <el-table-column prop="end_date" label="投放结束日期" width="120">
                        <template #default="{ row }">
                          {{ row.end_date ? formatDate(row.end_date) : '—' }}
                        </template>
                      </el-table-column>
                      <el-table-column prop="create_datetime" label="创建时间" width="160">
                        <template #default="{ row }">
                          {{ formatDateTime(row.create_datetime) }}
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" width="80" fixed="right">
                        <template #default="{ row }">
                          <el-button link size="small" @click="openOrder(row)">查看</el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-card>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 新建客户对话框 -->
    <el-dialog v-model="showNewCustomerDialog" title="新建客户" width="680" :close-on-click-modal="false">
      <el-form :model="newCustomerForm" :rules="newCustomerRules" ref="newCustomerFormRef" label-position="top">
        <div class="grid-2">
          <el-form-item label="客户编码" prop="customer_code">
            <el-input v-model="newCustomerForm.customer_code" placeholder="留空将自动生成" />
          </el-form-item>
          <el-form-item label="公司名称" prop="company_name">
            <el-input v-model="newCustomerForm.company_name" placeholder="请输入客户公司全称" />
          </el-form-item>
          <el-form-item label="行业分类" prop="industry">
            <el-select v-model="newCustomerForm.industry" placeholder="选择行业" style="width: 100%">
              <el-option v-for="x in industryOptions" :key="x.value" :label="x.label" :value="x.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="客户等级" prop="customer_level">
            <el-select v-model="newCustomerForm.customer_level" placeholder="选择等级" style="width: 100%">
              <el-option v-for="x in levelOptions" :key="x.value" :label="x.label" :value="x.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="统一社会信用代码" prop="credit_code">
            <el-input v-model="newCustomerForm.credit_code" placeholder="选填，18位" maxlength="18" />
          </el-form-item>
          <el-form-item label="公司地址" prop="company_address">
            <el-input v-model="newCustomerForm.company_address" placeholder="选填" />
          </el-form-item>
          <el-form-item label="联系人姓名" prop="contact_name">
            <el-input v-model="newCustomerForm.contact_name" placeholder="请输入" />
          </el-form-item>
          <el-form-item label="联系人电话" prop="contact_phone">
            <el-input v-model="newCustomerForm.contact_phone" placeholder="请输入" />
          </el-form-item>
          <el-form-item label="联系人邮箱" prop="contact_email">
            <el-input v-model="newCustomerForm.contact_email" placeholder="选填" />
          </el-form-item>
          <el-form-item label="状态" prop="status">
            <el-select v-model="newCustomerForm.status" placeholder="选择状态" style="width: 100%">
              <el-option v-for="x in statusOptions" :key="x.value" :label="x.label" :value="x.value" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="行业标签" prop="industry_tags">
          <el-input v-model="newCustomerForm.industry_tags" placeholder="多个标签用逗号分隔，如：食品,饮料" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="newCustomerForm.remark" type="textarea" :rows="3" placeholder="选填" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNewCustomerDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveNewCustomer">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { Plus, ShoppingCart } from '@element-plus/icons-vue'
import { ElMessage, FormInstance } from 'element-plus'
import { useRouter } from 'vue-router'
import { request } from '/@/utils/service'
import * as api from './api'

// 接口类型定义
interface Customer {
  id: string
  customer_code: string
  company_name: string
  credit_code?: string
  industry?: number
  industry_display?: string
  industry_tags?: string
  contact_name?: string
  contact_phone?: string
  contact_email?: string
  company_address?: string
  customer_level?: number
  customer_level_display?: string
  status: number
  status_display?: string
  first_cooperation_date?: string
  last_cooperation_date?: string
  total_amount?: number
  cooperation_count?: number
  remark?: string
  create_datetime?: string
  update_datetime?: string
}

interface BookingOrder {
  id: string
  booking_no: string
  booking_status: number
  booking_status_display?: string
  total_amount?: number
  ad_content?: string
  start_date?: string
  end_date?: string
  create_datetime?: string
}

const router = useRouter()

// API 前缀
const customerApiPrefix = '/api/CustomerModelViewSet/'
const bookingOrderApiPrefix = '/api/BookingOrderModelViewSet/'

// 选项定义
const industryOptions = [
  { value: 1, label: '快消' },
  { value: 2, label: '金融' },
  { value: 3, label: '地产' },
  { value: 4, label: '互联网' },
  { value: 5, label: '其他' },
]

const levelOptions = [
  { value: 1, label: '重点客户' },
  { value: 2, label: '普通客户' },
  { value: 3, label: '潜在客户' },
]

const statusOptions = [
  { value: 1, label: '活跃' },
  { value: 2, label: '休眠' },
  { value: 3, label: '流失' },
]

// 状态
const loading = ref(false)
const saving = ref(false)
const ordersLoading = ref(false)
const customerList = ref<Customer[]>([])
const selectedCustomerId = ref<string>('')
const selectedCustomer = ref<Customer | null>(null)
const customerOrders = ref<BookingOrder[]>([])
const customerTab = ref<'profile' | 'orders'>('profile')
const profileEdit = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 筛选
const keyword = ref('')
const filterIndustry = ref<number | undefined>(undefined)
const filterLevel = ref<number | undefined>(undefined)
const filterStatus = ref<number | undefined>(undefined)

// 新建客户
const showNewCustomerDialog = ref(false)
const newCustomerFormRef = ref<FormInstance>()
const newCustomerForm = reactive({
  customer_code: '',
  company_name: '',
  credit_code: '',
  industry: undefined as number | undefined,
  industry_tags: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  company_address: '',
  customer_level: 2,
  status: 1,
  remark: '',
})

const newCustomerRules = {
  company_name: [{ required: true, message: '公司名称必填', trigger: 'blur' }],
  status: [{ required: true, message: '状态必填', trigger: 'change' }],
}

// 编辑档案草稿
const profileDraft = reactive({
  company_name: '',
  credit_code: '',
  industry: undefined as number | undefined,
  industry_tags: '',
  contact_name: '',
  contact_phone: '',
  contact_email: '',
  company_address: '',
  customer_level: undefined as number | undefined,
  status: 1,
  remark: '',
})

// 辅助函数
const getIndustryText = (val?: number) => {
  const item = industryOptions.find(x => x.value === val)
  return item ? item.label : '—'
}

const getLevelText = (val?: number) => {
  const item = levelOptions.find(x => x.value === val)
  return item ? item.label : '—'
}

const getLevelTagType = (val?: number) => {
  if (val === 1) return 'warning' // 重点客户
  if (val === 3) return 'info'    // 潜在客户
  return ''                        // 普通客户
}

const getStatusText = (val?: number) => {
  const item = statusOptions.find(x => x.value === val)
  return item ? item.label : '—'
}

const getStatusTagType = (val?: number) => {
  if (val === 1) return 'success' // 活跃
  if (val === 2) return 'warning' // 休眠
  if (val === 3) return 'danger'  // 流失
  return 'info'
}

const getOrderStatusType = (val?: number) => {
  if (val === 4 || val === 5) return 'success' // 已通过、已完成
  if (val === 2 || val === 3) return 'warning' // 待审批、审批中
  if (val === 6 || val === 7) return 'danger'  // 已取消、已驳回
  return 'info'
}

const getTagsArray = (tags?: string) => {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(Boolean)
}

const formatAmount = (val?: number | string) => {
  if (!val) return '—'
  const num = Number(val)
  if (isNaN(num)) return '—'
  return `¥${num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const formatDateTime = (val?: string) => {
  if (!val) return '—'
  return val.slice(0, 16).replace('T', ' ')
}

const formatDate = (val?: string) => {
  if (!val) return '—'
  return val.slice(0, 10)
}

// 加载客户列表
const loadCustomerList = async () => {
  try {
    loading.value = true
    const params: any = {
      page: currentPage.value,
      limit: pageSize.value,
      delete_mark: 0,
      enabled_mark: 1,
    }
    if (keyword.value) {
      params.search = keyword.value
    }
    if (filterIndustry.value !== undefined) {
      params.industry = filterIndustry.value
    }
    if (filterLevel.value !== undefined) {
      params.customer_level = filterLevel.value
    }
    if (filterStatus.value !== undefined) {
      params.status = filterStatus.value
    }

    const res = await request({
      url: customerApiPrefix,
      method: 'get',
      params,
    })

    if (res && res.data) {
      if (Array.isArray(res.data)) {
        customerList.value = res.data
        total.value = res.data.length
      } else if (res.data.results) {
        customerList.value = res.data.results
        total.value = res.data.count || res.data.results.length
      }
    }

    // 如果没有选中客户且列表有数据，选中第一个
    if (!selectedCustomerId.value && customerList.value.length > 0) {
      selectCustomer(customerList.value[0])
    }
  } catch (error) {
    console.error('加载客户列表失败:', error)
    ElMessage.error('加载客户列表失败')
  } finally {
    loading.value = false
  }
}

// 选中客户
const selectCustomer = (customer: Customer) => {
  selectedCustomerId.value = customer.id
  selectedCustomer.value = customer
  profileEdit.value = false
  customerTab.value = 'profile'
  loadCustomerOrders(customer.id)
}

// 加载客户的关联订单
const loadCustomerOrders = async (customerId: string) => {
  try {
    ordersLoading.value = true
    const res = await request({
      url: bookingOrderApiPrefix,
      method: 'get',
      params: {
        customer_id: customerId,
        limit: 100,
        delete_mark: 0,
      },
    })

    if (res && res.data) {
      if (Array.isArray(res.data)) {
        customerOrders.value = res.data
      } else if (res.data.results) {
        customerOrders.value = res.data.results
      }
    }
  } catch (error) {
    console.error('加载客户订单失败:', error)
    customerOrders.value = []
  } finally {
    ordersLoading.value = false
  }
}

// 清空筛选
const clearFilters = () => {
  keyword.value = ''
  filterIndustry.value = undefined
  filterLevel.value = undefined
  filterStatus.value = undefined
  currentPage.value = 1
  loadCustomerList()
}

// 开始编辑档案
const startEditProfile = () => {
  if (!selectedCustomer.value) return
  const c = selectedCustomer.value
  profileDraft.company_name = c.company_name || ''
  profileDraft.credit_code = c.credit_code || ''
  profileDraft.industry = c.industry
  profileDraft.industry_tags = c.industry_tags || ''
  profileDraft.contact_name = c.contact_name || ''
  profileDraft.contact_phone = c.contact_phone || ''
  profileDraft.contact_email = c.contact_email || ''
  profileDraft.company_address = c.company_address || ''
  profileDraft.customer_level = c.customer_level
  profileDraft.status = c.status
  profileDraft.remark = c.remark || ''
  profileEdit.value = true
  customerTab.value = 'profile'
}

// 取消编辑
const cancelEditProfile = () => {
  profileEdit.value = false
}

// 保存档案
const saveProfile = async () => {
  if (!selectedCustomer.value) return
  try {
    saving.value = true
    const data = {
      id: selectedCustomer.value.id,
      company_name: profileDraft.company_name,
      credit_code: profileDraft.credit_code || null,
      industry: profileDraft.industry,
      industry_tags: profileDraft.industry_tags || null,
      contact_name: profileDraft.contact_name || null,
      contact_phone: profileDraft.contact_phone || null,
      contact_email: profileDraft.contact_email || null,
      company_address: profileDraft.company_address || null,
      customer_level: profileDraft.customer_level,
      status: profileDraft.status,
      remark: profileDraft.remark || null,
    }

    await api.UpdateObj(data as any)
    ElMessage.success('保存成功')
    profileEdit.value = false
    loadCustomerList()
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error(error?.response?.data?.msg || '保存失败')
  } finally {
    saving.value = false
  }
}

// 打开新建客户对话框
const openNewCustomerDialog = () => {
  newCustomerForm.customer_code = ''
  newCustomerForm.company_name = ''
  newCustomerForm.credit_code = ''
  newCustomerForm.industry = undefined
  newCustomerForm.industry_tags = ''
  newCustomerForm.contact_name = ''
  newCustomerForm.contact_phone = ''
  newCustomerForm.contact_email = ''
  newCustomerForm.company_address = ''
  newCustomerForm.customer_level = 2
  newCustomerForm.status = 1
  newCustomerForm.remark = ''
  showNewCustomerDialog.value = true
}

// 保存新客户
const saveNewCustomer = async () => {
  if (!newCustomerFormRef.value) return
  try {
    await newCustomerFormRef.value.validate()
    saving.value = true

    const data: any = {
      company_name: newCustomerForm.company_name,
      status: newCustomerForm.status,
    }
    if (newCustomerForm.customer_code) data.customer_code = newCustomerForm.customer_code
    if (newCustomerForm.credit_code) data.credit_code = newCustomerForm.credit_code
    if (newCustomerForm.industry !== undefined) data.industry = newCustomerForm.industry
    if (newCustomerForm.industry_tags) data.industry_tags = newCustomerForm.industry_tags
    if (newCustomerForm.contact_name) data.contact_name = newCustomerForm.contact_name
    if (newCustomerForm.contact_phone) data.contact_phone = newCustomerForm.contact_phone
    if (newCustomerForm.contact_email) data.contact_email = newCustomerForm.contact_email
    if (newCustomerForm.company_address) data.company_address = newCustomerForm.company_address
    if (newCustomerForm.customer_level !== undefined) data.customer_level = newCustomerForm.customer_level
    if (newCustomerForm.remark) data.remark = newCustomerForm.remark

    const res = await api.AddObj(data)
    ElMessage.success('创建成功')
    showNewCustomerDialog.value = false
    loadCustomerList()

    // 选中新创建的客户
    if (res && res.data && res.data.id) {
      setTimeout(() => {
        const newCustomer = customerList.value.find(c => c.id === res.data.id)
        if (newCustomer) {
          selectCustomer(newCustomer)
        }
      }, 500)
    }
  } catch (error: any) {
    if (error !== false) {  // 排除表单验证失败
      console.error('创建失败:', error)
      ElMessage.error(error?.response?.data?.msg || '创建失败')
    }
  } finally {
    saving.value = false
  }
}

// 为客户创建订单
const createOrderFromCustomer = () => {
  if (!selectedCustomer.value) return
  const c = selectedCustomer.value
  sessionStorage.setItem(
    'bookingCustomerSnapshot',
    JSON.stringify({
      id: c.id,
      name: c.company_name,
      industry: getIndustryText(c.industry),
      contact: c.contact_name,
    })
  )
  router.push({ path: '/booking_manage/booking_order/BookingOrderModelViewSet', query: { create: '1', customerId: c.id } })
}

// 打开订单详情
const openOrder = (order: BookingOrder) => {
  router.push({ path: '/booking_manage/booking_order/BookingOrderModelViewSet', query: { order: order.id } })
}

// 初始化
onMounted(() => {
  loadCustomerList()
})
</script>

<style scoped>
.booking-customers {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.layout {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 12px;
  height: calc(100vh - 100px);
}

.panel {
  height: 100%;
  overflow: hidden;
  border-radius: 10px;
}

.panel :deep(.el-card__body) {
  height: calc(100% - 48px);
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.panel-header .right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 10px;
}

.filters-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.customer-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  overflow-y: auto;
}

.customer-item {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 10px 12px;
  cursor: pointer;
  background: #fff;
  transition: all 0.2s;
}

.customer-item:hover {
  border-color: var(--el-color-primary-light-5);
}

.customer-item.active {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px var(--el-color-primary-light-8);
}

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.name {
  font-weight: 800;
  color: #303133;
}

.subrow {
  margin-top: 6px;
  font-size: 12px;
}

.dot {
  margin: 0 6px;
  color: #c0c4cc;
}

.muted {
  color: #909399;
  font-size: 12px;
}

.tags {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.empty {
  color: #909399;
  background: #fafafa;
  border: 1px dashed #dcdfe6;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
}

.pagination-wrap {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.subpanel {
  border-radius: 10px;
}

.subhead {
  font-weight: 700;
}

.kv {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 8px 10px;
  align-items: center;
}

.kv .k {
  color: #909399;
  font-size: 12px;
}

.kpi-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 10px;
}

.kpi {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 10px;
}

.kpi .k {
  color: #909399;
  font-size: 12px;
}

.kpi .v {
  margin-top: 4px;
  font-weight: 800;
}

.coop-extra {
  margin-top: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.coop-item {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 10px;
}

.coop-item .k {
  color: #909399;
  font-size: 12px;
}

.coop-item .v {
  margin-top: 4px;
  font-weight: 800;
}

.customer-360 {
  flex: 1;
  overflow: auto;
}
</style>
