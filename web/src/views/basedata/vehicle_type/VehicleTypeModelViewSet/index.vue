<!--
 * @Description: 车型管理
-->
<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <template #actionbar-right>
        <importExcel api="api/VehicleTypeModelViewSet/" v-auth="'user:Import'">导入</importExcel>
      </template>
    </fs-crud>
  </fs-page>
  </template>

<script lang="ts">
import { onMounted, getCurrentInstance, defineComponent } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';
import importExcel from '/@/components/importExcel/index.vue';
import { handleColumnPermission } from '/@/utils/columnPermission';
import { GetPermission } from './api';

export default defineComponent({
  name: 'VehicleTypeModelViewSet',
  components: { importExcel },
  setup() {
    const instance = getCurrentInstance();
    const context: any = { componentName: instance?.type.name };
    const { crudBinding, crudRef, crudExpose, crudOptions, resetCrudOptions } = useFs({ createCrudOptions });
    onMounted(async () => {
      const newOptions = await handleColumnPermission(GetPermission, crudOptions);
      resetCrudOptions(newOptions);
      crudExpose.doRefresh();
    });
    return { crudBinding, crudRef };
  },
});
</script>

<style scoped lang="scss">
</style>

