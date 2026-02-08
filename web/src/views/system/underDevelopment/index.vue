<template>
	<div class="under-development-container">
		<div class="development-content">
			<div class="development-icon">
				<i class="iconfont icon-kaifa"></i>
			</div>
			<div class="development-title">该功能尚未完成，正在开发中</div>
			<div class="development-subtitle">我们正在努力开发此功能，敬请期待</div>
			<div class="development-progress">
				<el-progress :percentage="75" :show-text="false" stroke-width="8" />
				<div class="progress-text">开发进度：75%</div>
			</div>
			<div class="development-actions">
				<el-button type="primary" @click="goBack">返回上一页</el-button>
				<el-button @click="goHome">回到首页</el-button>
			</div>
		</div>
	</div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
	name: 'UnderDevelopment',
	setup() {
		const router = useRouter();

		const goBack = () => {
			router.go(-1);
		};

		const goHome = () => {
			router.push('/home');
		};

		return {
			goBack,
			goHome,
		};
	},
});
</script>

<style scoped lang="scss">
.under-development-container {
	display: flex;
	justify-content: center;
	align-items: center;
	width: 100%;
	height: 100%;
	min-height: 400px;
	padding: 20px;
	background: var(--el-bg-color-page);
	box-sizing: border-box;
}

.development-content {
	text-align: center;
	width: 100%;
	max-width: 500px;
	padding: 40px;
	background: var(--el-color-white);
	border-radius: 12px;
	box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
	box-sizing: border-box;
}

.development-icon {
	margin-bottom: 24px;
	
	i {
		font-size: 80px;
		color: var(--el-color-primary);
		opacity: 0.8;
	}
}

.development-title {
	font-size: 24px;
	font-weight: 600;
	color: var(--el-text-color-primary);
	margin-bottom: 12px;
}

.development-subtitle {
	font-size: 16px;
	color: var(--el-text-color-regular);
	margin-bottom: 32px;
	line-height: 1.5;
}

.development-progress {
	margin-bottom: 32px;
	
	.progress-text {
		margin-top: 12px;
		font-size: 14px;
		color: var(--el-text-color-secondary);
	}
}

.development-actions {
	display: flex;
	gap: 12px;
	justify-content: center;
	flex-wrap: wrap;
}

@media (max-width: 768px) {
	.under-development-container {
		padding: 16px;
		min-height: 300px;
	}
	
	.development-content {
		padding: 24px;
		width: 100%;
		max-width: none;
	}
	
	.development-title {
		font-size: 20px;
	}
	
	.development-subtitle {
		font-size: 14px;
	}
	
	.development-actions {
		flex-direction: column;
		align-items: center;
		
		.el-button {
			width: 200px;
		}
	}
}

@media (max-width: 480px) {
	.under-development-container {
		padding: 12px;
		min-height: 250px;
	}
	
	.development-content {
		padding: 20px;
	}
	
	.development-icon i {
		font-size: 60px;
	}
	
	.development-title {
		font-size: 18px;
	}
	
	.development-subtitle {
		font-size: 13px;
	}
}
</style>
