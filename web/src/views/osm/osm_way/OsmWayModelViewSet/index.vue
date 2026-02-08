<!--
 * @Description: OSM道路管理
 * @Version: 1.0
 * @Autor: 系统生成
 * @Date: 2025-10-23
-->
<template>
    <fs-page class="PageFeatureSearchMulti">
        <fs-crud ref="crudRef" v-bind="crudBinding">
            <template #actionbar-right>
                <importExcel api="api/OsmWayModelViewSet/" v-auth="'OsmWayModelViewSet:Import'">导入</importExcel>
            </template>
        </fs-crud>
    </fs-page>
</template>

<script lang="ts">
import { onMounted, getCurrentInstance, defineComponent} from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions  from './crud';
import importExcel from '/@/components/importExcel/index.vue'   

export default defineComponent({
    name: "OsmWayModelViewSet",
	components: {importExcel},
    setup() {
		const instance = getCurrentInstance();
		const context: any = {
			componentName: instance?.type.name
		};
		const { crudBinding, crudRef, crudExpose, resetCrudOptions } = useFs({ createCrudOptions, context});

		// 页面打开后获取列表数据
		onMounted(() => {
			crudExpose.doRefresh();
		});
		return {  
				crudBinding,
				crudRef,
			};
    }
  });
</script>

<style scoped> 
</style>

