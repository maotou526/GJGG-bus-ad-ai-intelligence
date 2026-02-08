<!--
 * @Description: AI审核反馈管理
 * @Version: 1.0
 * @Date: 2026-02-04
-->
<template>
	<fs-page class="PageAIAuditFeedback">
		<fs-crud ref="crudRef" v-bind="crudBinding">
		</fs-crud>
	</fs-page>
</template>

<script lang="ts">
import { onMounted, getCurrentInstance, defineComponent } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';

export default defineComponent({
	name: "AIAuditFeedbackViewSet",
	setup() {
		const instance = getCurrentInstance();

		const context: any = {
			componentName: instance?.type.name
		};

		const { crudBinding, crudRef, crudExpose, resetCrudOptions } = useFs({ createCrudOptions, context });

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
