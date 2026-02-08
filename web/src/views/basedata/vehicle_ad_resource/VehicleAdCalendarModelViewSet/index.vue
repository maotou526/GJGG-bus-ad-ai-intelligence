<!--
 * @Description: 车辆广告资源位排期视图（固定筛选 + 列表 / 日历）
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
-->
<template>
  <fs-page class="VehicleAdResourceTemplate">
    <!-- Header -->
    <div class="module-header">
      <div class="header-left">
        <h2>资源管理</h2>
        <span class="subtitle">{{ pageTitle }}</span>
      </div>
      <div class="ai-helper">
        <i class="ri-lightbulb-flash-line"></i> {{ helperText }}
      </div>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="filters">
        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px"
          value-format="YYYY-MM-DD"
          @change="handleSearch"
        />
        <el-select
          v-model="searchForm.roadline_id"
          placeholder="线路"
          clearable
          filterable
          style="width: 200px"
          @change="handleRoadlineChange"
        >
          <el-option
            v-for="item in roadlineList"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-select
          v-model="searchForm.vehicle_id"
          placeholder="车辆"
          clearable
          filterable
          style="width: 200px"
          @change="handleSearch"
        >
          <el-option
            v-for="item in filteredVehicleList"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-select
          v-model="searchForm.base_media_type_id"
          placeholder="媒体类型"
          clearable
          filterable
          style="width: 150px"
          @change="handleSearch"
        >
          <el-option
            v-for="item in mediaTypeList"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
        <el-select
          v-model="searchForm.resource_status"
          placeholder="资源状态"
          clearable
          style="width: 150px"
          @change="handleSearch"
        >
          <el-option label="空闲" :value="1" />
          <el-option label="预订" :value="2" />
          <el-option label="在刊" :value="3" />
          <el-option label="下刊" :value="4" />
          <el-option label="维修中" :value="5" />
          <el-option label="不可用" :value="6" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <div class="actions">
        <el-radio-group v-model="mode" size="default">
          <el-radio-button label="list"><el-icon><List /></el-icon> 列表</el-radio-button>
          <el-radio-button label="calendar"><el-icon><Calendar /></el-icon> 日历</el-radio-button>
        </el-radio-group>
        <el-divider direction="vertical" />
        <el-dropdown @command="handleExport">
          <el-button type="success" :icon="Download">
            导出
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
              <el-dropdown-item command="pdf">导出 PDF</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- Content -->
    <div class="content-area" v-loading="calendarLoading && mode === 'calendar'">
      <el-alert v-if="errorMessage" :title="errorMessage" type="error" show-icon :closable="false" class="error-alert" />

      <template v-if="mode === 'list'">
        <!-- 列表：使用 list.vue，筛选条件从搜索表单获取 -->
        <VehicleAdResourceList 
          :key="`list-${JSON.stringify(currentFilters)}`"
          :external-filters="currentFilters" 
        />
      </template>
      <template v-else>
        <!-- 日历：直接使用 ScheduleCalendar 组件 -->
        <el-empty v-if="!calendarLoading && calendarVehicles.length === 0 && calendarSchedules.length === 0 && !errorMessage" description="暂无数据" />
        <ScheduleCalendar
          v-else-if="!calendarLoading || calendarVehicles.length > 0 || calendarSchedules.length > 0"
          :key="`calendar-${JSON.stringify(currentFilters)}`"
          :vehicles="calendarVehicles"
          :schedules="calendarSchedules"
          :loading="calendarLoading"
          @view="handleView"
          @update="handleScheduleUpdate"
        />
      </template>
    </div>

    <!-- Edit/Add Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑排期' : '新增排期'"
      width="600px"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="选择车辆" prop="vehicleId">
          <el-select v-model="form.vehicleId" placeholder="请选择车辆" style="width: 100%">
            <el-option
              v-for="v in vehicleList"
              :key="v.value"
              :label="v.label"
              :value="v.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="资源编码" prop="resourceCode">
          <el-input v-model="form.resourceCode" placeholder="请输入资源编码" />
        </el-form-item>

        <el-form-item label="媒体类型" prop="mediaTypeId">
          <el-select v-model="form.mediaTypeId" placeholder="请选择媒体类型" style="width: 100%">
            <el-option
              v-for="item in mediaTypeList"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="资源状态" prop="resourceStatus">
          <el-radio-group v-model="form.resourceStatus">
            <el-radio :label="1">空闲</el-radio>
            <el-radio :label="2">预订</el-radio>
            <el-radio :label="3">在刊</el-radio>
            <el-radio :label="4">下刊</el-radio>
            <el-radio :label="5">维修中</el-radio>
            <el-radio :label="6">不可用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="排期时间" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 广告详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="广告投放详情"
      width="1400px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div v-loading="detailLoading">
        <template v-if="detailData">
          <!-- 广告排期 -->
          <el-divider content-position="left">广告排期 ({{ detailData.positions?.length || 0 }}个)</el-divider>
          <el-table :data="detailData.positions" border stripe max-height="700" style="width: 100%">
            <el-table-column type="index" label="序号" width="60" align="center" fixed="left" />
            <el-table-column prop="resourceCode" label="资源编码" width="150" show-overflow-tooltip />
            <el-table-column prop="vehiclePlate" label="车牌号" width="120" />
            <el-table-column prop="vehicleNo" label="车辆自编号" width="120" />
            <el-table-column prop="mediaTypeName" label="媒体类型" width="120" />
            <el-table-column prop="roadlineName" label="线路名称" width="150" show-overflow-tooltip />
            <el-table-column prop="roadlineCompanyName" label="营运公司" width="150" show-overflow-tooltip />
            <el-table-column prop="actualOnDate" label="上刊日期" width="130" align="left">
              <template #default="{ row }">
                {{ row.actualOnDate || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="reservedStartDate" label="投放开始日期" width="130" align="left" />
            <el-table-column prop="reservedEndDate" label="投放结束日期" width="130" align="left" />     
            <el-table-column prop="actualOffDate" label="下刊日期" width="130" align="left">
              <template #default="{ row }">
                {{ row.actualOffDate || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="resourceStatusDisplay" label="资源状态" width="100" align="left" fixed="right">
              <template #default="{ row }">
                <el-tag :type="getResourceStatusTagType(row.resourceStatusDisplay)" size="small">
                  {{ row.resourceStatusDisplay }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </template>
        <el-empty v-else-if="!detailLoading" description="暂无数据" />
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </fs-page>
</template>

<script lang="ts" setup name="VehicleAdCalendarModelViewSet">
import { ref, watch, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage, type FormInstance } from 'element-plus';
import { List, Calendar, Search, Plus, Download, ArrowDown } from '@element-plus/icons-vue';
import * as api from './api';
import { request } from '/@/utils/service';
import VehicleAdResourceList from './list.vue';
import ScheduleCalendar from './ScheduleCalendar.vue';
import {
  type Vehicle as CalendarVehicle,
  type AdSchedule as CalendarSchedule,
} from '/@/stores/adSchedule';

const route = useRoute();

// 视图模式：列表 / 日历
const mode = ref<'list' | 'calendar'>('list');

// 搜索表单
const searchForm = ref({
  resource_code: '',
  roadline_id: '',
  vehicle_id: '',
  resource_status: null as number | null,
  base_media_type_id: '',
  dateRange: [] as string[],
});

// 当前筛选条件（过滤空值）
const currentFilters = computed(() => {
  const filters: any = {};
  if (searchForm.value.resource_code) {
    filters.resource_code = searchForm.value.resource_code;
  }
  if (searchForm.value.roadline_id) {
    filters.roadline_id = searchForm.value.roadline_id;
  }
  if (searchForm.value.vehicle_id) {
    filters.vehicle_id = searchForm.value.vehicle_id;
  }
  if (searchForm.value.resource_status !== null && searchForm.value.resource_status !== undefined) {
    filters.resource_status = searchForm.value.resource_status;
  }
  if (searchForm.value.base_media_type_id) {
    filters.base_media_type_id = searchForm.value.base_media_type_id;
  }
  if (searchForm.value.dateRange && searchForm.value.dateRange.length === 2) {
    filters.scheduled_start_date__gte = searchForm.value.dateRange[0];
    filters.scheduled_end_date__lte = searchForm.value.dateRange[1];
  }
  return filters;
});

// 页面标题和提示
const pageTitle = computed(() => {
  const title = route.meta.title;
  if (typeof title === 'string' && title) return title;
  return '车辆广告资源位排期管理';
});

const helperText = computed(() => {
  if (mode.value === 'calendar') return '';
  return '';
});

// 线路列表
const roadlineList = ref<Array<{ value: string; label: string }>>([]);
const roadlineApiPrefix = '/api/RoadlineModelViewSet/';

// 车辆列表（完整列表）
const vehicleList = ref<Array<{ value: string; label: string; roadline_id?: string }>>([]);
const vehicleApiPrefix = '/api/VehicleModelViewSet/';

// 过滤后的车辆列表（根据选中的线路）
const filteredVehicleList = computed(() => {
  if (!searchForm.value.roadline_id) {
    return vehicleList.value;
  }
  return vehicleList.value.filter(v => v.roadline_id === searchForm.value.roadline_id);
});

// 媒体类型列表
const mediaTypeList = ref<Array<{ value: string; label: string }>>([]);
const mediaTypeApiPrefix = '/api/AdMediaTypeModelViewSet/';

// 加载线路列表
const loadRoadlineList = async () => {
  try {
    const res = await request({
      url: roadlineApiPrefix,
      method: 'get',
      params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
    });
    const data = Array.isArray(res?.data) ? res.data : (res?.data?.results || []);
    if (data.length > 0) {
      roadlineList.value = data.map((item: any) => ({
        value: item.id,
        label: item.line_name || `线路ID:${item.id}`,
      }));
    }
  } catch (error) {
    console.error('加载线路列表失败:', error);
  }
};

// 加载车辆列表
const loadVehicleList = async () => {
  try {
    const res = await request({
      url: vehicleApiPrefix,
      method: 'get',
      params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
    });
    const data = Array.isArray(res?.data) ? res.data : (res?.data?.results || []);
    if (data.length > 0) {
      vehicleList.value = data.map((item: any) => {
        const plate = item.vehicle_plate || '';
        const no = item.vehicle_no || '';
        let label = '';
        if (plate && no) {
          label = `${plate}（${no}）`;
        } else if (plate) {
          label = plate;
        } else if (no) {
          label = `（${no}）`;
        } else {
          label = `车辆ID:${item.id}`;
        }
        return {
          value: item.id,
          label,
          roadline_id: item.roadline_id || item.roadline, // 保存线路ID用于过滤
        };
      });
    }
  } catch (error) {
    console.error('加载车辆列表失败:', error);
  }
};

// 加载媒体类型列表
const loadMediaTypeList = async () => {
  try {
    const res = await request({
      url: mediaTypeApiPrefix,
      method: 'get',
      params: { limit: 9999, is_composite: false, enabled_mark: 1, delete_mark: 0 },
    });
    const data = Array.isArray(res?.data) ? res.data : (res?.data?.results || []);
    if (data.length > 0) {
      mediaTypeList.value = data.map((item: any) => ({
        value: item.id,
        label: item.media_name || `媒体类型ID:${item.id}`,
      }));
    }
  } catch (error) {
    console.error('加载媒体类型列表失败:', error);
  }
};

// 线路变化处理
const handleRoadlineChange = () => {
  // 当线路变化时，清空车辆选择（因为车辆列表已经被过滤）
  searchForm.value.vehicle_id = '';
  handleSearch();
};

// 查询
const handleSearch = () => {
  // 筛选条件变化会自动触发列表/日历刷新
  if (mode.value === 'calendar') {
    loadCalendarData();
  }
};

// 重置
const handleReset = () => {
  searchForm.value = {
    resource_code: '',
    roadline_id: '',
    vehicle_id: '',
    resource_status: null,
    base_media_type_id: '',
    dateRange: [],
  };
  if (mode.value === 'calendar') {
    loadCalendarData();
  }
};

// 日历数据
const calendarLoading = ref(false);
const calendarVehicles = ref<CalendarVehicle[]>([]);
const calendarSchedules = ref<CalendarSchedule[]>([]);
const errorMessage = ref('');

// 兼容后端两种列表返回
const getListData = (resp: any): any[] => {
  const data = resp?.data;
  if (Array.isArray(data)) return data;
  if (data && Array.isArray(data.results)) return data.results;
  return [];
};

// 根据当前筛选条件加载日历数据（按预订单聚合，显示广告内容）
const loadCalendarData = async () => {
  calendarLoading.value = true;
  errorMessage.value = '';
  try {
    // 使用新的按预订单聚合的 API
    const query: any = {};
    if (searchForm.value.roadline_id) {
      query.roadline_id = searchForm.value.roadline_id;
    }
    if (searchForm.value.vehicle_id) {
      query.vehicle_id = searchForm.value.vehicle_id;
    }
    // 添加日期筛选参数（日历 API 使用 reserved_start_date 和 reserved_end_date）
    if (searchForm.value.dateRange && searchForm.value.dateRange.length === 2) {
      query.reserved_start_date__gte = searchForm.value.dateRange[0];
      query.reserved_end_date__lte = searchForm.value.dateRange[1];
    }
    
    const res: any = await request({
      url: '/api/VehicleAdResourceModelViewSet/get_gantt_by_booking_order/',
      method: 'get',
      params: query,
    });

    if (res.code === 2000 && res.data) {
      // 新 API 直接返回格式化好的数据
      calendarVehicles.value = res.data.vehicles || [];
      calendarSchedules.value = (res.data.schedules || []).map((s: any) => ({
        id: s.id,
        vehicleId: s.vehicleId,
        advertiser: s.advertiser || '广告内容',
        adType: s.adType || '',
        status: s.status || 'reserved',
        startDate: s.startDate,
        endDate: s.endDate,
        // 扩展字段，用于详情弹窗
        bookingOrderId: s.bookingOrderId,
        bookingNo: s.bookingNo,
        customerName: s.customerName,
        positionCount: s.positionCount,
        // 用于判断到期未下刊的字段
        off_air_date: s.off_air_date,
        scheduled_end_date: s.scheduled_end_date,
      }));
    } else {
      errorMessage.value = res.msg || '加载日历数据失败';
    }
  } catch (error: any) {
    errorMessage.value = error?.message || '加载日历数据失败';
  } finally {
    calendarLoading.value = false;
  }
};

// 对话框相关
const dialogVisible = ref(false);
const isEdit = ref(false);
const formRef = ref<FormInstance>();

const form = ref({
  id: '',
  vehicleId: '',
  resourceCode: '',
  mediaTypeId: '',
  resourceStatus: 1,
  dateRange: [] as string[],
});

const rules = {
  vehicleId: [{ required: true, message: '请选择车辆', trigger: 'change' }],
  resourceCode: [{ required: true, message: '请输入资源编码', trigger: 'blur' }],
  mediaTypeId: [{ required: true, message: '请选择媒体类型', trigger: 'change' }],
  dateRange: [{ required: true, message: '请选择时间范围', trigger: 'change' }],
};

const handleAdd = () => {
  isEdit.value = false;
  form.value = {
    id: '',
    vehicleId: '',
    resourceCode: '',
    mediaTypeId: '',
    resourceStatus: 1,
    dateRange: [],
  };
  dialogVisible.value = true;
};

// 详情弹窗相关
const detailDialogVisible = ref(false);
const detailLoading = ref(false);
const detailData = ref<{
  bookingOrder: any;
  positions: any[];
} | null>(null);

const handleView = async (schedule: any) => {
  // 从 schedule 中获取 vehicleId 和 bookingOrderId
  const vehicleId = schedule.vehicleId;
  // 从组合ID中提取 bookingOrderId（格式：vehicleId_bookingOrderId）
  let bookingOrderId = schedule.bookingOrderId;
  if (!bookingOrderId && schedule.id && schedule.id.includes('_')) {
    bookingOrderId = schedule.id.split('_')[1];
  }
  
  if (!vehicleId || !bookingOrderId) {
    ElMessage.warning('无法获取详情信息');
    return;
  }
  
  detailDialogVisible.value = true;
  detailLoading.value = true;
  detailData.value = null;
  
  try {
    const res: any = await request({
      url: '/api/VehicleAdResourceModelViewSet/get_positions_by_booking/',
      method: 'get',
      params: {
        vehicle_id: vehicleId,
        booking_order_id: bookingOrderId,
      },
    });
    
    if (res.code === 2000 && res.data) {
      detailData.value = res.data;
    } else {
      ElMessage.error(res.msg || '获取详情失败');
    }
  } catch (error: any) {
    ElMessage.error(error?.message || '获取详情失败');
  } finally {
    detailLoading.value = false;
  }
};

const handleScheduleUpdate = async (schedule: CalendarSchedule) => {
  try {
    // 根据 schedule 的 id 查找原始数据，获取完整的资源位信息
    const query: any = {
      ...currentFilters.value,
      limit: 0,
    };
    const res: any = await api.GetList(query);
    const data = getListData(res);
    const originalItem = data.find((item: any) => String(item.id) === schedule.id);
    
    if (!originalItem) {
      ElMessage.error('未找到对应的资源位数据');
      return;
    }

    // 构建更新数据
    const payload: any = {
      id: originalItem.id,
      vehicle_id: originalItem.vehicle_id,
      resource_code: originalItem.resource_code,
      base_media_type_id: originalItem.base_media_type_id,
      resource_status: originalItem.resource_status,
      scheduled_start_date: schedule.startDate,
      scheduled_end_date: schedule.endDate,
    };

    await api.UpdateObj(payload);
    ElMessage.success('排期更新成功');
    // 刷新日历数据
    await loadCalendarData();
  } catch (error: any) {
    ElMessage.error(error?.message || '更新失败');
  }
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate((valid) => {
    if (valid) {
      try {
        const payload: any = {
          vehicle_id: form.value.vehicleId,
          resource_code: form.value.resourceCode,
          base_media_type_id: form.value.mediaTypeId,
          resource_status: form.value.resourceStatus,
          scheduled_start_date: form.value.dateRange[0],
          scheduled_end_date: form.value.dateRange[1],
        };

        if (isEdit.value) {
          payload.id = form.value.id;
          api.UpdateObj(payload).then(() => {
            ElMessage.success('排期更新成功');
            dialogVisible.value = false;
            if (mode.value === 'calendar') {
              loadCalendarData();
            }
          });
        } else {
          api.AddObj(payload).then(() => {
            ElMessage.success('排期创建成功');
            dialogVisible.value = false;
            if (mode.value === 'calendar') {
              loadCalendarData();
            }
          });
        }
      } catch (error: any) {
        ElMessage.error(error?.message || '操作失败');
      }
    }
  });
};

// 导出功能
const handleExport = async (type: 'excel' | 'pdf') => {
  try {
    const query: any = {
      ...currentFilters.value,
      limit: 0,
    };
    const res: any = await api.GetList(query);
    const data = getListData(res);

    if (type === 'excel') {
      const header = ['资源编码', '车牌', '线路', '媒体类型', '资源状态', '投放开始日期', '投放结束日期'];
      const lines = [header];
      for (const item of data) {
        const statusMap: Record<number, string> = {
          1: '空闲',
          2: '预订',
          3: '在刊',
          4: '下刊',
          5: '维修中',
          6: '不可用',
        };
        lines.push([
          item.resource_code || '',
          item.vehicle_plate || '',
          item.roadline_name || '',
          item.media_type_name || '',
          statusMap[item.resource_status] || '',
          item.scheduled_start_date || '',
          item.scheduled_end_date || '',
        ]);
      }
      const csv = '\ufeff' + lines.map(cols => cols.map(c => `"${String(c).replace(/"/g, '""')}"`).join(',')).join('\n');
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `车辆广告资源位排期_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      ElMessage.success('已导出 CSV，可用 Excel 打开');
    } else {
      ElMessage.info('PDF 导出功能开发中');
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '导出失败');
  }
};

// 当视图模式切换时，如果是日历模式则加载数据
watch(
  mode,
  (newMode) => {
    if (newMode === 'calendar') {
      loadCalendarData();
    }
  }
);

// 当筛选条件变化时，自动刷新日历
watch(
  currentFilters,
  () => {
    if (mode.value === 'calendar') {
      loadCalendarData();
    }
  },
  { deep: true }
);

// 根据资源状态显示文本返回对应的 el-tag type，与摘要面板颜色保持一致
const getResourceStatusTagType = (statusDisplay: string) => {
  if (!statusDisplay) return 'info'
  const status = String(statusDisplay).trim()
  
  // 预订 -> warning (橙色 #e6a23c) - 对应 reserved
  if (status === '预订') return 'warning'
  // 在刊 -> success (绿色 #67c23a) - 对应 active
  if (status === '在刊') return 'success'
  // 下刊 -> info (灰色 #909399) - 对应 finished
  if (status === '下刊') return 'info'
  // 到期未下刊 -> danger (红色) - 对应 expired
  if (status === '到期未下刊') return 'danger'
  // 空闲 -> info (默认灰色)
  if (status === '空闲') return 'info'
  // 维修中 -> warning (橙色)
  if (status === '维修中') return 'warning'
  // 不可用 -> danger (红色)
  if (status === '不可用') return 'danger'
  
  return 'info'
}

// 初始化
onMounted(() => {
  loadRoadlineList();
  loadVehicleList();
  loadMediaTypeList();
});
</script>

<style scoped>
.VehicleAdResourceTemplate {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.module-header h2 {
  margin: 0;
  font-size: 18px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.subtitle {
  color: #909399;
  font-size: 12px;
}

.ai-helper {
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  padding: 2px 10px;
  border-radius: 15px;
  font-size: 12px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.content-area {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.error-alert {
  margin-bottom: 12px;
}

@media (max-width: 768px) {
  .VehicleAdResourceTemplate {
    padding: 12px;
  }
}
</style>
