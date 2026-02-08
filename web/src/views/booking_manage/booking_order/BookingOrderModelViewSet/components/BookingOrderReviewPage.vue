<template>
  <div class="review-container">
    <!-- 主单信息 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">预订主单信息</span>
          <el-tag v-if="mainOrder" :type="getStatusType(mainOrder.booking_status_display)">
            {{ mainOrder.booking_status_display || '未知状态' }}
          </el-tag>
        </div>
      </template>
      
      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      
      <el-descriptions v-else-if="mainOrder" :column="3" border>
        <el-descriptions-item label="预订单号">{{ mainOrder.booking_no }}</el-descriptions-item>
        <el-descriptions-item label="客户名称">{{ getCustomerName(mainOrder) }}</el-descriptions-item>
        <el-descriptions-item label="代理商名称">{{ getAgentName(mainOrder) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ mainOrder.create_datetime }}</el-descriptions-item>
        <el-descriptions-item label="投放开始日期">{{ mainOrder.start_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="投放结束日期">{{ mainOrder.end_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="广告内容" :span="3">
          {{ mainOrder.ad_content || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="3">
          {{ mainOrder.remark || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-empty v-else description="未找到主单数据" />
    </el-card>

    <!-- 明细列表 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">预订明细列表</span>
          <el-tag type="info">共 {{ detailList.length }} 条明细</el-tag>
        </div>
      </template>
      
      <el-table 
        :data="detailList" 
        border 
        stripe
        style="width: 100%"
        @row-click="handleDetailRowClick"
        :row-class-name="({ row }: { row: any }) => row.id === selectedDetailId ? 'selected-row' : ''"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column label="线路名称" min-width="80">
          <template #default="{ row }">
            {{ getRoadlineName(row) }}
          </template>
        </el-table-column>
        <el-table-column label="运营公司" min-width="80">
          <template #default="{ row }">
            {{ getCompanyName(row) }}
          </template>
        </el-table-column>
        <el-table-column label="媒体类型" min-width="80">
          <template #default="{ row }">
            {{ getDetailMediaTypeName(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" min-width="80" align="left" />
        <el-table-column prop="start_date" label="投放开始日期" min-width="120" align="left" />
        <el-table-column prop="end_date" label="投放结束日期" min-width="120" align="left" />
        <el-table-column label="操作" min-width="100" align="left">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              link
              @click.stop="loadPositions(row.id)"
            >
              <!-- 查看车位 -->
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 车位列表 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">预订车位列表</span>
          <el-tag v-if="groupedPositionList.length > 0" type="success">
            已分配 {{ groupedPositionList.length }} 辆车
          </el-tag>
          <el-tag v-else-if="!positionLoading" type="info">暂无车位数据</el-tag>
        </div>
      </template>
      
      <div v-if="positionLoading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载车位数据...</span>
      </div>
      
      <el-table 
        v-else-if="groupedPositionList.length > 0"
        :data="groupedPositionList" 
        border 
        stripe
        style="width: 100%"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="roadline_name" label="线路名称" min-width="100" />
        <el-table-column label="车牌号" min-width="120">
          <template #default="{ row }">
            {{ getVehiclePlate(row) }}
          </template>
        </el-table-column>
        <el-table-column label="媒体类型" min-width="120">
          <template #default="{ row }">
            {{ getVehicleMediaTypeName(row) }}
          </template>
        </el-table-column>
        <el-table-column label="资源状态" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getResourceStatusTagType(row)" size="small">
              {{ getResourceStatusText(row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="actual_on_date" label="上刊日期" min-width="120" align="left" />
        <el-table-column prop="reserved_start_date" label="投放开始日期" min-width="120" align="left" />
        <el-table-column prop="reserved_end_date" label="投放结束日期" min-width="120" align="left" />
        <el-table-column prop="actual_off_date" label="下刊日期" min-width="120" align="left" />
        <!-- <el-table-column label="车位数量" width="100" align="center">
          <template #default="{ row }">
            {{ row.positionCount || 0 }}
          </template>
        </el-table-column> -->
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleEditVehiclePositions(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-else description="暂无车位分配信息" />
    </el-card>

    <!-- 审批流程进度 -->
    <el-card v-if="mainOrder" shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">审批流程</span>
          <el-tag v-if="mainOrder.reject_reason" type="danger">
            驳回原因：{{ mainOrder.reject_reason }}
          </el-tag>
        </div>
      </template>
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="草稿" description="创建预订单" />
        <el-step title="媒体部初审" description="审核资源分配" />
        <el-step title="营运公司审核" description="确认/换车/剔除" />
        <el-step title="媒体部复审" description="最终审核" />
        <el-step title="已通过" description="创建上刊订单" />
      </el-steps>
    </el-card>

    <!-- 营运公司审核 - 按公司分组的车位确认 -->
    <el-card v-if="mainOrder && mainOrder.booking_status === 3" shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">营运公司车位确认</span>
          <div>
            <el-tag type="info" style="margin-right: 8px">
              待确认: {{ positionStats.pending }}
            </el-tag>
            <el-tag type="success" style="margin-right: 8px">
              已确认: {{ positionStats.confirmed }}
            </el-tag>
            <el-tag type="danger">
              已剔除: {{ positionStats.excluded }}
            </el-tag>
          </div>
        </div>
      </template>

      <el-table :data="positionList" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="roadline_name" label="线路" min-width="80" />
        <el-table-column prop="roadline_company_name" label="营运公司" min-width="80" />
        <el-table-column label="车牌号" min-width="100">
          <template #default="{ row }">{{ getVehiclePlate(row) }}</template>
        </el-table-column>
        <el-table-column label="媒体类型" min-width="80">
          <template #default="{ row }">{{ row.base_media_type_name || row.media_type_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="reserved_start_date" label="开始日期" width="110" />
        <el-table-column prop="reserved_end_date" label="结束日期" width="110" />
        <el-table-column label="确认状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getConfirmStatusType(row.confirm_status)" size="small">
              {{ getConfirmStatusText(row.confirm_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="剔除原因" min-width="100">
          <template #default="{ row }">{{ row.exclude_reason || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" align="center" fixed="right">
          <template #default="{ row }">
            <template v-if="row.confirm_status === 1">
              <el-button type="success" size="small" link @click="handleConfirmPosition(row)">确认</el-button>
              <el-button type="warning" size="small" link @click="handleSwapVehicle(row)">换车</el-button>
              <el-button type="danger" size="small" link @click="handleExcludePosition(row)">剔除</el-button>
            </template>
            <span v-else style="color: #909399">已处理</span>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; text-align: right">
        <el-button @click="handleBatchConfirm" type="primary">批量全部确认</el-button>
      </div>
    </el-card>

    <!-- 审核操作区域 -->
    <el-card v-if="!isReadOnly && mainOrder" shadow="never" class="section-card">
      <template #header>
        <div class="section-header">
          <span class="section-title">审核操作</span>
        </div>
      </template>

      <el-form label-width="100px">
        <el-form-item label="审核意见">
          <el-input
            v-model="reviewComment"
            type="textarea"
            :rows="4"
            placeholder="请输入审核意见..."
          />
        </el-form-item>
        <el-form-item>
          <!-- 媒体部初审 -->
          <template v-if="mainOrder.booking_status === 2">
            <el-button type="success" @click="handleFirstReviewApprove">初审通过</el-button>
            <el-button type="danger" @click="handleFirstReviewReject">初审驳回</el-button>
          </template>
          <!-- 营运公司审核完成 -->
          <template v-if="mainOrder.booking_status === 3">
            <el-button type="primary" @click="handleCompanyReviewComplete" :disabled="positionStats.pending > 0">
              营运审核完成 {{ positionStats.pending > 0 ? `(还有${positionStats.pending}个待确认)` : '' }}
            </el-button>
          </template>
          <!-- 媒体部复审 -->
          <template v-if="mainOrder.booking_status === 4">
            <el-button type="success" @click="handleFinalReviewApprove">复审通过</el-button>
            <el-button type="danger" @click="handleFinalReviewReject">复审驳回</el-button>
          </template>
          <el-button @click="handleClose">关闭</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 编辑车位对话框 -->
    <el-dialog
      v-model="editPositionDialogVisible"
      title="编辑车位信息"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="editPositionForm" 
        label-width="120px"
        v-loading="editPositionLoading"
      >
        <el-form-item label="线路名称">
          <el-input v-model="editPositionForm.roadline_name" disabled />
        </el-form-item>
        <el-form-item label="选择车辆" required>
          <el-select 
            v-model="editPositionForm.vehicle_id" 
            placeholder="请选择车辆"
            filterable
            style="width: 100%"
            :loading="roadlineVehiclesLoading"
          >
            <el-option
              v-for="vehicle in roadlineVehicles"
              :key="vehicle.id"
              :label="`${vehicle.vehicle_plate || vehicle.vehicle_no} (${vehicle.vehicle_no})`"
              :value="vehicle.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="预订开始日期">
          <el-date-picker
            v-model="editPositionForm.reserved_start_date"
            type="date"
            placeholder="开始日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            disabled
          />
        </el-form-item>
        <el-form-item label="预订结束日期">
          <el-date-picker
            v-model="editPositionForm.reserved_end_date"
            type="date"
            placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            disabled
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editPositionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePosition" :loading="editPositionLoading">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Loading } from '@element-plus/icons-vue';
import { request } from '/@/utils/service';

// 定义props（参考 RoadlineForm 的方式）
const props = defineProps<{
  /** 订单ID（向后兼容，优先使用 formParams.id） */
  orderId?: string;
  /** 订单号（向后兼容） */
  orderNo?: string;
  /** 是否只读模式 */
  readonly?: boolean;
  /** 初始数据 */
  data?: Record<string, any>;
  /** 节点ID（可用于控制不同节点显示不同字段） */
  nodeId?: string;
  /** URL参数（来自工作流表单配置，包含 id 字段） */
  formParams?: Record<string, string>;
}>();

// 定义emits
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'refresh'): void;
}>();

// 计算订单ID：优先使用 formParams.id，如果没有则使用 orderId
const orderId = computed(() => {
  return props.formParams?.id || props.orderId || '';
});

// 计算是否只读：readonly 属性或 formParams.viewFlag=1 参数
const isReadOnly = computed(() => {
  return props.readonly || props.formParams?.viewFlag === '1';
});

// 响应式数据
const loading = ref(false);
const positionLoading = ref(false);
const mainOrder = ref<any>(null);
const detailList = ref<any[]>([]);
const positionList = ref<any[]>([]);
const selectedDetailId = ref<string>('');
const reviewComment = ref('');

// 编辑车位对话框相关
const editPositionDialogVisible = ref(false);
const editPositionLoading = ref(false);
const editPositionForm = ref<any>({
  id: '',
  vehicle_id: '',
  roadline_id: '',
  roadline_name: '',
  reserved_start_date: '',
  reserved_end_date: '',
});

// 当前线路下的车辆列表
const roadlineVehicles = ref<any[]>([]);
const roadlineVehiclesLoading = ref(false);

// 基础数据列表（用于显示名称）
const roadlineList = ref<any[]>([]);
const companyList = ref<any[]>([]);
const mediaTypeList = ref<any[]>([]);
const vehicleList = ref<any[]>([]);
const customerList = ref<any[]>([]);
const agentList = ref<any[]>([]);

// API前缀
const roadlineApiPrefix = '/api/RoadlineModelViewSet/';
const companyApiPrefix = '/api/CompanyModelViewSet/';
const mediaTypeApiPrefix = '/api/AdMediaTypeModelViewSet/';
const vehicleApiPrefix = '/api/VehicleModelViewSet/';
const customerApiPrefix = '/api/CustomerModelViewSet/';
const agentApiPrefix = '/api/AgentModelViewSet/';

// 加载线路列表
const loadRoadlineList = async () => {
  try {
    const res = await request({
      url: roadlineApiPrefix,
      method: 'get',
      params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
    });
    let dataArray: any[] = [];
    if (res && res.data) {
      if (Array.isArray(res.data)) {
        dataArray = res.data;
      } else if (res.data.results && Array.isArray(res.data.results)) {
        dataArray = res.data.results;
      }
    }
    roadlineList.value = dataArray;
  } catch (error) {
    console.error('加载线路列表失败:', error);
  }
};

// 加载公司列表（使用 get_company_options 接口获取所有公司，包括子节点）
const loadCompanyList = async () => {
  try {
    // 使用 get_company_options 接口，设置 enabled_only=false 获取所有未删除的公司（包括子节点）
    const res = await request({
      url: `${companyApiPrefix}get_company_options/`,
      method: 'get',
      params: { enabled_only: 'false' }, // 获取所有未删除的公司，包括已禁用的
    });
    let dataArray: any[] = [];
    if (res && res.data) {
      if (Array.isArray(res.data)) {
        dataArray = res.data;
      } else if (res.data.results && Array.isArray(res.data.results)) {
        dataArray = res.data.results;
      }
    }
    companyList.value = dataArray;
  } catch (error) {
    console.error('加载公司列表失败:', error);
    // 如果 get_company_options 接口失败，尝试使用普通接口
    try {
      const res = await request({
        url: companyApiPrefix,
        method: 'get',
        params: { limit: 9999 },
      });
      let dataArray: any[] = [];
      if (res && res.data) {
        if (Array.isArray(res.data)) {
          dataArray = res.data;
        } else if (res.data.results && Array.isArray(res.data.results)) {
          dataArray = res.data.results;
        }
      }
      companyList.value = dataArray;
    } catch (fallbackError) {
      console.error('使用备用接口加载公司列表也失败:', fallbackError);
    }
  }
};

// 加载媒体类型列表
const loadMediaTypeList = async () => {
  try {
    // 同时请求组合类型和非组合类型
    const [compositeRes, nonCompositeRes] = await Promise.all([
      request({
        url: mediaTypeApiPrefix,
        method: 'get',
        params: { limit: 9999, enabled_mark: 1, delete_mark: 0, is_composite: 'true' },
      }),
      request({
        url: mediaTypeApiPrefix,
        method: 'get',
        params: { limit: 9999, enabled_mark: 1, delete_mark: 0, is_composite: 'false' },
      }),
    ]);
    
    let compositeArray: any[] = [];
    let nonCompositeArray: any[] = [];
    
    if (compositeRes && compositeRes.data) {
      compositeArray = Array.isArray(compositeRes.data) ? compositeRes.data : (compositeRes.data.results || []);
    }
    if (nonCompositeRes && nonCompositeRes.data) {
      nonCompositeArray = Array.isArray(nonCompositeRes.data) ? nonCompositeRes.data : (nonCompositeRes.data.results || []);
    }
    
    mediaTypeList.value = [...compositeArray, ...nonCompositeArray];
  } catch (error) {
    console.error('加载媒体类型列表失败:', error);
  }
};

// 加载车辆列表（备用，用于其他需要车辆信息的场景）
const loadVehicleList = async () => {
  try {
    const res = await request({
      url: vehicleApiPrefix,
      method: 'get',
      params: { limit: 9999 },
    });
    let dataArray: any[] = [];
    if (res && res.data) {
      if (Array.isArray(res.data)) {
        dataArray = res.data;
      } else if (res.data.results && Array.isArray(res.data.results)) {
        dataArray = res.data.results;
      }
    }
    vehicleList.value = dataArray;
  } catch (error) {
    console.error('加载车辆列表失败:', error);
  }
};

// 加载客户列表
const loadCustomerList = async () => {
  try {
    const res = await request({
      url: customerApiPrefix,
      method: 'get',
      params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
    });
    let dataArray: any[] = [];
    if (res && res.data) {
      if (Array.isArray(res.data)) {
        dataArray = res.data;
      } else if (res.data.results && Array.isArray(res.data.results)) {
        dataArray = res.data.results;
      }
    }
    customerList.value = dataArray;
  } catch (error) {
    console.error('加载客户列表失败:', error);
  }
};

// 加载代理商列表
const loadAgentList = async () => {
  try {
    const res = await request({
      url: agentApiPrefix,
      method: 'get',
      params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
    });
    let dataArray: any[] = [];
    if (res && res.data) {
      if (Array.isArray(res.data)) {
        dataArray = res.data;
      } else if (res.data.results && Array.isArray(res.data.results)) {
        dataArray = res.data.results;
      }
    }
    agentList.value = dataArray;
  } catch (error) {
    console.error('加载代理商列表失败:', error);
  }
};

// 获取车牌号
const getVehiclePlate = (row: any) => {
  // 优先使用后端直接返回的 vehicle_plate 字段
  if (row.vehicle_plate) {
    return row.vehicle_plate;
  }
  // 兜底使用 vehicle_no 字段（自编号）
  return row.vehicle_no || '-';
};

// 根据ID获取线路名称
const getRoadlineName = (row: any) => {
  // 优先使用冗余字段
  if (row.roadline_name) {
    return row.roadline_name;
  }
  // 从列表中查找
  if (row.roadline_id && roadlineList.value.length > 0) {
    const item = roadlineList.value.find((r: any) => r.id === row.roadline_id);
    return item?.line_name || '-';
  }
  return '-';
};

// 根据ID获取公司名称
const getCompanyName = (row: any) => {
  // 根据 dwd_booking_order_detail 表的 roadline_company_id 字段去 dwd_company 表查找 fullname
  // row 是明细行数据，包含 roadline_company_id 字段
  
  // 检查明细行是否有 roadline_company_id 字段
  if (!row.roadline_company_id) {
    // 如果明细行没有 roadline_company_id，使用冗余字段作为兜底
    return row.roadline_company_name || '-';
  }
  
  // 使用字符串比较，避免类型不匹配问题（ID可能是字符串或数字）
  const companyId = String(row.roadline_company_id);
  
  // 确保公司列表已加载
  if (companyList.value.length === 0) {
    // 如果找不到，尝试使用冗余字段作为兜底
    return row.roadline_company_name || '-';
  }
  
  // 根据 roadline_company_id 匹配 dwd_company 的 id 字段
  const item = companyList.value.find((c: any) => {
    // 匹配 dwd_company 表的 id 字段（支持多种数据结构）
    const cId = String(c.id || c.company_id || '');
    return cId === companyId;
  });
  
  // 如果找到对应的公司，返回 fullname
  if (item) {
    // 优先返回 fullname，如果没有则使用其他字段作为兜底
    return item.fullname || item.shortname || item.company_name || '-';
  }
  
  // 如果找不到对应的公司，尝试使用冗余字段作为兜底
  if (row.roadline_company_name) {
    return row.roadline_company_name;
  }
  return '-';
};

// 根据ID获取媒体类型名称（明细列表用）
const getDetailMediaTypeName = (row: any) => {
  // 优先使用冗余字段
  if (row.media_type_name) {
    return row.media_type_name;
  }
  // 从列表中查找
  if (row.media_type_id && mediaTypeList.value.length > 0) {
    const item = mediaTypeList.value.find((m: any) => m.id === row.media_type_id);
    return item?.media_name || '-';
  }
  return '-';
};

// 获取客户名称
const getCustomerName = (order: any) => {
  // 优先使用冗余字段 customer_name
  if (order.customer_name) {
    return order.customer_name;
  }
  // 如果 customer_name 为空，尝试从 customer_id 关联对象中获取
  if (order.customer_id) {
    // customer_id 可能是对象或ID
    if (typeof order.customer_id === 'object') {
      // 从关联对象中获取客户名称
      const customer = order.customer_id;
      return customer.company_name || customer.customer_name || customer.name || '-';
    } else {
      // customer_id 是ID，从客户列表中查找
      const customerId = order.customer_id;
      if (customerList.value.length > 0) {
        const customer = customerList.value.find((c: any) => c.id === customerId);
        if (customer) {
          return customer.company_name || customer.customer_name || customer.name || '-';
        }
      }
    }
  }
  return '-';
};

// 获取代理商名称
const getAgentName = (order: any) => {
  // 优先使用冗余字段 agent_name
  if (order.agent_name) {
    return order.agent_name;
  }
  // 如果 agent_name 为空，尝试从 agent_id 关联对象中获取
  if (order.agent_id) {
    // agent_id 可能是对象或ID
    if (typeof order.agent_id === 'object') {
      // 从关联对象中获取代理商名称
      const agent = order.agent_id;
      return agent.company_name || agent.agent_name || agent.name || '-';
    } else {
      // agent_id 是ID，从代理商列表中查找
      const agentId = order.agent_id;
      if (agentList.value.length > 0) {
        const agent = agentList.value.find((a: any) => a.id === agentId);
        if (agent) {
          return agent.company_name || agent.agent_name || agent.name || '-';
        }
      }
    }
  }
  return '-';
};

// 加载主单数据
const loadMainOrder = async () => {
  if (!orderId.value) {
    console.warn('[BookingOrderReviewPage] 订单ID为空，无法加载数据');
    return;
  }
  try {
    loading.value = true;
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/`,
      method: 'get',
    });
    
    if (res && res.data) {
      mainOrder.value = res.data;
    }
  } catch (error) {
    console.error('加载主单数据失败:', error);
    ElMessage.error('加载主单数据失败');
  } finally {
    loading.value = false;
  }
};

// 加载明细数据
const loadDetailList = async () => {
  if (!orderId.value) {
    console.warn('[BookingOrderReviewPage] 订单ID为空，无法加载明细数据');
    return;
  }
  try {
    const res = await request({
      url: '/api/BookingOrderDetailModelViewSet/',
      method: 'get',
      params: {
        booking_order_id: orderId.value,
        limit: 9999,
      },
    });
    
    if (res && res.data) {
      detailList.value = res.data.results || res.data || [];
    }
  } catch (error) {
    console.error('加载明细数据失败:', error);
    ElMessage.error('加载明细数据失败');
  }
};

// 加载车位数据（按明细ID）
const loadPositions = async (detailId: string) => {
  try {
    positionLoading.value = true;
    selectedDetailId.value = detailId;
    
    const res = await request({
      url: '/api/VehicleAdPositionModelViewSet/',
      method: 'get',
      params: {
        booking_detail_id: detailId,
        limit: 9999,
      },
    });
    
    if (res && res.data) {
      positionList.value = res.data.results || res.data || [];
    }
  } catch (error) {
    console.error('加载车位数据失败:', error);
    ElMessage.error('加载车位数据失败');
  } finally {
    positionLoading.value = false;
  }
};

// 加载所有车位数据（按订单ID，遍历所有明细）
const loadAllPositions = async () => {
  try {
    positionLoading.value = true;
    selectedDetailId.value = ''; // 清空选中的明细ID
    
    // 如果没有明细数据，先等待明细数据加载完成
    if (detailList.value.length === 0) {
      await loadDetailList();
    }
    
    // 如果还是没有明细数据，直接返回
    if (detailList.value.length === 0) {
      positionList.value = [];
      return;
    }
    
    // 获取所有明细ID
    const detailIds = detailList.value.map((detail: any) => detail.id);
    
    // 并行加载所有明细的车位数据
    const positionPromises = detailIds.map((detailId: string) =>
      request({
        url: '/api/VehicleAdPositionModelViewSet/',
        method: 'get',
        params: {
          booking_detail_id: detailId,
          limit: 9999,
        },
      }).catch((error: any) => {
        console.error(`加载明细 ${detailId} 的车位数据失败:`, error);
        return null;
      })
    );
    
    const results = await Promise.all(positionPromises);
    
    // 合并所有车位数据
    const allPositions: any[] = [];
    results.forEach((res) => {
      if (res && res.data) {
        const positions = res.data.results || res.data || [];
        allPositions.push(...positions);
      }
    });
    
    positionList.value = allPositions;
  } catch (error) {
    console.error('加载所有车位数据失败:', error);
    ElMessage.error('加载车位数据失败');
  } finally {
    positionLoading.value = false;
  }
};

// 处理明细行点击（筛选显示该明细的车位）
const handleDetailRowClick = (row: any) => {
  // 如果点击的是已选中的明细，则显示所有车位
  if (selectedDetailId.value === row.id) {
    selectedDetailId.value = '';
    loadAllPositions();
  } else {
    // 否则筛选显示该明细的车位
    selectedDetailId.value = row.id;
    loadPositions(row.id);
  }
};

// 审批流程步骤计算
const currentStep = computed(() => {
  if (!mainOrder.value) return 0;
  const statusMap: Record<number, number> = {
    1: 0,  // 草稿
    2: 1,  // 待媒体部初审
    3: 2,  // 待营运公司审核
    4: 3,  // 待媒体部复审
    5: 4,  // 已通过
    6: 4,  // 已完成
    7: -1, // 已驳回（特殊处理）
    8: -1, // 已取消
  };
  return statusMap[mainOrder.value.booking_status] ?? 0;
});

// 车位确认状态统计
const positionStats = computed(() => {
  const stats = { total: 0, confirmed: 0, excluded: 0, pending: 0 };
  positionList.value.forEach((p: any) => {
    if (p.allocation_status !== 1) return; // 只统计已分配的
    stats.total++;
    if (p.confirm_status === 2) stats.confirmed++;
    else if (p.confirm_status === 3) stats.excluded++;
    else stats.pending++;
  });
  return stats;
});

// 确认状态文本
const getConfirmStatusText = (status: number) => {
  const map: Record<number, string> = { 1: '待确认', 2: '已确认', 3: '已剔除' };
  return map[status] || '未知';
};

// 确认状态标签类型
const getConfirmStatusType = (status: number) => {
  const map: Record<number, string> = { 1: 'warning', 2: 'success', 3: 'danger' };
  return map[status] || 'info';
};

// 获取状态类型
const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '草稿': 'info',
    '待媒体部初审': 'warning',
    '待营运公司审核': 'warning',
    '待媒体部复审': 'warning',
    '已通过': 'success',
    '已完成': 'success',
    '已取消': 'info',
    '已驳回': 'danger',
  };
  return statusMap[status] || 'info';
};

// 获取分配状态文本
const getAllocationStatusText = (status: number) => {
  const statusMap: Record<number, string> = {
    1: '已分配',
    2: '已上刊',
    3: '已下刊',
    4: '已取消',
  };
  return statusMap[status] || '未知';
};

// 获取分配状态类型
const getAllocationStatusType = (status: number) => {
  const typeMap: Record<number, string> = {
    1: 'success',
    2: 'primary',
    3: 'info',
    4: 'danger',
  };
  return typeMap[status] || 'info';
};

// 获取媒体类型名称（从resource_id关联的base_media_type获取）
const getMediaTypeName = (row: any) => {
  // 后端已经通过SerializerMethodField返回了base_media_type_name
  if (row.base_media_type_name) {
    return row.base_media_type_name;
  }
  return '-';
};

// 按车辆分组的车位列表
const groupedPositionList = computed(() => {
  if (!positionList.value || positionList.value.length === 0) {
    return [];
  }
  
  // 按 vehicle_id 分组
  const groupedMap = new Map<string, any[]>();
  
  positionList.value.forEach((position: any) => {
    const vehicleId = typeof position.vehicle_id === 'object' 
      ? position.vehicle_id?.id 
      : position.vehicle_id;
    
    if (!vehicleId) return;
    
    if (!groupedMap.has(vehicleId)) {
      groupedMap.set(vehicleId, []);
    }
    groupedMap.get(vehicleId)!.push(position);
  });
  
  // 转换为数组，每个车辆一条记录
  const result: any[] = [];
  
  groupedMap.forEach((positions, vehicleId) => {
    // 取第一个车位作为基础信息
    const firstPosition = positions[0];
    
    // 获取所有唯一的明细ID
    const detailIds = [...new Set(positions.map((p: any) => {
      const detailId = typeof p.booking_detail_id === 'object' 
        ? p.booking_detail_id?.id 
        : p.booking_detail_id;
      return detailId;
    }).filter(Boolean))];
    
    // 从明细列表中获取媒体类型名称
    const mediaTypeNames: string[] = [];
    detailIds.forEach((detailId: string) => {
      const detail = detailList.value.find((d: any) => d.id === detailId);
      if (detail) {
        const mediaTypeName = getDetailMediaTypeName(detail);
        if (mediaTypeName && mediaTypeName !== '-' && !mediaTypeNames.includes(mediaTypeName)) {
          mediaTypeNames.push(mediaTypeName);
        }
      }
    });
    
    // 计算日期范围：最早开始日期和最晚结束日期
    const dates = positions.map((p: any) => ({
      start: p.reserved_start_date,
      end: p.reserved_end_date,
    })).filter((d: any) => d.start && d.end);
    
    let minStartDate = '';
    let maxEndDate = '';
    if (dates.length > 0) {
      minStartDate = dates.reduce((min: string, d: any) => 
        !min || d.start < min ? d.start : min, '');
      maxEndDate = dates.reduce((max: string, d: any) => 
        !max || d.end > max ? d.end : max, '');
    }
    
    // 计算上刊日期和下刊日期：最早上刊日期和最晚下刊日期
    const onOffDates = positions.map((p: any) => ({
      on: p.actual_on_date,
      off: p.actual_off_date,
    })).filter((d: any) => d.on || d.off);
    
    let minOnDate = '';
    let maxOffDate = '';
    if (onOffDates.length > 0) {
      // 获取所有有上刊日期的记录，取最早的
      const onDates = onOffDates.filter((d: any) => d.on).map((d: any) => d.on);
      if (onDates.length > 0) {
        minOnDate = onDates.reduce((min: string, d: string) => 
          !min || d < min ? d : min, '');
      }
      // 获取所有有下刊日期的记录，取最晚的
      const offDates = onOffDates.filter((d: any) => d.off).map((d: any) => d.off);
      if (offDates.length > 0) {
        maxOffDate = offDates.reduce((max: string, d: string) => 
          !max || d > max ? d : max, '');
      }
    }

    // 计算资源状态：若该车辆所有车位状态一致，则直接取该状态；否则显示“多种状态”
    const statusValues = [...new Set(
      positions
        .map((p: any) => p.resource_status)
        .filter((s: any) => s !== null && s !== undefined)
    )];

    let groupResourceStatus: number | null = null;
    let groupResourceStatusDisplay = '';

    if (statusValues.length === 1) {
      groupResourceStatus = statusValues[0] as number;
      const sample = positions.find((p: any) => p.resource_status === groupResourceStatus);
      groupResourceStatusDisplay = sample?.resource_status_display || '';
    } else if (statusValues.length > 1) {
      groupResourceStatusDisplay = '多种状态';
    }

    result.push({
      vehicle_id: vehicleId,
      vehicle_no: firstPosition.vehicle_no || '',
      vehicle_plate: firstPosition.vehicle_plate || '',
      roadline_id: typeof firstPosition.roadline_id === 'object' 
        ? firstPosition.roadline_id?.id 
        : firstPosition.roadline_id,
      roadline_name: firstPosition.roadline_name || '',
      reserved_start_date: minStartDate || firstPosition.reserved_start_date || '',
      reserved_end_date: maxEndDate || firstPosition.reserved_end_date || '',
      actual_on_date: minOnDate || firstPosition.actual_on_date || '',
      actual_off_date: maxOffDate || firstPosition.actual_off_date || '',
      positionCount: positions.length,
      positions: positions, // 保存原始车位列表，用于编辑
      media_type_names: mediaTypeNames, // 保存媒体类型名称列表
      detail_ids: detailIds, // 保存关联的明细ID列表
      resource_status: groupResourceStatus,
      resource_status_display: groupResourceStatusDisplay,
    });
  });
  
  return result;
});

// 获取车辆的媒体类型名称（从明细列表获取）
const getVehicleMediaTypeName = (row: any) => {
  if (row.media_type_names && row.media_type_names.length > 0) {
    return row.media_type_names.join('、');
  }
  return '-';
};

// 获取资源状态展示文本
const getResourceStatusText = (row: any) => {
  if (row.resource_status_display) {
    return row.resource_status_display;
  }
  const status = row.resource_status;
  if (status === null || status === undefined) {
    return '-';
  }
  const statusMap: Record<number, string> = {
    1: '空闲',
    2: '预订',
    3: '在刊',
    4: '下刊',
    5: '维修中',
    6: '不可用',
    7: '到期未下刊',
  };
  return statusMap[status] || '未知';
};

// 获取资源状态对应的标签颜色类型
const getResourceStatusTagType = (row: any) => {
  const statusValue = row.resource_status;
  const statusText = getResourceStatusText(row);

  // 优先根据显示文本判断（支持自动判断的"到期未下刊"、"多种状态"等）
  if (statusText === '预订') {
    return 'warning'; // 预订
  } else if (statusText === '在刊') {
    return 'success'; // 在刊
  } else if (statusText === '下刊') {
    return 'info'; // 下刊
  } else if (statusText === '到期未下刊') {
    return 'danger'; // 到期未下刊
  } else if (statusText === '维修中') {
    return 'warning'; // 维修中
  } else if (statusText === '不可用') {
    return 'danger'; // 不可用
  } else if (statusText === '空闲') {
    return 'info'; // 空闲
  } else if (statusText === '多种状态') {
    return 'warning'; // 多种状态，用醒目颜色
  }

  // 兜底：根据状态值判断
  if (statusValue === 2) {
    return 'warning'; // 预订
  } else if (statusValue === 3) {
    return 'success'; // 在刊
  } else if (statusValue === 4) {
    return 'info'; // 下刊
  } else if (statusValue === 5) {
    return 'warning'; // 维修中
  } else if (statusValue === 6) {
    return 'danger'; // 不可用
  } else if (statusValue === 7) {
    return 'danger'; // 到期未下刊
  }

  return 'info'; // 默认
};

// ==================== 审批流程操作 ====================

// 媒体部初审通过
const handleFirstReviewApprove = async () => {
  try {
    await ElMessageBox.confirm('确认初审通过？将转交营运公司审核。', '确认操作', { type: 'success' });
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/first_review_approve/`,
      method: 'post',
      data: { review_comment: reviewComment.value || '' },
    });
    if (res && res.code === 2000) {
      ElMessage.success(res.msg || '初审通过');
      emit('refresh');
      emit('close');
    } else {
      ElMessage.error(res?.msg || '操作失败');
    }
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.msg || e?.message || '操作失败');
  }
};

// 媒体部初审驳回
const handleFirstReviewReject = async () => {
  if (!reviewComment.value.trim()) {
    ElMessage.warning('驳回时必须填写审核意见');
    return;
  }
  try {
    await ElMessageBox.confirm('确认驳回此订单？', '确认驳回', { type: 'warning' });
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/first_review_reject/`,
      method: 'post',
      data: { reject_reason: reviewComment.value },
    });
    if (res && res.code === 2000) {
      ElMessage.success(res.msg || '已驳回');
      emit('refresh');
      emit('close');
    } else {
      ElMessage.error(res?.msg || '驳回失败');
    }
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.msg || e?.message || '驳回失败');
  }
};

// 营运公司确认车位
const handleConfirmPosition = async (row: any) => {
  try {
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/company_confirm_position/`,
      method: 'post',
      data: { position_id: row.id },
    });
    if (res && res.code === 2000) {
      ElMessage.success('车位已确认');
      await loadAllPositions();
    } else {
      ElMessage.error(res?.msg || '确认失败');
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.msg || e?.message || '确认失败');
  }
};

// 营运公司剔除车位
const handleExcludePosition = async (row: any) => {
  try {
    const { value: reason } = await ElMessageBox.prompt('请输入剔除原因', '剔除车位', {
      confirmButtonText: '确认剔除',
      cancelButtonText: '取消',
      inputType: 'textarea',
      inputValidator: (val: string) => !!val?.trim() || '剔除原因不能为空',
      type: 'warning',
    });
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/company_exclude_position/`,
      method: 'post',
      data: { position_id: row.id, exclude_reason: reason },
    });
    if (res && res.code === 2000) {
      ElMessage.success('车位已剔除');
      await loadAllPositions();
    } else {
      ElMessage.error(res?.msg || '剔除失败');
    }
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.msg || e?.message || '剔除失败');
  }
};

// 营运公司换车
const handleSwapVehicle = async (row: any) => {
  // 获取线路下的可用车辆
  const roadlineId = typeof row.roadline_id === 'object' ? row.roadline_id?.id : row.roadline_id;
  await loadRoadlineVehicles(roadlineId);

  // 填充编辑表单
  editPositionForm.value = {
    id: row.id,
    vehicle_id: '',
    roadline_id: roadlineId || '',
    roadline_name: row.roadline_name || '',
    reserved_start_date: row.reserved_start_date || '',
    reserved_end_date: row.reserved_end_date || '',
    _isSwap: true, // 标记为换车操作
  };
  editPositionDialogVisible.value = true;
};

// 批量确认
const handleBatchConfirm = async () => {
  try {
    await ElMessageBox.confirm('确认将所有待确认的车位全部确认？', '批量确认', { type: 'warning' });
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/company_batch_confirm/`,
      method: 'post',
    });
    if (res && res.code === 2000) {
      ElMessage.success(res.msg || '批量确认成功');
      await loadAllPositions();
    } else {
      ElMessage.error(res?.msg || '批量确认失败');
    }
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.msg || e?.message || '批量确认失败');
  }
};

// 营运公司审核完成
const handleCompanyReviewComplete = async () => {
  try {
    await ElMessageBox.confirm('确认营运公司审核完成？将转交媒体部复审。', '确认完成', { type: 'success' });
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/company_review_complete/`,
      method: 'post',
      data: { review_comment: reviewComment.value || '' },
    });
    if (res && res.code === 2000) {
      ElMessage.success(res.msg || '审核完成');
      emit('refresh');
      emit('close');
    } else {
      ElMessage.error(res?.msg || '操作失败');
    }
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.msg || e?.message || '操作失败');
  }
};

// 媒体部复审通过
const handleFinalReviewApprove = async () => {
  try {
    await ElMessageBox.confirm('确认复审通过？将创建上刊订单。', '确认操作', { type: 'success' });
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/final_review_approve/`,
      method: 'post',
      data: { review_comment: reviewComment.value || '' },
    });
    if (res && res.code === 2000) {
      ElMessage.success(res.msg || '复审通过');
      emit('refresh');
      emit('close');
    } else {
      ElMessage.error(res?.msg || '操作失败');
    }
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.msg || e?.message || '操作失败');
  }
};

// 媒体部复审驳回
const handleFinalReviewReject = async () => {
  if (!reviewComment.value.trim()) {
    ElMessage.warning('驳回时必须填写审核意见');
    return;
  }
  try {
    await ElMessageBox.confirm('确认驳回此订单？', '确认驳回', { type: 'warning' });
    const res = await request({
      url: `/api/BookingOrderModelViewSet/${orderId.value}/final_review_reject/`,
      method: 'post',
      data: { reject_reason: reviewComment.value },
    });
    if (res && res.code === 2000) {
      ElMessage.success(res.msg || '已驳回');
      emit('refresh');
      emit('close');
    } else {
      ElMessage.error(res?.msg || '驳回失败');
    }
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e?.response?.data?.msg || e?.message || '驳回失败');
  }
};

// 处理关闭
const handleClose = () => {
  emit('close');
};

// 加载指定线路下的车辆列表
const loadRoadlineVehicles = async (roadlineId: string) => {
  if (!roadlineId) {
    roadlineVehicles.value = [];
    return;
  }
  
  try {
    roadlineVehiclesLoading.value = true;
    const res = await request({
      url: vehicleApiPrefix,
      method: 'get',
      params: { 
        limit: 9999, 
        roadline: roadlineId,  // 按线路ID筛选
      },
    });
    let dataArray: any[] = [];
    if (res && res.data) {
      if (Array.isArray(res.data)) {
        dataArray = res.data;
      } else if (res.data.results && Array.isArray(res.data.results)) {
        dataArray = res.data.results;
      }
    }
    roadlineVehicles.value = dataArray;
  } catch (error) {
    console.error('加载线路车辆列表失败:', error);
    roadlineVehicles.value = [];
  } finally {
    roadlineVehiclesLoading.value = false;
  }
};

// 编辑车位（原方法，保留用于兼容）
const handleEditPosition = async (row: any) => {
  // 获取 roadline_id，可能是字符串或对象
  const roadlineId = typeof row.roadline_id === 'object' ? row.roadline_id?.id : row.roadline_id;
  // 获取 vehicle_id，可能是字符串或对象
  const vehicleId = typeof row.vehicle_id === 'object' ? row.vehicle_id?.id : row.vehicle_id;
  
  // 填充表单数据
  editPositionForm.value = {
    id: row.id,
    vehicle_id: vehicleId || '',
    roadline_id: roadlineId || '',
    roadline_name: row.roadline_name || '',
    reserved_start_date: row.reserved_start_date || '',
    reserved_end_date: row.reserved_end_date || '',
  };
  
  // 打开对话框
  editPositionDialogVisible.value = true;
  
  // 加载该线路下的车辆列表
  await loadRoadlineVehicles(roadlineId);
};

// 编辑车辆的车位（按车辆分组后的编辑方法）
const handleEditVehiclePositions = async (row: any) => {
  // 如果该车辆只有一个车位，直接编辑该车位
  if (row.positions && row.positions.length === 1) {
    await handleEditPosition(row.positions[0]);
    return;
  }
  
  // 如果有多个车位，提示用户该车辆有多个车位，需要分别编辑
  ElMessage.info(`该车辆共有 ${row.positionCount} 个车位，请分别编辑每个车位`);
  
  // 可以在这里打开一个对话框显示该车辆的所有车位，让用户选择编辑
  // 目前先提示用户，后续可以根据需求扩展
};

// 保存车位编辑
const handleSavePosition = async () => {
  if (!editPositionForm.value.vehicle_id) {
    ElMessage.warning('请选择车辆');
    return;
  }

  try {
    editPositionLoading.value = true;

    // 如果是营运公司换车操作，使用专用接口
    if (editPositionForm.value._isSwap) {
      const res = await request({
        url: `/api/BookingOrderModelViewSet/${orderId.value}/company_swap_vehicle/`,
        method: 'post',
        data: {
          position_id: editPositionForm.value.id,
          new_vehicle_id: editPositionForm.value.vehicle_id,
          swap_reason: '营运公司换车',
        },
      });
      if (res && res.code === 2000) {
        ElMessage.success(res.msg || '换车成功');
        editPositionDialogVisible.value = false;
        await loadAllPositions();
        return;
      } else {
        ElMessage.error(res?.msg || '换车失败');
        return;
      }
    }

    // 普通编辑模式
    const currentRes = await request({
      url: `/api/VehicleAdPositionModelViewSet/${editPositionForm.value.id}/`,
      method: 'get',
    });

    if (!currentRes || !currentRes.data) {
      throw new Error('获取当前数据失败');
    }

    const currentData = currentRes.data;
    const selectedVehicle = roadlineVehicles.value.find(
      (v: any) => v.id === editPositionForm.value.vehicle_id
    );

    await request({
      url: `/api/VehicleAdPositionModelViewSet/${editPositionForm.value.id}/`,
      method: 'put',
      data: {
        ...currentData,
        vehicle_id: editPositionForm.value.vehicle_id,
        vehicle_no: selectedVehicle?.vehicle_no || currentData.vehicle_no,
      },
    });

    ElMessage.success('保存成功');
    editPositionDialogVisible.value = false;

    if (selectedDetailId.value) {
      await loadPositions(selectedDetailId.value);
    } else {
      await loadAllPositions();
    }
  } catch (error: any) {
    console.error('保存车位失败:', error);
    ElMessage.error(error?.response?.data?.msg || error?.message || '保存失败');
  } finally {
    editPositionLoading.value = false;
  }
};

// 删除车位
const handleDeletePosition = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确认删除车辆编号为 "${row.vehicle_no}" 的车位分配吗？`,
      '确认删除',
      {
        type: 'warning',
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
      }
    );
    
    // 调用删除API
    await request({
      url: `/api/VehicleAdPositionModelViewSet/${row.id}/`,
      method: 'delete',
    });
    
    ElMessage.success('删除成功');
    
    // 重新加载车位列表
    if (selectedDetailId.value) {
      await loadPositions(selectedDetailId.value);
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除车位失败:', error);
      ElMessage.error('删除失败');
    }
  }
};

// 监听 data prop 变化，如果有初始数据则使用
watch(
  () => props.data,
  (newData) => {
    if (newData && Object.keys(newData).length > 0) {
      // 如果有初始数据，直接使用，不再从接口加载
      mainOrder.value = { ...newData };
    }
  },
  { immediate: true, deep: true }
);

// 监听 formParams.id 变化，重新加载数据
watch(
  () => orderId.value,
  async (newId) => {
    if (newId && !props.data) {
      // 只有在没有初始数据时才从接口加载
      await loadMainOrder();
      await loadDetailList();
      await loadAllPositions();
    }
  },
  { immediate: false }
);

// 组件挂载时加载数据
onMounted(async () => {
  // 并行加载基础数据（用于显示名称）
  await Promise.all([
    loadRoadlineList(),
    loadCompanyList(),
    loadMediaTypeList(),
    loadVehicleList(),
    loadCustomerList(),
    loadAgentList(),
  ]);
  
  // 如果有初始数据，直接使用，否则从接口加载
  if (props.data && Object.keys(props.data).length > 0) {
    // 使用初始数据，但仍需要加载明细和车位数据
    await loadDetailList();
    await loadAllPositions();
  } else if (orderId.value) {
    // 从接口加载主单和明细数据
    await loadMainOrder();
    await loadDetailList();
    // 加载所有车位数据（需要在明细数据加载完成后）
    await loadAllPositions();
  } else {
    console.warn('[BookingOrderReviewPage] 未提供订单ID或初始数据');
  }
});
</script>

<style scoped>
.review-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

.section-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.section-card:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #909399;
}

.loading-container .el-icon {
  margin-right: 8px;
  font-size: 20px;
}

:deep(.el-table .selected-row) {
  background-color: #ecf5ff;
}

:deep(.el-table .selected-row:hover > td) {
  background-color: #d9ecff !important;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
  background-color: #fafafa;
}
</style>
