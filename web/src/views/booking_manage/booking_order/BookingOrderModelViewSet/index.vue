<!--
 * @Description: 预订订单管理
 * @Version: 1.0
 * @Autor: AI Assistant
 * @Date: 2025-01-XX
 * @LastEditors: 
 * @LastEditTime: 2025-01-XX
-->
<template>
    <fs-page class="PageFeatureSearchMulti">
        <fs-crud ref="crudRef" v-bind="crudBinding">
        </fs-crud>
        
        <!-- 审核对话框 -->
        <el-dialog
            v-model="reviewDialogVisible"
            :title="`预订订单审核 - ${reviewOrderNo}`"
            width="90%"
            :close-on-click-modal="false"
            destroy-on-close
        >
            <booking-order-review-page
                v-if="reviewDialogVisible"
                :order-id="reviewOrderId"
                :order-no="reviewOrderNo"
                @close="reviewDialogVisible = false"
                @refresh="handleReviewRefresh"
            />
        </el-dialog>
    </fs-page>
</template>

<script lang="ts">
import { onMounted, getCurrentInstance, defineComponent, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions  from './crud';
import BookingOrderReviewPage from './components/BookingOrderReviewPage.vue';

export default defineComponent({
    name: "BookingOrderModelViewSet",
    components: {
        BookingOrderReviewPage
    },
    setup() {

		const instance = getCurrentInstance();

		const context: any = {
			componentName: instance?.type.name
		};

		const { crudBinding, crudRef, crudExpose, resetCrudOptions } = useFs({ createCrudOptions, context});
        
        // 审核对话框控制
        const reviewDialogVisible = ref(false);
        const reviewOrderId = ref('');
        const reviewOrderNo = ref('');
        
        // 处理审核后刷新
        const handleReviewRefresh = () => {
            crudExpose.doRefresh();
        };

		// 页面打开后获取列表数据
		onMounted(() => {
			crudExpose.doRefresh();
		});
        
        // 将审核相关的ref暴露给crud.tsx
        (globalThis as any).__reviewDialog = {
            visible: reviewDialogVisible,
            orderId: reviewOrderId,
            orderNo: reviewOrderNo
        };
        
		return {
				crudBinding,
				crudRef,
                reviewDialogVisible,
                reviewOrderId,
                reviewOrderNo,
                handleReviewRefresh
			};
	

    }
  });

</script>

<style scoped>
</style>

<style>
/* 多行错误消息样式 */
.multiline-message {
	white-space: pre-wrap !important;
	word-break: break-word !important;
	max-width: 600px !important;
	text-align: left !important;
	line-height: 1.6 !important;
	padding: 16px !important;
}

.multiline-message .el-message__content {
	white-space: pre-wrap !important;
	word-break: break-word !important;
	text-align: left !important;
	line-height: 1.6 !important;
}
</style>
