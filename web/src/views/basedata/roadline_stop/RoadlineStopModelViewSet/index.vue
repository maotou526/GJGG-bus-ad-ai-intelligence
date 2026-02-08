<!--
 * @Description: 站点管理页面
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
                <importExcel api="api/RoadlineStopModelViewSet/" v-auth="'RoadlineStopModelViewSet:Import'">导入</importExcel>
            </template>

        </fs-crud>
    </fs-page>
</template>

<script lang="ts">
import { onMounted, getCurrentInstance, defineComponent} from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions  from './crud';
import { autoFillData, convertCoordinates } from './api';
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';

// 导入组件
import importExcel from '/@/components/importExcel/index.vue'   


export default defineComponent({    //这里配置defineComponent
    name: "RoadlineStopModelViewSet",   //把name放在这里进行配置了
	components: {importExcel},  //注册组件
    setup() {   //这里配置了setup()

		const instance = getCurrentInstance();

		const context: any = {
			componentName: instance?.type.name
		};

		const { crudBinding, crudRef, crudExpose, resetCrudOptions } = useFs({ createCrudOptions, context});

	// 自动填充站点数据
	const onAutoFillData = async () => {
		try {
			// 询问用户确认
			await ElMessageBox.confirm(
				'<div style="line-height: 1.8;">' +
				'<p style="margin-bottom: 10px;"><strong>功能说明：</strong></p>' +
				'<p style="margin-bottom: 8px;">通过<strong style="color: #409EFF;">高德地图逆地理编码API</strong>，根据站点经纬度获取：</p>' +
				'<ul style="margin-left: 20px; margin-bottom: 10px;">' +
				'<li>环域、区属、街道</li>' +
				'<li>道路名称、站点地址</li>' +
				'</ul>' +
				'<p style="color: #E6A23C;">⏱ 处理时间可能较长，请耐心等待</p>' +
				'</div>',
				'自动填充站点数据',
				{
					confirmButtonText: '开始填充',
					cancelButtonText: '取消',
					type: 'warning',
					dangerouslyUseHTMLString: true,
				}
			);

				// 显示加载提示
				const loading = ElMessage({
					message: '正在调用高德API填充站点数据，请稍候...',
					type: 'info',
					duration: 0, // 不自动关闭
					showClose: false,
				});

				try {
					// 调用API
					const response: any = await autoFillData({
						batch_size: 100,
						delay: 0.2,
						force_update: false, // 默认不强制更新已有数据
					});

					// 关闭加载提示
					loading.close();

					if (response.code === 2000) {
						const data = response.data;

						// 显示详细结果通知
						ElNotification({
							title: '自动填充完成',
							message: `
								<div style="line-height: 1.8;">
									<p><strong>处理结果：</strong></p>
									<p>✅ 成功：${data.success_count} 个站点</p>
									<p>❌ 失败：${data.failed_count} 个站点</p>
									<p>⏭️ 跳过：${data.skipped_count} 个站点（无经纬度或已有数据）</p>
									<p>📊 总计：${data.total_stops} 个站点</p>
									<p>🔄 API调用：${data.api_call_count} 次</p>
									${data.retry_count > 0 ? `<p>🔁 重试：${data.retry_count} 个（成功 ${data.retry_success_count}）</p>` : ''}
								</div>
							`,
							type: 'success',
							duration: 8000,
							dangerouslyUseHTMLString: true,
						});

						// 如果有失败项，显示警告
						if (data.failed_count > 0 && data.failed_items && data.failed_items.length > 0) {
							const failedList = data.failed_items
								.slice(0, 5)
								.map((item: any) => `${item.stop_name}: ${item.reason}`)
								.join('<br>');

							ElNotification({
								title: '部分站点填充失败',
								message: `<div style="line-height: 1.6;">${failedList}${data.failed_items.length > 5 ? '<br>...' : ''}</div>`,
								type: 'warning',
								duration: 6000,
								dangerouslyUseHTMLString: true,
							});
						}

						// 刷新列表
						await crudExpose.doRefresh();
					} else {
						ElMessage.error(response.msg || '操作失败');
					}
				} catch (error: any) {
					loading.close();
					console.error('自动填充区属失败:', error);
					ElMessage.error(error.message || '操作失败，请稍后重试');
				}
			} catch {
				// 用户取消操作
				console.log('用户取消操作');
			}
		};

		// 坐标转换：GCJ-02 → WGS84
		const onConvertCoordinates = async () => {
			try {
				// 询问用户确认
				await ElMessageBox.confirm(
					'<div style="line-height: 1.8;">' +
					'<p style="margin-bottom: 10px;"><strong>功能说明：</strong></p>' +
					'<p style="margin-bottom: 8px;">将站点坐标从<strong style="color: #409EFF;">GCJ-02（高德坐标系）</strong>转换为<strong style="color: #67C23A;">WGS84（国际标准坐标系）</strong>：</p>' +
					'<ul style="margin-left: 20px; margin-bottom: 10px;">' +
					'<li>读取 lon02 和 lat02 字段（GCJ-02坐标）</li>' +
					'<li>转换为 WGS84 坐标系</li>' +
					'<li>保存到 lon84 和 lat84 字段</li>' +
					'</ul>' +
					'<p style="color: #E6A23C;">⏱ 处理时间可能较长，请耐心等待</p>' +
					'</div>',
					'坐标系转换',
					{
						confirmButtonText: '开始转换',
						cancelButtonText: '取消',
						type: 'warning',
						dangerouslyUseHTMLString: true,
					}
				);

					// 显示加载提示
					const loading = ElMessage({
						message: '正在转换坐标系统，请稍候...',
						type: 'info',
						duration: 0, // 不自动关闭
						showClose: false,
					});

					try {
						// 调用API
						const response: any = await convertCoordinates({
							batch_size: 100,
							delay: 0.1,
							force_update: false, // 默认不强制更新已有数据
						});

						// 关闭加载提示
						loading.close();

						if (response.code === 2000) {
							const data = response.data;

							// 显示详细结果通知
							ElNotification({
								title: '坐标转换完成',
								message: `
									<div style="line-height: 1.8;">
										<p><strong>处理结果：</strong></p>
										<p>✅ 成功：${data.success_count} 个站点</p>
										<p>❌ 失败：${data.failed_count} 个站点</p>
										<p>⏭️ 跳过：${data.skipped_count} 个站点（无GCJ-02坐标或已有WGS84坐标）</p>
										<p>📊 总计：${data.total_stops} 个站点</p>
										<p>🔄 转换方式：GCJ-02 → WGS84（迭代法精确转换）</p>
									</div>
								`,
								type: 'success',
								duration: 8000,
								dangerouslyUseHTMLString: true,
							});

							// 如果有失败项，显示警告
							if (data.failed_count > 0 && data.failed_items && data.failed_items.length > 0) {
								const failedList = data.failed_items
									.slice(0, 5)
									.map((item: any) => `${item.stop_name}: ${item.reason}`)
									.join('<br>');

								ElNotification({
									title: '部分站点转换失败',
									message: `<div style="line-height: 1.6;">${failedList}${data.failed_items.length > 5 ? '<br>...' : ''}</div>`,
									type: 'warning',
									duration: 6000,
									dangerouslyUseHTMLString: true,
								});
							}

							// 刷新列表
							await crudExpose.doRefresh();
						} else {
							ElMessage.error(response.msg || '操作失败');
						}
					} catch (error: any) {
						loading.close();
						console.error('坐标转换失败:', error);
						ElMessage.error(error.message || '操作失败，请稍后重试');
					}
				} catch {
					// 用户取消操作
					console.log('用户取消操作');
				}
			};

		// 将自定义方法暴露给 crud
		crudExpose.onAutoFillData = onAutoFillData;
		crudExpose.onConvertCoordinates = onConvertCoordinates;

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

