<!--
 * @Description:
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-10 11:19:38
 * @LastEditors: 王晨
 * @LastEditTime: 2025-11-03 16:01:13
-->
<template>
	<fs-page class="PageFeatureSearchMulti">
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #cell_url="scope">
				<el-tag size="small">{{ scope.row.url }}</el-tag>
			</template>
			<!-- 线路名称列自定义显示，添加点击事件 -->
			<template #cell_line_name="scope">
				<el-link type="primary" :underline="false" @click="openDetailDialog(scope.row)" style="cursor: pointer;">
					{{ scope.row.line_name }}
				</el-link>
			</template>
			<!-- 注释编号: django-vue3-admin-index442216: -->
			<!-- 注释编号:django-vue3-admin-index39263917:代码开始行-->
			<!--  功能说明:使用导入组件，并且修改api地址为当前对应的api，当前是demo的api="api/CrudDemoModelViewSet/"-->
			<template #actionbar-right>
				<importExcel api="api/RoadlineModelViewSet/" v-auth="'user:Import'">导入</importExcel>
			</template>
			<!--  注释编号:django-vue3-admin-index263917:代码结束行-->
			<template #form>
				<el-form-item label="用户名（自定义）" prop="username"   class="custom-username-item">
					<!-- 自定义组件：如带图标的输入框 -->

					<el-text type="info" class="block mt-1">提示：用户名仅支持字母、数字、下划线</el-text>
				</el-form-item>
			</template>
		</fs-crud>

		<!-- 表单预览弹窗 -->
		<el-dialog
			v-model="formDialogVisible"
			:title="formDialogTitle"
			width="800px"
			destroy-on-close
			:close-on-click-modal="false"
		>
			<div v-if="formDialogLoading" class="dialog-loading">
				<el-icon class="is-loading"><Loading /></el-icon>
				<span>加载中...</span>
			</div>
			<RoadlineForm
				v-else
				ref="roadlineFormRef"
				:readonly="true"
				:data="formDialogData"
			/>
		</el-dialog>

		<!-- 详情弹窗 -->
		<el-dialog
			v-model="detailDialogVisible"
			:title="detailDialogTitle"
			width="90%"
			destroy-on-close
			:close-on-click-modal="false"
			top="5vh"
		>
			<el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
				<el-tab-pane label="线路走向信息" name="detail">
					<div style="height: 60vh; overflow: auto">
						<RoadlineDetailList ref="roadlineDetailListRef" />
					</div>
				</el-tab-pane>
				<el-tab-pane label="站级信息" name="stopRel">
					<div style="height: 60vh; overflow: auto">
						<RoadlineStopRelList ref="roadlineStopRelListRef" />
					</div>
				</el-tab-pane>
			</el-tabs>
		</el-dialog>
	</fs-page>
</template>

<script lang="ts">
import { ref, onMounted, getCurrentInstance, defineComponent, provide } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';

// 注释编号: django-vue3-admin-index192316:导入组件
import importExcel from '/@/components/importExcel/index.vue';
import { handleColumnPermission } from '/@/utils/columnPermission';
import { GetPermission, GetObj } from './api';
import RoadlineForm from '../RoadlineForm/index.vue';
import RoadlineDetailList from './components/RoadlineDetailList.vue';
import RoadlineStopRelList from './components/RoadlineStopRelList.vue';
import { ElMessage } from 'element-plus';
import { Loading } from '@element-plus/icons-vue';

export default defineComponent({
	//这里配置defineComponent
	name: 'RoadlineModelViewSet', //把name放在这里进行配置了
	components: { importExcel, RoadlineForm, Loading, RoadlineDetailList, RoadlineStopRelList }, //注释编号: django-vue3-admin-index552416: 注册组件，把importExcel组件放在这里，这样<template></template>中才能正确的引用到组件
	setup() {
		//这里配置了setup()

		const instance = getCurrentInstance();

		// 表单预览弹窗状态
		const formDialogVisible = ref(false);
		const formDialogTitle = ref('表单预览');
		const formDialogData = ref<any>({});
		const formDialogLoading = ref(false);
		const roadlineFormRef = ref();

		// 详情弹窗状态
		const detailDialogVisible = ref(false);
		const detailDialogTitle = ref('线路详情');
		const activeTab = ref('detail');
		const roadlineDetailListRef = ref();
		const roadlineStopRelListRef = ref();
		const currentRoadlineId = ref<number | null>(null); // 保存当前选中的线路ID

		// 打开表单预览弹窗的方法
		const openFormDialog = async (id: string | number) => {
			if (!id) {
				ElMessage.warning('缺少数据ID');
				return;
			}

			formDialogLoading.value = true;
			formDialogVisible.value = true;
			formDialogTitle.value = '表单预览';
			formDialogData.value = {};

			try {
				const res: any = await GetObj(id as any);
				if (res.code === 2000 && res.data) {
					formDialogData.value = res.data;
					formDialogTitle.value = `线路表单 - ${res.data.line_name || ''}`;
				} else {
					ElMessage.error(res.msg || '获取数据失败');
					formDialogVisible.value = false;
				}
			} catch (e: any) {
				ElMessage.error(e.message || '获取数据失败');
				formDialogVisible.value = false;
			} finally {
				formDialogLoading.value = false;
			}
		};

		// 打开详情弹窗的方法
		const openDetailDialog = (row: any) => {
			if (!row || !row.id) {
				ElMessage.warning('缺少线路信息');
				return;
			}

			currentRoadlineId.value = row.id;
			detailDialogVisible.value = true;
			detailDialogTitle.value = `线路详情 - ${row.line_name || ''}`;
			activeTab.value = 'detail';

			// 等待 DOM 更新后刷新列表数据
			setTimeout(() => {
				if (roadlineDetailListRef.value && currentRoadlineId.value) {
					roadlineDetailListRef.value.refresh(currentRoadlineId.value);
				}
				if (roadlineStopRelListRef.value && currentRoadlineId.value) {
					roadlineStopRelListRef.value.refresh(currentRoadlineId.value);
				}
			}, 100);
		};

		// 标签页切换处理
		const handleTabChange = (tabName: string) => {
			if (!currentRoadlineId.value) return;

			// 切换标签页时刷新对应列表的数据
			setTimeout(() => {
				if (tabName === 'detail' && roadlineDetailListRef.value) {
					roadlineDetailListRef.value.refresh(currentRoadlineId.value);
				} else if (tabName === 'stopRel' && roadlineStopRelListRef.value) {
					roadlineStopRelListRef.value.refresh(currentRoadlineId.value);
				}
			}, 50);
		};

		const context: any = {
			componentName: instance?.type.name,
			openFormDialog, // 将方法传递给 crud
			openDetailDialog, // 将详情弹窗方法传递给 crud
		};

		const { crudBinding, crudRef, crudExpose, crudOptions, resetCrudOptions } = useFs({ createCrudOptions, context });

		// 页面打开后获取列表数据
		onMounted(async () => {
			// 设置列权限
			const newOptions = await handleColumnPermission(GetPermission, crudOptions);
			//重置crudBinding
			resetCrudOptions(newOptions);
			crudExpose.doRefresh();
		});
		return {
			//增加了return把需要给上面<template>内调用的<fs-crud ref="crudRef" v-bind="crudBinding">
			crudBinding,
			crudRef,
			formDialogVisible,
			formDialogTitle,
			formDialogData,
			formDialogLoading,
			roadlineFormRef,
			detailDialogVisible,
			detailDialogTitle,
			activeTab,
			roadlineDetailListRef,
			roadlineStopRelListRef,
			handleTabChange,
			openDetailDialog,
		};
	}, //这里关闭setup()
}); //关闭defineComponent
</script>

<style scoped lang="scss">
.dialog-loading {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 60px 20px;
	color: #909399;

	.el-icon {
		font-size: 32px;
		margin-bottom: 10px;
	}
}

/* 页面特定样式（如需要） */
// 搜索区域按钮组样式
// :deep(.fs-search-layout-default .fs-search-buttons-group) {
// 	// 在这里添加你需要的样式
// 	// 例如：
// 	// justify-content: flex-end; // 按钮靠右对齐
// 	// gap: 10px; // 按钮间距
// 	// margin-top: 10px; // 上边距
// 	align-items: end;
// }

// .PageFeatureSearchMulti {
// 	.fs-search-multi-line-buttons {
// 		position: absolute;
// 		bottom: -38px;
// 		right: 226px;
// 	}
// }
</style>
