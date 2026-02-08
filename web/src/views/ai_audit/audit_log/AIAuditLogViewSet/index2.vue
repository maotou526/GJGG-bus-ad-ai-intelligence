<!--
 * @Description: AI审核记录管理
 * @Version: 1.0
 * @Date: 2026-02-04
-->
<template>
	<fs-page class="PageAIAuditLog">
		<fs-crud ref="crudRef" v-bind="crudBinding">
		</fs-crud>

		<!-- 上传文件抽屉 -->
		<el-drawer
			v-model="uploadDrawerVisible"
			title="上传文件并审核"
			:size="800"
			direction="rtl"
			:close-on-click-modal="false"
			:destroy-on-close="true"
		>
			<UploadForm
				v-if="uploadDrawerVisible"
				@success="handleUploadSuccess"
				@cancel="handleUploadCancel"
			/>
		</el-drawer>
	</fs-page>
</template>

<script lang="ts">
import { onMounted, getCurrentInstance, defineComponent, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { ElMessage } from 'element-plus';
import createCrudOptions from './crud';
import UploadForm from '../uploadFile/UploadForm.vue';

export default defineComponent({
	name: "AIAuditLogViewSet",
	components: {
		UploadForm,
	},
	setup() {
		const instance = getCurrentInstance();

		const context: any = {
			componentName: instance?.type.name
		};

		// 上传抽屉显示状态
		const uploadDrawerVisible = ref(false);

		// 打开上传抽屉
		const openUploadDrawer = () => {
			uploadDrawerVisible.value = true;
		};

		// 上传成功回调
		const handleUploadSuccess = (result: any) => {
			uploadDrawerVisible.value = false;
			ElMessage.success('审核完成！');
			// 刷新列表
			crudExpose.doRefresh();
		};

		// 取消上传
		const handleUploadCancel = () => {
			uploadDrawerVisible.value = false;
		};

		// 将 openUploadDrawer 方法添加到 context，供 crud.tsx 调用
		context.openUploadDrawer = openUploadDrawer;

		const { crudBinding, crudRef, crudExpose, resetCrudOptions } = useFs({ createCrudOptions, context });

		// 页面打开后获取列表数据
		onMounted(() => {
			crudExpose.doRefresh();
		});

		return {
			crudBinding,
			crudRef,
			uploadDrawerVisible,
			handleUploadSuccess,
			handleUploadCancel,
		};
	}
});
</script>

<style scoped>
:deep(.el-drawer__header) {
	margin-bottom: 20px;
	padding-bottom: 20px;
	border-bottom: 1px solid #ebeef5;
}

:deep(.el-drawer__body) {
	padding: 0;
}
</style>
