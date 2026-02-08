<!--
 * @Description: 站级信息列表组件（用于详情弹窗）
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-01-XX
-->
<template>
	<div class="roadline-stop-rel-list">
		<fs-crud ref="crudRef" v-bind="crudBinding"></fs-crud>
	</div>
</template>

<script lang="ts">
import { ref, getCurrentInstance, defineComponent } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './roadlineStopRelCrud';

export default defineComponent({
	name: 'RoadlineStopRelList',
	setup(_, { expose }) {
		const instance = getCurrentInstance();
		const crudRef = ref();

		const roadlineIdRef = ref<number | null>(null);
		const context: any = {
			componentName: instance?.type.name,
			getRoadlineId: () => roadlineIdRef.value,
		};

		const { crudBinding, crudExpose } = useFs({ createCrudOptions, context });

		// 暴露方法供父组件调用
		const refresh = (roadlineId: number) => {
			roadlineIdRef.value = roadlineId;
			if (crudExpose) {
				// 设置搜索条件，过滤当前线路的数据
				crudExpose.setSearchFormData({ roadline_id: roadlineId });
				crudExpose.doRefresh();
			}
		};

		// 暴露给父组件
		expose({
			refresh,
		});

		return {
			crudBinding,
			crudRef,
		};
	},
});
</script>

<style scoped lang="scss">
.roadline-stop-rel-list {
	height: 100%;
}
</style>
