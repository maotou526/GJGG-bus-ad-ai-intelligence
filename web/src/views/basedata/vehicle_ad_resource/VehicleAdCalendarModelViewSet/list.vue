<!--
 * @Description: 车辆广告资源位管理（普通列表）
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
-->
<template>
  <!-- 纯列表视图：不再自带筛选栏和 fs-page，筛选由外部模板页传入 -->
  <!-- 注意：外层 index.vue 已经有 fs-page，这里只渲染 crud -->
  <div class="list-container">
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <!-- 资源状态颜色显示 -->
      <template #cell_resource_status_display="scope">
        <el-tag 
          :type="getStatusTagType(scope.row)" 
          size="small"
        >
          {{ scope.row.resource_status_display || '未知' }}
        </el-tag>
      </template>
    </fs-crud>
  </div>
</template>

<script lang="ts" setup name="VehicleAdResourceModelViewSetList">
import { onMounted, getCurrentInstance, watch, nextTick } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';
import { ElTag } from 'element-plus';

// 根据状态获取标签类型（与 ScheduleCalendar.vue 一致）
const getStatusTagType = (row: any) => {
  const statusValue = row.resource_status;
  const statusText = row.resource_status_display || '未知';
  
  // 优先根据显示文本判断（支持自动判断的"到期未下刊"）
  if (statusText === '预订') {
    return 'warning'; // 预订 - 对应 reserved (#e6a23c)
  } else if (statusText === '在刊') {
    return 'success'; // 在刊 - 对应 active (#67c23a)
  } else if (statusText === '下刊') {
    return 'info'; // 下刊 - 对应 finished (#909399)
  } else if (statusText === '到期未下刊') {
    return 'danger'; // 到期未下刊 - 危险色
  } else if (statusText === '维修中') {
    return 'warning'; // 维修中
  } else if (statusText === '不可用') {
    return 'danger'; // 不可用
  } else if (statusText === '空闲') {
    return 'info'; // 空闲
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

// 外部传入的固定筛选条件（来自模板页）
const props = defineProps<{
  externalFilters?: {
    resource_code?: string;
    roadline_id?: string;
    vehicle_id?: string;
    resource_status?: number | null;
    base_media_type_id?: string;
    scheduled_start_date__gte?: string;
    scheduled_end_date__lte?: string;
  };
}>();

const instance = getCurrentInstance();

// 创建响应式的 context，确保筛选条件变化时能够更新
const context: any = {
  componentName: instance?.type.name,
  get externalFilters() {
    return props.externalFilters;
  },
};

const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions, context });

// 根据外部筛选条件触发查询
const applyExternalFilters = () => {
  // 等待 crudExpose 和 crudRef 初始化完成
  if (!crudExpose || !crudRef.value) {
    return;
  }
  
  const filters = props.externalFilters || {};
  
  try {
    // 设置搜索表单的值
    if (typeof crudExpose.setSearchFormData === 'function') {
      crudExpose.setSearchFormData({ form: filters });
    }
    
    // 刷新数据
    if (typeof crudExpose.doRefresh === 'function') {
      crudExpose.doRefresh();
    }
  } catch (error) {
    console.error('应用筛选条件时出错:', error);
  }
};

// 监听 crudExpose 的初始化，确保初始化完成后加载数据
watch(
  () => crudExpose,
  (expose) => {
    if (expose && crudRef.value) {
      // 当 crudExpose 初始化完成后，延迟触发数据加载
      nextTick(() => {
        setTimeout(() => {
          applyExternalFilters();
        }, 300);
      });
    }
  },
  { immediate: true }
);

// 首次加载 - 使用 onMounted 作为备用方案
onMounted(() => {
  nextTick(() => {
    setTimeout(() => {
      applyExternalFilters();
    }, 500);
  });
});

// 模板页筛选变化时，自动刷新列表
watch(
  () => props.externalFilters,
  () => {
    // 当筛选条件变化时刷新
    nextTick(() => {
      applyExternalFilters();
    });
  },
  { deep: true }
);
</script>

<style scoped>
.list-container {
  width: 100%;
  flex: 1;
  min-height: 0;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background: white;
  display: flex;
  flex-direction: column;
}

/* 让 FastCrud 内部主体区域按 flex 撑满，避免表格下方出现大块留白 */
.list-container :deep(.fs-crud) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.list-container :deep(.fs-crud-body) {
  flex: 1;
  min-height: 0;
}
</style>

