<template>
  <div class="agents-page">
    <div class="layout">
      <div class="left">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <span>代理商工作台</span>
              <div class="right">
                <el-select v-model="leftMode" size="small" style="width: 140px">
                  <el-option label="注册审核" value="applications" />
                  <el-option label="代理商档案" value="agents" />
                </el-select>
                <el-input v-model="keyword" size="small" placeholder="公司/联系人/账号" style="width: 220px" @keyup.enter="loadAgentList" />
                <el-button size="small" type="primary" @click="openNewAgentDialog">
                  <el-icon><Plus /></el-icon>
                  添加代理商
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="leftMode === 'applications'" class="list">
            <div
              v-for="a in filteredApplications"
              :key="a.id"
              class="item"
              :class="selectedAppId === a.id ? 'active' : ''"
              @click="selectedAppId = a.id"
            >
              <div class="row">
                <div class="name">{{ a.company }}</div>
                <el-tag size="small" :type="appStatusType(a.status)">{{ a.status }}</el-tag>
              </div>
              <div class="subrow">
                <span class="muted">{{ a.name }}</span>
                <span class="dot">·</span>
                <span class="muted">{{ a.phone }}</span>
              </div>
              <div class="subrow">
                <span class="muted">提交：{{ a.submittedAt }}</span>
              </div>
            </div>
            <div v-if="filteredApplications.length === 0" class="empty">暂无注册申请</div>
          </div>

          <div v-else v-loading="loading" class="list">
            <div
              v-for="a in filteredAgents"
              :key="a.id"
              class="item"
              :class="selectedAgentId === a.id ? 'active' : ''"
              @click="selectAgent(a)"
            >
              <div class="row">
                <div class="name">{{ a.company_name }}</div>
                <el-tag size="small" :type="a.enabled_mark === 1 ? 'success' : 'info'">{{ a.enabled_mark === 1 ? '启用' : '停用' }}</el-tag>
              </div>
              <div class="subrow">
                <span class="muted">等级：{{ getLevelText(a.cooperation_level) }}</span>
                <span class="dot">·</span>
                <span class="muted">合同：{{ getContractStatus(a) }}</span>
              </div>
              <div class="subrow">
                <span class="muted">编码：{{ a.agent_code || '未分配' }}</span>
              </div>
            </div>
            <div v-if="filteredAgents.length === 0 && !loading" class="empty">暂无代理商档案</div>
          </div>
        </el-card>
      </div>

      <div class="right">
        <el-card shadow="never" class="panel">
          <template #header>
            <div class="panel-header">
              <span>{{ rightTitle }}</span>
              <div class="right" v-if="leftMode === 'agents' && selectedAgent">
                <el-tag size="small" :type="selectedAgent.enabled_mark === 1 ? 'success' : 'info'">{{ selectedAgent.enabled_mark === 1 ? '启用' : '停用' }}</el-tag>
                <el-button size="small" @click="toggleAgentStatus">
                  {{ selectedAgent.enabled_mark === 1 ? '停用' : '启用' }}
                </el-button>
              </div>
              <div class="right" v-else-if="leftMode === 'applications' && selectedApplication">
                <el-tag size="small" :type="appStatusType(selectedApplication.status)">{{ selectedApplication.status }}</el-tag>
                <el-button
                  v-if="selectedApplication.status === '待审核'"
                  size="small"
                  type="success"
                  @click="approveSelectedApplication"
                >
                  通过并分配账号
                </el-button>
                <el-button
                  v-if="selectedApplication.status === '待审核'"
                  size="small"
                  type="danger"
                  @click="rejectSelectedApplication"
                >
                  驳回
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="leftMode === 'applications'">
            <div v-if="!selectedApplication" class="empty">请选择一条注册申请查看详情</div>
            <div v-else class="detail">
              <div class="grid-2">
                <el-card shadow="never" class="subpanel">
                  <template #header><div class="subhead">注册信息</div></template>
                  <div class="kv">
                    <div class="k">公司</div><div class="v">{{ selectedApplication.company }}</div>
                    <div class="k">联系人</div><div class="v">{{ selectedApplication.name }}</div>
                    <div class="k">手机号</div><div class="v">{{ selectedApplication.phone }}</div>
                    <div class="k">邮箱</div><div class="v">{{ selectedApplication.email || '-' }}</div>
                    <div class="k">提交时间</div><div class="v">{{ selectedApplication.submittedAt }}</div>
                  </div>
                </el-card>
                <el-card shadow="never" class="subpanel">
                  <template #header><div class="subhead">审核流转</div></template>
                  <div class="kv">
                    <div class="k">状态</div><div class="v">{{ selectedApplication.status }}</div>
                    <div class="k">审核人</div><div class="v">{{ selectedApplication.auditedBy || '-' }}</div>
                    <div class="k">审核时间</div><div class="v">{{ selectedApplication.auditedAt || '-' }}</div>
                    <div class="k">备注</div><div class="v">{{ selectedApplication.auditNote || '-' }}</div>
                    <div class="k">关联代理商</div><div class="v">{{ selectedApplication.linkedAgentId || '-' }}</div>
                  </div>
                </el-card>
              </div>
            </div>
          </div>

          <div v-else>
            <div v-if="!selectedAgent" class="empty">请选择一个代理商查看详情</div>
            <div v-else class="detail">
              <el-tabs v-model="agentTab">
                <el-tab-pane label="基础信息" name="base">
                  <div class="grid-2">
                    <el-card shadow="never" class="subpanel">
                      <template #header><div class="subhead">公司与合作</div></template>
                      <div class="form-grid">
                        <el-form label-position="top" :model="agentDraft">
                          <el-form-item label="公司名称">
                            <el-input v-model="agentDraft.company_name" />
                          </el-form-item>
                          <el-form-item label="统一社会信用代码">
                            <el-input v-model="agentDraft.credit_code" placeholder="18位信用代码" />
                          </el-form-item>
                          <el-form-item label="合作等级">
                            <el-select v-model="agentDraft.cooperation_level" style="width: 100%">
                              <el-option label="A级（核心）" :value="1" />
                              <el-option label="B级（重要）" :value="2" />
                              <el-option label="C级（普通）" :value="3" />
                            </el-select>
                          </el-form-item>
                          <!-- <el-form-item label="合同状态">
                            <el-tag size="small" :type="getContractStatusType(selectedAgent)">
                              {{ getContractStatus(selectedAgent) }}
                            </el-tag>
                          </el-form-item>
                          <div class="grid-2">
                            <el-form-item label="合同开始">
                              <el-date-picker v-model="agentDraft.contract_start_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" placeholder="YYYY-MM-DD" />
                            </el-form-item>
                            <el-form-item label="合同结束">
                              <el-date-picker v-model="agentDraft.contract_end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" placeholder="YYYY-MM-DD" />
                            </el-form-item>
                          </div> -->
                        </el-form>
                      </div>
                    </el-card>
                    <el-card shadow="never" class="subpanel">
                      <template #header><div class="subhead">联系人与结算</div></template>
                      <div class="subblock">
                        <div class="subhead2">联系信息</div>
                        <el-form label-position="top" :model="agentDraft">
                          <el-form-item label="联系电话">
                            <el-input v-model="agentDraft.contact_phone" placeholder="请输入" />
                          </el-form-item>
                          <el-form-item label="联系邮箱">
                            <el-input v-model="agentDraft.contact_email" placeholder="请输入" />
                          </el-form-item>
                          <el-form-item label="业务负责人">
                            <el-input v-model="agentDraft.business_manager" placeholder="请输入" />
                          </el-form-item>
                        </el-form>
                      </div>

                      <div class="subblock">
                        <div class="subhead2">结算信息</div>
                        <el-form label-position="top" :model="agentDraft">
                          <el-form-item label="结算方式">
                            <el-select v-model="agentDraft.settlement_type" style="width: 100%" placeholder="请选择">
                              <el-option label="月结" :value="1" />
                              <el-option label="季结" :value="2" />
                              <el-option label="年结" :value="3" />
                            </el-select>
                          </el-form-item>
                          <el-form-item label="开户行">
                            <el-input v-model="agentDraft.bank_name" placeholder="请输入" />
                          </el-form-item>
                          <el-form-item label="银行账号">
                            <el-input v-model="agentDraft.bank_account" placeholder="请输入" />
                          </el-form-item>
                        </el-form>
                      </div>
                    </el-card>
                  </div>
                  <div style="display: flex; justify-content: flex-end; margin-top: 16px; padding-top: 16px; border-top: 1px solid #ebeef5;">
                    <el-button size="small" type="primary" @click="saveAgent" :disabled="!agentDraft.company_name?.trim()" :loading="saving">保存</el-button>
                  </div>
                </el-tab-pane>

                <el-tab-pane label="账号分配" name="account">
                  <el-card shadow="never" class="subpanel">
                    <template #header>
                      <div class="subhead-row">
                        <div class="subhead">已分配账号</div>
                        <el-button size="small" @click="loadAgentUsers">刷新</el-button>
                      </div>
                    </template>
                    <div v-loading="usersLoading">
                      <el-table :data="agentUsers" size="small" empty-text="暂无已分配账号" max-height="200">
                        <el-table-column prop="username" label="账号" width="150" />
                        <el-table-column prop="name" label="姓名" width="150" />
                        <el-table-column prop="mobile" label="手机号" width="130" />
                        <el-table-column prop="is_active" label="状态" width="80">
                          <template #default="{ row }">
                            <el-tag size="small" :type="row.is_active ? 'success' : 'info'">
                              {{ row.is_active ? '启用' : '禁用' }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="create_datetime" label="创建时间" min-width="160">
                          <template #default="{ row }">
                            {{ formatDateTime(row.create_datetime) }}
                          </template>
                        </el-table-column>
                      </el-table>
                    </div>
                  </el-card>

                  <el-card shadow="never" class="subpanel mt12">
                    <template #header><div class="subhead">新建账号</div></template>
                    <div class="kv">
                      <div class="k">代理商编码</div><div class="v">{{ selectedAgent.agent_code || '未分配' }}</div>
                      <div class="k">公司名称</div><div class="v">{{ selectedAgent.company_name }}</div>
                    </div>
                    <div class="account-form mt12">
                      <el-form :model="{ username: accountUsername, name: accountName }" label-position="top" size="default">
                        <div class="form-row">
                          <el-form-item label="账号" class="form-item-flex">
                            <el-input v-model="accountUsername" placeholder="请输入账号" clearable />
                          </el-form-item>
                          <el-form-item label="姓名" class="form-item-flex">
                            <el-input v-model="accountName" placeholder="请输入姓名" clearable />
                          </el-form-item>
                        </div>
                        <el-form-item>
                          <el-button type="primary" :disabled="!accountUsername.trim() || !accountName.trim()" :loading="saving" @click="allocateAccount">
                            <el-icon><Plus /></el-icon>
                            创建账号
                          </el-button>
                        </el-form-item>
                      </el-form>
                    </div>
                    <div class="muted mt12">提示：新账号默认密码为 123456，创建后请通知代理商及时修改密码</div>
                  </el-card>
                </el-tab-pane>

                <el-tab-pane label="资源授权" name="auth">
                  <!-- 已授权线路 -->
                  <el-card shadow="never" class="subpanel">
                    <template #header>
                      <div class="subhead-row">
                        <div class="subhead">已授权线路</div>
                        <el-tag size="small" type="success">{{ authorizedRoadlines.length }} 条</el-tag>
                      </div>
                    </template>
                    <div class="authorized-list">
                      <template v-if="authorizedRoadlines.length > 0">
                        <el-tag
                          v-for="r in authorizedRoadlines"
                          :key="r.id"
                          closable
                          size="default"
                          type="success"
                          effect="plain"
                          class="authorized-tag"
                          @close="removeAuthorizedRoadline(r.id)"
                        >
                          {{ r.ygc_code || r.normal_code || '' }} {{ r.line_name }}
                        </el-tag>
                      </template>
                      <div v-else class="empty-inline">暂无已授权线路</div>
                    </div>
                  </el-card>

                  <!-- 可授权线路 -->
                  <el-card shadow="never" class="subpanel mt12">
                    <template #header>
                      <div class="subhead-row">
                        <div class="subhead">可授权线路</div>
                        <div class="right">
                          <el-button size="small" @click="loadRoadlines" :loading="roadlinesLoading">刷新线路</el-button>
                          <el-button size="small" @click="selectAllFiltered">全选当前筛选</el-button>
                          <el-button size="small" @click="clearSelectedResources">清空授权</el-button>
                          <el-button size="small" type="primary" :loading="authSaving" @click="saveResourceAuth">保存授权</el-button>
                        </div>
                      </div>
                    </template>

                    <div class="filters">
                      <el-input v-model="resourceKeyword" size="small" placeholder="搜索线路编号/名称" style="width: 260px" />
                      <el-select v-model="resourceCompanyFilter" size="small" clearable placeholder="所属公司" style="width: 180px">
                        <el-option v-for="c in companyOptions" :key="c" :label="c" :value="c" />
                      </el-select>
                    </div>

                    <div class="auth-meta">
                      <el-tag size="small" type="info">已勾选：{{ allowedResourceIds.length }} 条线路</el-tag>
                      <el-tag size="small" type="warning">当前筛选：{{ filteredResources.length }} 条</el-tag>
                      <el-tag size="small">全部线路：{{ roadlines.length }} 条</el-tag>
                    </div>

                    <div v-loading="roadlinesLoading" class="auth-list-wrap">
                      <el-checkbox-group v-model="allowedResourceIds" class="auth-list">
                        <div v-for="r in filteredResources" :key="r.id" class="auth-item">
                          <el-checkbox :label="String(r.id)">
                            <div class="auth-label">
                              <div class="primary">
                                <span class="code">{{ r.ygc_code || r.normal_code || '—' }}</span>
                                <span class="line-name">{{ r.line_name }}</span>
                              </div>
                              <div class="muted">{{ r.company_name || '—' }}<span v-if="r.bus_count"> · {{ r.bus_count }} 辆车</span></div>
                            </div>
                          </el-checkbox>
                        </div>
                        <div v-if="filteredResources.length === 0 && !roadlinesLoading" class="empty">暂无可选线路（请先在线路管理页维护线路数据）</div>
                      </el-checkbox-group>
                    </div>
                  </el-card>
                </el-tab-pane>

                <!-- <el-tab-pane label="刊例价" name="rate">
                  <el-card shadow="never" class="subpanel">
                    <template #header><div class="subhead">代理商独立刊例价体系</div></template>
                    <div class="grid-2">
                      <el-card shadow="never" class="subpanel inner">
                        <template #header><div class="subhead2">默认折扣(%)</div></template>
                        <el-input-number v-model="defaultDiscount" :min="50" :max="120" style="width: 100%" />
                      </el-card>
                      <el-card shadow="never" class="subpanel inner">
                        <template #header><div class="subhead2">分类型折扣(%)</div></template>
                        <div class="discounts">
                          <div class="disc">
                            <div class="k">车身</div>
                            <el-input-number v-model="typeDiscounts.bus" :min="50" :max="120" size="small" />
                          </div>
                          <div class="disc">
                            <div class="k">站台</div>
                            <el-input-number v-model="typeDiscounts.station" :min="50" :max="120" size="small" />
                          </div>
                          <div class="disc">
                            <div class="k">移动电视</div>
                            <el-input-number v-model="typeDiscounts.tv" :min="50" :max="120" size="small" />
                          </div>
                          <div class="disc-actions">
                            <el-button size="small" @click="applyTypeDiscounts">应用到该代理商</el-button>
                          </div>
                        </div>
                      </el-card>
                    </div>
                    <div class="mt12 kv">
                      <div class="k">说明</div>
                      <div class="v">折扣为按刊例价百分比计价，100% 表示不打折</div>
                    </div>
                  </el-card>
                </el-tab-pane> -->
              </el-tabs>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 新建代理商对话框 -->
    <el-dialog v-model="showNewAgentDialog" title="添加代理商" width="600" :close-on-click-modal="false">
      <el-form :model="newAgentForm" :rules="newAgentRules" ref="newAgentFormRef" label-position="top">
        <el-form-item label="代理商编码" prop="agent_code">
          <el-input v-model="newAgentForm.agent_code" placeholder="系统自动生成" :readonly="true">
            <template #append>
              <el-button @click="generateAgentCode" :icon="Refresh" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="公司名称" prop="company_name">
          <el-input v-model="newAgentForm.company_name" placeholder="请输入代理商公司全称" />
        </el-form-item>
        <el-form-item label="合作等级" prop="cooperation_level">
          <el-select v-model="newAgentForm.cooperation_level" placeholder="选择等级" style="width: 100%">
            <el-option label="A级（核心）" :value="1" />
            <el-option label="B级（重要）" :value="2" />
            <el-option label="C级（普通）" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系电话" prop="contact_phone">
          <el-input v-model="newAgentForm.contact_phone" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="联系邮箱" prop="contact_email">
          <el-input v-model="newAgentForm.contact_email" placeholder="请输入" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNewAgentDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveNewAgent">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { request } from '/@/utils/service'
import * as api from './api'

// 系统用户 API
const userApiPrefix = '/api/system/user/'
// 线路 API
const roadlineApiPrefix = '/api/RoadlineModelViewSet/'
// 资源授权 API
const authApiPrefix = '/api/AgentResourceAuthModelViewSet/'

type LeftMode = 'applications' | 'agents'

// 代理商接口类型（对应后端模型）
interface Agent {
  id: string
  agent_code: string
  company_name: string
  credit_code?: string
  legal_person?: string
  registered_capital?: number
  established_date?: string
  company_address?: string
  contact_phone?: string
  contact_email?: string
  cooperation_level: number
  contract_start_date?: string
  contract_end_date?: string
  settlement_type?: number
  bank_name?: string
  bank_account?: string
  business_manager?: string
  remark?: string
  enabled_mark: number
  create_datetime?: string
  update_datetime?: string
}

// 注册申请类型（暂无后端接口，使用本地数据）
interface AgentApplication {
  id: string
  company: string
  name: string
  phone: string
  email?: string
  submittedAt: string
  status: '待审核' | '已通过' | '已驳回'
  auditedBy?: string
  auditedAt?: string
  auditNote?: string
  linkedAgentId?: string
}

// 线路资源类型
interface Roadline {
  id: string
  ygc_code?: string
  normal_code?: string
  line_name: string
  company_name?: string
  bus_count?: number
}

// 状态
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const leftMode = ref<LeftMode>('agents')

// 代理商列表（从API获取）
const agentList = ref<Agent[]>([])
const selectedAgentId = ref<string>('')
const selectedAgent = computed(() => agentList.value.find(a => a.id === selectedAgentId.value) || null)

// 注册申请列表（暂无API，本地数据）
const agentApplications = ref<AgentApplication[]>([])
const selectedAppId = ref('')
const selectedApplication = computed(() => agentApplications.value.find(a => a.id === selectedAppId.value) || null)

// 线路资源列表
const roadlines = ref<Roadline[]>([])
const roadlinesLoading = ref(false)
const allowedResourceIds = ref<string[]>([])  // 当前勾选的（用于编辑）
const savedAuthRecords = ref<any[]>([])  // 当前代理商的授权记录
const allAuthorizedResourceIds = ref<Set<string>>(new Set())  // 所有已被授权的线路ID（所有代理商）
const authSaving = ref(false)
const defaultDiscount = ref(100)

const rightTitle = computed(() => {
  if (leftMode.value === 'applications') return '注册审核详情'
  return '代理商档案'
})

// 辅助函数
const getLevelText = (val?: number) => {
  if (val === 1) return 'A级'
  if (val === 2) return 'B级'
  return 'C级'
}

const getContractStatus = (agent: Agent) => {
  if (!agent.contract_start_date || !agent.contract_end_date) return '未签'
  const now = new Date()
  const end = new Date(agent.contract_end_date)
  if (end < now) return '到期'
  return '有效'
}

const getContractStatusType = (agent: Agent) => {
  const status = getContractStatus(agent)
  if (status === '有效') return 'success'
  if (status === '到期') return 'danger'
  return 'info'
}

const formatDateTime = (val?: string) => {
  if (!val) return '-'
  return val.slice(0, 16).replace('T', ' ')
}

const appStatusType = (s: AgentApplication['status']) => {
  if (s === '待审核') return 'warning'
  if (s === '已通过') return 'success'
  return 'info'
}

// 筛选
const filteredApplications = computed(() => {
  const kw = keyword.value.trim()
  const list = [...agentApplications.value]
  if (!kw) return list
  return list.filter(a => {
    if (a.company.includes(kw)) return true
    if (a.name.includes(kw)) return true
    if (a.phone.includes(kw)) return true
    return false
  })
})

const filteredAgents = computed(() => {
  const kw = keyword.value.trim()
  const list = [...agentList.value]
  if (!kw) return list
  return list.filter(a => {
    if (a.company_name.includes(kw)) return true
    if ((a.contact_phone || '').includes(kw)) return true
    if ((a.agent_code || '').includes(kw)) return true
    return false
  })
})

// 代理商编辑草稿
const agentDraft = reactive<Partial<Agent>>({
  id: '',
  company_name: '',
  credit_code: '',
  cooperation_level: 3,
  contract_start_date: '',
  contract_end_date: '',
  settlement_type: undefined,
  bank_name: '',
  bank_account: '',
  contact_phone: '',
  contact_email: '',
  business_manager: '',
})

const agentTab = ref<'base' | 'account' | 'auth' | 'rate'>('base')
const accountUsername = ref('')
const accountName = ref('')
const typeDiscounts = reactive({ bus: 100, station: 100, tv: 100 })

// 代理商已分配用户
const usersLoading = ref(false)
const agentUsers = ref<any[]>([])

// 资源筛选
const resourceKeyword = ref('')
const resourceCompanyFilter = ref<string>('')

const companyOptions = computed(() => {
  const set = new Set<string>()
  for (const r of roadlines.value) {
    if (r.company_name) set.add(r.company_name)
  }
  return Array.from(set).sort((a, b) => a.localeCompare(b, 'zh-Hans-CN'))
})

// 当前代理商已授权的线路ID集合
const currentAgentAuthorizedIds = computed(() => {
  return new Set(savedAuthRecords.value.map((r: any) => String(r.resource_id)))
})

const filteredResources = computed(() => {
  const kw = resourceKeyword.value.trim()
  const company = resourceCompanyFilter.value
  const currentAgentIds = currentAgentAuthorizedIds.value
  
  return roadlines.value.filter(r => {
    const rid = String(r.id)
    // 排除已被其他代理商授权的线路（但保留当前代理商自己授权的）
    if (allAuthorizedResourceIds.value.has(rid) && !currentAgentIds.has(rid)) {
      return false
    }
    if (company && r.company_name !== company) return false
    if (!kw) return true
    const code = r.ygc_code || r.normal_code || ''
    const hay = `${code} ${r.line_name} ${r.company_name || ''}`
    return hay.includes(kw)
  })
})

// 已授权线路列表（根据数据库保存的记录）
const authorizedRoadlines = computed(() => {
  // 从已保存的授权记录中获取 resource_id，与线路列表匹配
  const savedIds = new Set(savedAuthRecords.value.map((r: any) => String(r.resource_id)))
  return roadlines.value.filter(r => savedIds.has(String(r.id)))
})

// 移除单条已授权线路（直接调用删除 API）
const removeAuthorizedRoadline = async (roadlineId: string) => {
  // 找到对应的授权记录
  const authRecord = savedAuthRecords.value.find((r: any) => String(r.resource_id) === String(roadlineId))
  if (!authRecord) return
  
  try {
    await request({
      url: `${authApiPrefix}${authRecord.id}/`,
      method: 'delete',
    })
    ElMessage.success('已移除授权')
    // 刷新授权列表和全局授权状态
    await Promise.all([loadAgentAuthResources(), loadAllAuthorizedResources()])
  } catch (error: any) {
    console.error('移除授权失败:', error)
    ElMessage.error(error?.response?.data?.msg || '移除授权失败')
  }
}

// 加载所有已被授权的线路（所有代理商）
const loadAllAuthorizedResources = async () => {
  try {
    const res = await request({
      url: authApiPrefix,
      method: 'get',
      params: {
        resource_type: 1,  // 线路类型
        delete_mark: 0,
        limit: 10000,
      },
    })
    if (res && res.data) {
      const list = Array.isArray(res.data) ? res.data : res.data.results || []
      allAuthorizedResourceIds.value = new Set(list.map((item: any) => String(item.resource_id)))
    }
  } catch (error) {
    console.error('加载已授权资源失败:', error)
    allAuthorizedResourceIds.value = new Set()
  }
}

// 加载所有线路
const loadRoadlines = async () => {
  try {
    roadlinesLoading.value = true
    // 并行加载线路和所有已授权资源
    const [roadlineRes] = await Promise.all([
      request({
        url: roadlineApiPrefix,
        method: 'get',
        params: {
          limit: 1000,
          delete_mark: 0,
          enabled_mark: 1,
        },
      }),
      loadAllAuthorizedResources(),
    ])
    if (roadlineRes && roadlineRes.data) {
      if (Array.isArray(roadlineRes.data)) {
        roadlines.value = roadlineRes.data
      } else if (roadlineRes.data.results) {
        roadlines.value = roadlineRes.data.results
      }
    }
  } catch (error) {
    console.error('加载线路列表失败:', error)
    roadlines.value = []
  } finally {
    roadlinesLoading.value = false
  }
}

// 加载代理商已授权的线路
const loadAgentAuthResources = async () => {
  if (!selectedAgent.value) {
    allowedResourceIds.value = []
    savedAuthRecords.value = []
    return
  }
  try {
    const res = await request({
      url: authApiPrefix,
      method: 'get',
      params: {
        agent_id: selectedAgent.value.id,
        resource_type: 1,  // 线路类型
        delete_mark: 0,
        limit: 1000,
      },
    })
    if (res && res.data) {
      const list = Array.isArray(res.data) ? res.data : res.data.results || []
      // 保存完整的授权记录（用于显示已授权线路和删除操作）
      savedAuthRecords.value = list
      // 提取已授权的资源ID（用于复选框勾选状态）
      allowedResourceIds.value = list.map((item: any) => String(item.resource_id))
    }
  } catch (error) {
    console.error('加载代理商授权资源失败:', error)
    allowedResourceIds.value = []
    savedAuthRecords.value = []
  }
}

// 加载代理商已分配用户
const loadAgentUsers = async () => {
  if (!selectedAgent.value) {
    agentUsers.value = []
    return
  }
  try {
    usersLoading.value = true
    const res = await request({
      url: userApiPrefix,
      method: 'get',
      params: {
        agent_id: selectedAgent.value.id,
        limit: 100,
      },
    })
    if (res && res.data) {
      if (Array.isArray(res.data)) {
        agentUsers.value = res.data
      } else if (res.data.results) {
        agentUsers.value = res.data.results
      }
    }
  } catch (error) {
    console.error('加载代理商用户失败:', error)
    agentUsers.value = []
  } finally {
    usersLoading.value = false
  }
}

// 监听选中代理商
watch(
  selectedAgent,
  (a) => {
    if (!a) return
    agentDraft.id = a.id
    agentDraft.company_name = a.company_name || ''
    agentDraft.credit_code = a.credit_code || ''
    agentDraft.cooperation_level = a.cooperation_level
    agentDraft.contract_start_date = a.contract_start_date || ''
    agentDraft.contract_end_date = a.contract_end_date || ''
    agentDraft.settlement_type = a.settlement_type
    agentDraft.bank_name = a.bank_name || ''
    agentDraft.bank_account = a.bank_account || ''
    agentDraft.contact_phone = a.contact_phone || ''
    agentDraft.contact_email = a.contact_email || ''
    agentDraft.business_manager = a.business_manager || ''
    accountUsername.value = ''
    accountName.value = ''
    // 加载代理商已分配用户
    loadAgentUsers()
    // 加载代理商已授权资源
    loadAgentAuthResources()
  },
  { immediate: true }
)

// 加载代理商列表
const loadAgentList = async () => {
  try {
    loading.value = true
    const params: any = {
      limit: 100,
      delete_mark: 0,
    }
    if (keyword.value) {
      params.search = keyword.value
    }

    const res = await api.GetList(params)

    if (res && res.data) {
      if (Array.isArray(res.data)) {
        agentList.value = res.data
      } else if (res.data.results) {
        agentList.value = res.data.results
      }
    }

    // 如果没有选中代理商且列表有数据，选中第一个
    if (!selectedAgentId.value && agentList.value.length > 0) {
      selectAgent(agentList.value[0])
    }
  } catch (error) {
    console.error('加载代理商列表失败:', error)
    ElMessage.error('加载代理商列表失败')
  } finally {
    loading.value = false
  }
}

// 选中代理商
const selectAgent = (agent: Agent) => {
  selectedAgentId.value = agent.id
  agentTab.value = 'base'
}

// 保存代理商
const saveAgent = async () => {
  if (!selectedAgent.value) return
  try {
    saving.value = true
    const data: any = {
      id: agentDraft.id,
      company_name: agentDraft.company_name,
      credit_code: agentDraft.credit_code || null,
      cooperation_level: agentDraft.cooperation_level,
      contract_start_date: agentDraft.contract_start_date || null,
      contract_end_date: agentDraft.contract_end_date || null,
      settlement_type: agentDraft.settlement_type || null,
      bank_name: agentDraft.bank_name || null,
      bank_account: agentDraft.bank_account || null,
      contact_phone: agentDraft.contact_phone || null,
      contact_email: agentDraft.contact_email || null,
      business_manager: agentDraft.business_manager || null,
    }

    await api.UpdateObj(data)
    ElMessage.success('已保存代理商档案')
    loadAgentList()
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error(error?.response?.data?.msg || '保存失败')
  } finally {
    saving.value = false
  }
}

// 切换代理商状态
const toggleAgentStatus = async () => {
  if (!selectedAgent.value) return
  const currentStatus = selectedAgent.value.enabled_mark
  const newStatus = currentStatus === 1 ? 0 : 1
  const statusText = newStatus === 1 ? '启用' : '停用'

  try {
    await ElMessageBox.confirm(`确认${statusText}该代理商吗？`, '确认操作', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await api.UpdateObj({
      id: selectedAgent.value.id,
      enabled_mark: newStatus,
    } as any)

    ElMessage.success(`已${statusText}`)
    loadAgentList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error(error?.response?.data?.msg || '操作失败')
    }
  }
}

// 账号分配 - 为代理商创建系统用户
const allocateAccount = async () => {
  if (!selectedAgent.value) return
  const username = accountUsername.value.trim()
  const name = accountName.value.trim()
  if (!username) {
    ElMessage.warning('请输入账号')
    return
  }
  if (!name) {
    ElMessage.warning('请输入姓名')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认为代理商「${selectedAgent.value.company_name}」创建登录账号「${username}」（姓名：${name}）吗？\n默认密码为：123456`,
      '创建代理商账号',
      {
        confirmButtonText: '确认创建',
        cancelButtonText: '取消',
        type: 'info',
      }
    )

    saving.value = true

    // 创建系统用户，关联代理商 ID
    const userData = {
      username: username,
      name: name,
      password: '123456',
      mobile: selectedAgent.value.contact_phone || '',
      email: selectedAgent.value.contact_email || '',
      is_active: true,
      user_type: 1,  // 前台用户
      agent_id: selectedAgent.value.id,  // 关联代理商
    }

    await request({
      url: userApiPrefix,
      method: 'post',
      data: userData,
    })

    ElMessage.success(`已为代理商创建账号「${username}」（姓名：${name}），默认密码：123456`)
    accountUsername.value = ''
    accountName.value = ''
    // 刷新用户列表
    loadAgentUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('创建账号失败:', error)
      const msg = error?.response?.data?.msg || error?.response?.data?.username?.[0] || '创建账号失败'
      ElMessage.error(msg)
    }
  } finally {
    saving.value = false
  }
}

// 资源授权
const selectAllFiltered = () => {
  const set = new Set(allowedResourceIds.value)
  for (const r of filteredResources.value) set.add(String(r.id))
  allowedResourceIds.value = Array.from(set)
}

const clearSelectedResources = () => {
  allowedResourceIds.value = []
}

// 保存资源授权
const saveResourceAuth = async () => {
  if (!selectedAgent.value) return
  
  try {
    authSaving.value = true
    const agentId = selectedAgent.value.id
    
    // 1. 先获取当前已有的授权
    const existingRes = await request({
      url: authApiPrefix,
      method: 'get',
      params: {
        agent_id: agentId,
        resource_type: 1,
        delete_mark: 0,
        limit: 1000,
      },
    })
    const existingList = Array.isArray(existingRes?.data) ? existingRes.data : existingRes?.data?.results || []
    const existingMap = new Map<string, any>()
    for (const item of existingList) {
      existingMap.set(String(item.resource_id), item)
    }
    
    // 2. 计算需要新增和删除的
    const newIds = new Set(allowedResourceIds.value)
    const toAdd: string[] = []
    const toDelete: string[] = []
    
    // 需要新增的
    for (const id of newIds) {
      if (!existingMap.has(id)) {
        toAdd.push(id)
      }
    }
    
    // 需要删除的
    for (const [id, item] of existingMap) {
      if (!newIds.has(id)) {
        toDelete.push(item.id)
      }
    }
    
    // 3. 执行新增
    for (const resourceId of toAdd) {
      await request({
        url: authApiPrefix,
        method: 'post',
        data: {
          agent_id: agentId,
          resource_type: 1,  // 线路
          resource_id: resourceId,  // UUID 字符串
        },
      })
    }
    
    // 4. 执行删除
    for (const authId of toDelete) {
      await request({
        url: `${authApiPrefix}${authId}/`,
        method: 'delete',
      })
    }
    
    ElMessage.success(`授权保存成功！新增 ${toAdd.length} 条，移除 ${toDelete.length} 条`)
    // 刷新已保存的授权记录和全局授权状态
    await Promise.all([loadAgentAuthResources(), loadAllAuthorizedResources()])
  } catch (error: any) {
    console.error('保存授权失败:', error)
    ElMessage.error(error?.response?.data?.msg || '保存授权失败')
  } finally {
    authSaving.value = false
  }
}

// 应用折扣
const applyTypeDiscounts = () => {
  ElMessage.success('已应用分类型折扣')
}

// 审核操作（暂无API）
const approveSelectedApplication = async () => {
  const app = selectedApplication.value
  if (!app || app.status !== '待审核') return
  try {
    await ElMessageBox.prompt('请输入要分配的代理商账号', '通过并分配账号', {
      confirmButtonText: '确认通过',
      cancelButtonText: '取消',
      inputValue: `agent_${app.phone.slice(-4)}`
    })
    ElMessage.info('审核功能需要后端支持')
  } catch {
    return
  }
}

const rejectSelectedApplication = async () => {
  const app = selectedApplication.value
  if (!app || app.status !== '待审核') return
  try {
    await ElMessageBox.prompt('请输入驳回原因（可选）', '驳回注册申请', {
      confirmButtonText: '确认驳回',
      cancelButtonText: '取消',
      inputValue: ''
    })
    ElMessage.info('审核功能需要后端支持')
  } catch {
    return
  }
}

// 新建代理商
const showNewAgentDialog = ref(false)
const newAgentFormRef = ref<FormInstance>()
const newAgentForm = reactive({
  agent_code: '',
  company_name: '',
  cooperation_level: 3,
  contact_phone: '',
  contact_email: '',
})

const newAgentRules = {
  agent_code: [{ required: true, message: '代理商编码必填', trigger: 'blur' }],
  company_name: [{ required: true, message: '公司名称必填', trigger: 'blur' }],
  cooperation_level: [{ required: true, message: '合作等级必填', trigger: 'change' }],
}

// 生成代理商编码：AG-YYYYMMDD-XXXX
const generateAgentCode = () => {
  const now = new Date()
  const dateStr = now.getFullYear().toString() +
    String(now.getMonth() + 1).padStart(2, '0') +
    String(now.getDate()).padStart(2, '0')
  const randomStr = String(Math.floor(Math.random() * 9000) + 1000) // 1000-9999
  newAgentForm.agent_code = `AG-${dateStr}-${randomStr}`
}

const openNewAgentDialog = () => {
  generateAgentCode() // 自动生成编码
  newAgentForm.company_name = ''
  newAgentForm.cooperation_level = 3
  newAgentForm.contact_phone = ''
  newAgentForm.contact_email = ''
  showNewAgentDialog.value = true
}

const saveNewAgent = async () => {
  if (!newAgentFormRef.value) return
  try {
    await newAgentFormRef.value.validate()
    saving.value = true

    const data: any = {
      agent_code: newAgentForm.agent_code,
      company_name: newAgentForm.company_name,
      cooperation_level: newAgentForm.cooperation_level,
    }
    if (newAgentForm.contact_phone) data.contact_phone = newAgentForm.contact_phone
    if (newAgentForm.contact_email) data.contact_email = newAgentForm.contact_email

    const res = await api.AddObj(data)
    ElMessage.success('创建成功')
    showNewAgentDialog.value = false
    loadAgentList()

    // 选中新创建的代理商
    if (res && res.data && res.data.id) {
      setTimeout(() => {
        const newAgent = agentList.value.find(a => a.id === res.data.id)
        if (newAgent) {
          selectAgent(newAgent)
        }
      }, 500)
    }
  } catch (error: any) {
    if (error !== false) {
      console.error('创建失败:', error)
      ElMessage.error(error?.response?.data?.msg || '创建失败')
    }
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadAgentList()
  loadRoadlines()
})
</script>

<style scoped>
.agents-page {
  height: 100%;
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
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.panel-header .right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 10px 12px;
  cursor: pointer;
  background: #fff;
}

.item:hover {
  border-color: var(--el-color-primary-light-5);
}

.item.active {
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

.empty {
  color: #909399;
  background: #fafafa;
  border: 1px dashed #dcdfe6;
  border-radius: 12px;
  padding: 12px;
}

.empty-inline {
  color: #909399;
  font-size: 13px;
}

.authorized-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 32px;
}

.authorized-tag {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.subpanel {
  border-radius: 10px;
}

.subpanel.inner :deep(.el-card__body) {
  height: auto;
}

.subhead {
  font-weight: 700;
}

.subhead2 {
  font-weight: 700;
  font-size: 12px;
  margin-bottom: 10px;
}

.kv {
  display: grid;
  grid-template-columns: 90px 1fr;
  gap: 8px 10px;
  align-items: center;
}

.kv .k {
  color: #909399;
  font-size: 12px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.auth-meta {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.auth-list-wrap {
  max-height: 400px;
  overflow-y: auto;
  margin-top: 10px;
}

.auth-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.auth-item {
  border: 1px solid #ebeef5;
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: #fff;
}

.auth-label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.auth-label .primary {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.auth-label .code {
  font-weight: 800;
  color: #303133;
  margin-right: 8px;
}

.auth-label .line-name {
  color: #606266;
}

.price {
  color: #303133;
  font-weight: 700;
  white-space: nowrap;
}

.subhead-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.subblock {
  margin-bottom: 12px;
}

.mt12 {
  margin-top: 12px;
}

.discounts {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.disc {
  display: grid;
  grid-template-columns: 80px 1fr;
  align-items: center;
  gap: 10px;
}

.disc .k {
  color: #909399;
  font-size: 12px;
}

.disc-actions {
  display: flex;
  justify-content: flex-end;
}

.account-form {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.account-form :deep(.el-form-item) {
  margin-bottom: 16px;
}

.account-form :deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-item-flex {
  flex: 1;
}

.account-form :deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
  font-size: 13px;
  padding-bottom: 6px;
}

.account-form :deep(.el-input) {
  width: 100%;
}

@media (max-width: 1200px) {
  .layout {
    grid-template-columns: 1fr;
    height: auto;
  }
  .grid-2 {
    grid-template-columns: 1fr;
  }
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
