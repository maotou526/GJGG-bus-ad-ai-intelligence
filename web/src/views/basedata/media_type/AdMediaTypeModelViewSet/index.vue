<!--
 * @Description: 媒体类型管理页面
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors: 
 * @LastEditTime: 2025-01-XX
-->
<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<!-- 注释编号: django-vue3-admin-index442216: -->
			<!-- 注释编号:django-vue3-admin-index39263917:代码开始行-->
			<!--  功能说明:使用导入组件，并且修改api地址为当前对应的api，当前是media_type的api="api/AdMediaTypeModelViewSet/"-->
			<template #actionbar-right>
				<importExcel api="api/AdMediaTypeModelViewSet/" v-auth="'user:Import'">导入</importExcel>
			</template>
			<!--  注释编号:django-vue3-admin-index263917:代码结束行-->
		</fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="AdMediaTypeModelViewSet">
import { onMounted, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';

// 注释编号: django-vue3-admin-index192316:导入组件
import importExcel from '/@/components/importExcel/index.vue';
import ComponentTypeSelector from './components/ComponentTypeSelector.vue';

const { crudBinding, crudRef, crudExpose, crudOptions, resetCrudOptions } = useFs({ 
	createCrudOptions,
	// 注册自定义组件
	componentRefs: {
		'ComponentTypeSelector': ComponentTypeSelector,
	},
});

// 页面打开后获取列表数据
onMounted(() => {
	crudExpose.doRefresh();
});
</script>

<style scoped> 
</style>

