<!--
 * @Description: 车辆管理
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-18
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-18
-->
<template>
    <fs-page class="PageFeatureSearchMulti">
        <fs-crud ref="crudRef" v-bind="crudBinding">
            <template #cell_url="scope">
                <el-tag size="small">{{ scope.row.url }}</el-tag>
            </template>
            <!-- 导入组件 -->
            <template #actionbar-right>
                <importExcel api="api/VehicleModelViewSet/" v-auth="'user:Import'">导入</importExcel>
            </template>

        </fs-crud>
    </fs-page>
</template>

<script lang="ts">
import { onMounted, getCurrentInstance, defineComponent} from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions  from './crud';

// 导入组件
import importExcel from '/@/components/importExcel/index.vue'   


export default defineComponent({
    name: "VehicleModelViewSet",
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

