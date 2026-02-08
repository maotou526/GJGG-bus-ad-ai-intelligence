<!--
 * @Description: 站点关联管理页面
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-14
 * @LastEditors: 王晨
 * @LastEditTime: 2025-10-14
-->
<template>
    <fs-page class="PageFeatureSearchMulti">
        <fs-crud ref="crudRef" v-bind="crudBinding">
            <template #cell_url="scope">
                <el-tag size="small">{{ scope.row.url }}</el-tag>
            </template>
            <!-- 导入功能 -->
            <template #actionbar-right>
                <importExcel api="api/RoadlineStopRelModelViewSet/" v-auth="'user:Import'">导入</importExcel>
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


export default defineComponent({    //这里配置defineComponent
    name: "RoadlineStopRelModelViewSet",   //把name放在这里进行配置了
	components: {importExcel},  //注册组件
    setup() {   //这里配置了setup()

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
		//增加了return把需要给上面<template>内调用的<fs-crud ref="crudRef" v-bind="crudBinding">
				crudBinding,
				crudRef,
			};
	

    } 	//这里关闭setup()
  });  //关闭defineComponent

</script>

<style scoped> 
</style>

