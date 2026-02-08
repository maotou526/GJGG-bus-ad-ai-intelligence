<!--
 * @Description: 公交线路复线情况管理页面
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-12-01 00:00:00
 * @LastEditors: 王晨
 * @LastEditTime: 2025-12-01 16:20:17
-->
<template>
  <fs-page class="PageFeatureSearchMulti">
      <fs-crud ref="crudRef" v-bind="crudBinding">
          <template #cell_url="scope">
              <el-tag size="small">{{ scope.row.url }}</el-tag>
          </template>
          <template #actionbar-right>
              <importExcel api="api/RoadlineToRoadlineOverlapModelViewSet/" v-auth="'user:Import'">导入</importExcel>
          </template>
      </fs-crud>
  </fs-page>
</template>

<script lang="ts">
import { defineComponent, getCurrentInstance, onMounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';
import importExcel from '/@/components/importExcel/index.vue'   

export default defineComponent({
  name: 'RoadlineToRoadlineOverlapModelViewSet',
  components: { importExcel },
  setup() {
    const instance = getCurrentInstance();
    const context: any = {
      componentName: instance?.type.name,
    };

    const { crudBinding, crudRef, crudExpose } = useFs({
      createCrudOptions,
      context,
    });

    onMounted(() => {
      crudExpose.doRefresh();
    });

    return {
      crudBinding,
      crudRef,
    };
  },
});
</script>

<style scoped>
</style>


