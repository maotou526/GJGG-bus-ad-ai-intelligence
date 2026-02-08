<template>
	<!-- 全屏背景容器 -->
	<div class="login-container">
		<!-- 背景图片 -->
		<div class="login-background">
			<img v-if="loginBg" :src="loginBg" class="background-image" />
		</div>

		<!-- 登录卡片 -->
		<div class="login-card">

			<!-- 登录表单区域 -->
			<div class="login-form-container">
				<div class="form-title">
					<!-- <img :src="loginTitleIcon" class="title-icon" alt="智擎交通广告云脑平台" /> -->
					<span class="title-text">{{ userInfos.pwd_change_count === 0 ? '初次登录修改密码' : '智擎交通广告云脑平台' }}</span>
				</div>

				<div class="form-content">
					<div v-if="!state.isScan">
						<ChangePwd v-if="userInfos.pwd_change_count === 0" />
						<Account v-else />
					</div>
					<OAuth2 />
				</div>
			</div>
		</div>

	</div>
	<div v-if="loginBg">
		<img :src="loginBg" class="fixed inset-0 w-full h-full loginBg z-1" />
	</div>
</template>

<script setup lang="ts" name="loginIndex">
import { defineAsyncComponent, onMounted, reactive, computed, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { NextLoading } from '/@/utils/loading';
import loginMain from '/@/assets/login-main.svg';
import loginBg from '/@/assets/login-bg-city.png';
import loginTitleIcon from '/@/assets/login-title-icon.png';
import { SystemConfigStore } from '/@/stores/systemConfig'
import { getBaseURL } from "/@/utils/baseUrl";
// 引入组件
const Account = defineAsyncComponent(() => import('/@/views/system/login/component/account.vue'));
const Mobile = defineAsyncComponent(() => import('/@/views/system/login/component/mobile.vue'));
const Scan = defineAsyncComponent(() => import('/@/views/system/login/component/scan.vue'));
const ChangePwd = defineAsyncComponent(() => import('/@/views/system/login/component/changePwd.vue'));
const OAuth2 = defineAsyncComponent(() => import('/@/views/system/login/component/oauth2.vue'));

import { useUserInfo } from "/@/stores/userInfo";
const { userInfos } = storeToRefs(useUserInfo());

// 定义变量内容
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const state = reactive({
	isScan: false,
});


// 获取布局配置信息
const getThemeConfig = computed(() => {
	return themeConfig.value;
});

const systemConfigStore = SystemConfigStore()
const { systemConfig } = storeToRefs(systemConfigStore)
const getSystemConfig = computed(() => {
	return systemConfig.value
})


const siteBg = computed(() => {
	if (getSystemConfig.value['login.login_background']) {
		return getSystemConfig.value['login.login_background']
	}
});

// 页面加载时
onMounted(() => {
	NextLoading.done();
});
</script>

<style scoped lang="scss">
.login-container {
	position: relative;
	height: 100vh;
	width: 100vw;
	overflow: hidden;
	display: flex;
	align-items: center;
	justify-content: flex-end;
	padding-right: 200px;

	// 全屏背景
	.login-background {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 1;
		overflow: hidden;

		.background-image {
			position: absolute;
			top: 0;
			left: 0;
			width: 100%;
			height: 100%;
			object-fit: cover;
			object-position: center;
			image-rendering: auto;
			transform: scale(1.02); // 轻微放大避免边缘空白
		}

		// 为了更好的平铺效果，也可以使用CSS背景图的方式
		&.pattern-mode {
			background-image: url('/@/assets/login-bg-city.png');
			background-repeat: repeat;
			background-size: 800px auto; // 可调节重复大小
			background-position: center;

			.background-image {
				display: none;
			}
		}
	}

	// 登录卡片
	.login-card {
		position: relative;
		z-index: 10;
		width: 511px;
		height: 609px;
		background: rgba(255, 255, 255, 0.9);
		box-shadow: 0px 4px 10px 0px rgba(0, 0, 0, 0.1);
		border-radius: 10px;
		display: flex;
		flex-direction: column;
		overflow: hidden;
		animation: logoAnimation 0.5s ease-out;


		// 登录表单容器
		.login-form-container {
			flex: 1;
			padding: 0px;
			display: flex;
			flex-direction: column;

			.form-title {
				width: 100%;
				height: auto;
				display: flex;
				align-items: center;
				justify-content: flex-start;
				margin-top: 37px;
				margin-bottom: 30px;
				padding-left: 25px;
				padding-right: 20px;

				.title-icon {
					width: 60.65px;
					height: 60.65px;
					margin-right: 7px;
					opacity: 1;
					border-radius: 0;
					flex-shrink: 0;
				}

				.title-text {
					font-family: 'Source Han Sans', 'Source Han Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
					font-weight: 900;
					font-size: 30px;
					color: #000000;
					line-height: 32px;
					letter-spacing: 1px;
					font-style: normal;
					text-transform: none;
					flex: 1;
					min-height: 60px;
					display: flex;
					align-items: center;
				}
			}

			.form-content {
				flex: 1;
			}
		}
	}


	// 响应式适配
	@media (max-width: 768px) {
		padding: 20px;
		justify-content: center;

		.login-card {
			width: 90vw;
			max-width: 400px;
			height: auto;
			min-height: 500px;
		}

	}

	@media (max-width: 1200px) {
		padding-right: 80px;
	}
}
</style>
