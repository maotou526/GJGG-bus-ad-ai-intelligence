<template>
	<el-form ref="formRef" size="large" class="login-content-form" :model="state.ruleForm" :rules="rules" @keyup.enter="loginClick">
		<div class="input-label">账号</div>
		<el-form-item class="login-animation1" prop="username">
			<el-input type="text" :placeholder="$t('message.account.accountPlaceholder1')" v-model="ruleForm.username"
				clearable autocomplete="off">
				<template #prefix>
					<img :src="accountIcon" class="account-icon" alt="账号图标" />
				</template>
			</el-input>
		</el-form-item>
		<div class="input-label">密码</div>
		<el-form-item class="login-animation2" prop="password">
			<el-input :type="isShowPassword ? 'text' : 'password'" :placeholder="$t('message.account.accountPlaceholder2')"
				v-model="ruleForm.password">
				<template #prefix>
					<img :src="passwordIcon" class="password-icon" alt="密码图标" />
				</template>
				<template #suffix>
					<i class="iconfont el-input__icon login-content-password"
						:class="isShowPassword ? 'icon-yincangmima' : 'icon-xianshimima'"
						@click="isShowPassword = !isShowPassword">
					</i>
				</template>
			</el-input>
		</el-form-item>
		<div class="input-label" v-if="isShowCaptcha">验证码</div>
		<el-form-item class="login-animation3" v-if="isShowCaptcha" prop="captcha">
			<div style="display: flex; align-items: center;">
				<el-input type="text" maxlength="4" :placeholder="$t('message.account.accountPlaceholder3')"
					v-model="ruleForm.captcha" clearable autocomplete="off">
				</el-input>
				<el-button class="login-content-captcha">
					<el-image :src="ruleForm.captchaImgBase" @click="refreshCaptcha" />
				</el-button>
			</div>
		</el-form-item>
		<el-form-item class="login-animation4">
			<el-button type="primary" class="login-content-submit" @click="loginClick"
				:loading="loading.signIn">
				<span>立即登录</span>
			</el-button>
		</el-form-item>
	</el-form>
  <!--      申请试用-->
  <div style="text-align: center" v-if="showApply()">
    <el-button class="login-content-apply" link type="primary" plain round @click="applyBtnClick">
      <span>申请试用</span>
    </el-button>
  </div>
</template>

<script lang="ts">
import { toRefs, reactive, defineComponent, computed, onMounted, onUnmounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, FormInstance, FormRules } from 'element-plus';
import { useI18n } from 'vue-i18n';
import Cookies from 'js-cookie';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { initFrontEndControlRoutes } from '/@/router/frontEnd';
import { initBackEndControlRoutes } from '/@/router/backEnd';
import { Session } from '/@/utils/storage';
import { formatAxis } from '/@/utils/formatTime';
import { NextLoading } from '/@/utils/loading';
import * as loginApi from '/@/views/system/login/api';
import { useUserInfo } from '/@/stores/userInfo';
import { DictionaryStore } from '/@/stores/dictionary';
import { SystemConfigStore } from '/@/stores/systemConfig';
import { BtnPermissionStore } from '/@/plugin/permission/store.permission';
import { Md5 } from 'ts-md5';
import { errorMessage } from '/@/utils/message';
import {getBaseURL} from "/@/utils/baseUrl";
import accountIcon from '/@/assets/账号图标.png';
import passwordIcon from '/@/assets/密码图标.png';

export default defineComponent({
	name: 'loginAccount',
	setup() {
		const { t } = useI18n();
		const storesThemeConfig = useThemeConfig();
		const { themeConfig } = storeToRefs(storesThemeConfig);
		const { userInfos } = storeToRefs(useUserInfo());
		const route = useRoute();
		const router = useRouter();
		const state = reactive({
			isShowPassword: false,
			ruleForm: {
				username: '',
				password: '',
				captcha: '',
				captchaKey: '',
				captchaImgBase: '',
			},
			loading: {
				signIn: false,
			},
		});
		const rules = reactive<FormRules>({
			username: [
				{ required: true, message: '请填写账号', trigger: 'blur' },
			],
			password: [
				{
					required: true,
					message: '请填写密码',
					trigger: 'blur',
				},
			],
			captcha: [
				{
					required: true,
					message: '请填写验证码',
					trigger: 'blur',
				},
			],
		})
		const formRef = ref();
		// 时间获取
		const currentTime = computed(() => {
			return formatAxis(new Date());
		});
		// 是否关闭验证码
		const isShowCaptcha = computed(() => {
			return SystemConfigStore().systemConfig['base.captcha_state'];
		});

		const getCaptcha = async () => {
			loginApi.getCaptcha().then((ret: any) => {
				state.ruleForm.captchaImgBase = ret.data.image_base;
				state.ruleForm.captchaKey = ret.data.key;
			});
		};
		const applyBtnClick = async () => {
			window.open(getBaseURL('/api/system/apply_for_trial/'));
		};
    const refreshCaptcha = async () => {
			state.ruleForm.captcha=''
			loginApi.getCaptcha().then((ret: any) => {
				state.ruleForm.captchaImgBase = ret.data.image_base;
				state.ruleForm.captchaKey = ret.data.key;
			});
		};
		const loginClick = async () => {
			if (!formRef.value) return
			await formRef.value.validate((valid: any) => {
				if (valid) {
					loginApi.login({ ...state.ruleForm, password: Md5.hashStr(state.ruleForm.password) }).then((res: any) => {
						if (res.code === 2000) {
              const {data} = res
              Cookies.set('username', res.data.username);
              Session.set('token', res.data.access);
              useUserInfo().setPwdChangeCount(data.pwd_change_count)
              if(data.pwd_change_count==0){
                return router.push('/login');
              }
							if (!themeConfig.value.isRequestRoutes) {
								// 前端控制路由，2、请注意执行顺序
								initFrontEndControlRoutes();
								loginSuccess();
							} else {
								// 模拟后端控制路由，isRequestRoutes 为 true，则开启后端控制路由
								// 添加完动态路由，再进行 router 跳转，否则可能报错 No match found for location with path "/"
								initBackEndControlRoutes();
								// 执行完 initBackEndControlRoutes，再执行 signInSuccess
								loginSuccess();
							}
						}
					}).catch((err: any) => {
						// 登录错误之后，刷新验证码
						refreshCaptcha();
					});
				} else {
					errorMessage("请填写登录信息")
				}
			})

		};



		// 登录成功后的跳转
		const loginSuccess = () => {
			//获取所有字典
			DictionaryStore().getSystemDictionarys();
			// 初始化登录成功时间问候语
			let currentTimeInfo = currentTime.value;
			// 登录成功，跳到转首页
      const pwd_change_count = userInfos.value.pwd_change_count
      if(pwd_change_count>0){
        // 如果是复制粘贴的路径，非首页/登录页，那么登录成功后重定向到对应的路径中
        if (route.query?.redirect) {
        	router.push({
        		path: <string>route.query?.redirect,
        		query: Object.keys(<string>route.query?.params).length > 0 ? JSON.parse(<string>route.query?.params) : '',
        	});
        } else {
        	router.push('/');
        }
        // 登录成功提示
        // 关闭 loading
        state.loading.signIn = true;
        const signInText = t('message.signInText');
        ElMessage.success(`${currentTimeInfo}，${signInText}`);
      }
			// 添加 loading，防止第一次进入界面时出现短暂空白
			NextLoading.start();
		};
		onMounted(() => {
			getCaptcha();
			//获取系统配置
			SystemConfigStore().getSystemConfigs();
		});
    // 是否显示申请试用按钮
    const showApply = () => {
      return window.location.href.indexOf('public') != -1
    }

		return {
			refreshCaptcha,
			loginClick,
			loginSuccess,
			isShowCaptcha,
			state,
			formRef,
			rules,
      applyBtnClick,
      showApply,
			accountIcon,
			passwordIcon,
			...toRefs(state),
		};
	},
});
</script>

<style scoped lang="scss">
.login-content-form {
	margin-top: 20px;
	margin-left: 41px;

	// 输入框标签样式
	.input-label {
		width: 80px;
		height: 32px;
		font-family: Source Han Sans, Source Han Sans;
		font-weight: 400;
		font-size: 20px;
		color: #575757;
		line-height: 32px;
		letter-spacing: 1px;
		text-align: left;
		font-style: normal;
		text-transform: none;
		margin-bottom: 8px;
	}

	// 输入框样式
	:deep(.el-input) {
		width: 430px;
		
		.el-input__wrapper {
			width: 430px;
			height: 55px;
			border-radius: 4px 4px 4px 4px;
			border: 1px solid #AAAAAA;
			padding: 0 !important;
			box-shadow: none !important;
		}
		
		&.el-input--large .el-input__wrapper {
			padding: 0 !important;
		}
		
		.el-input__inner {
			width: 100%;
			height: 32px;
			font-family: Source Han Sans, Source Han Sans;
			font-weight: 400;
			font-size: 20px;
			color: #575757;
			line-height: 32px;
			letter-spacing: 1px;
			text-align: left;
			font-style: normal;
			text-transform: none;
		}
		.el-input__clear{
			margin-right: 22px;
			font-size: 20px;
		}

		.el-input__suffix {
		}
	}
	
	// 错误状态下的输入框样式
	:deep(.el-form-item.is-error .el-input__wrapper) {
		border: 1px solid #F56C6C !important;
		box-shadow: none !important;
	}

	// 验证码输入框特殊样式
	.login-animation3 :deep(.el-input) {
		width: 284px;
		
		.el-input__wrapper {
			width: 284px;
			height: 54px;
			border-radius: 4px 0px 0px 4px;
			border: 1px solid #AAAAAA;
			box-shadow: none !important;
		}
		
		.el-input__inner {
			width: 125px;
			height: 32px;
			font-family: Source Han Sans, Source Han Sans;
			font-weight: 400;
			font-size: 20px;
			line-height: 32px;
			letter-spacing: 1px;
			text-align: left;
			font-style: normal;
			text-transform: none;
			margin-left: 38px;
			padding-right: 15px;
		}
		.el-input__suffix {
			 margin-right: 10px;
		}
	}
	
	// 验证码输入框错误状态
	.login-animation3.is-error :deep(.el-input__wrapper) {
		border: 1px solid #F56C6C !important;
		box-shadow: none !important;
	}

	// 账号图标样式
	.account-icon {
		width: 30px;
		height: 30px;
		margin-left: 11px;
		margin-top: 13px;
		margin-bottom: 12px;
	}

	// 密码图标样式（与账号图标相同）
	.password-icon {
		width: 30px;
		height: 30px;
		margin-left: 11px;
		margin-top: 13px;
		margin-bottom: 12px;
	}

	@for $i from 1 through 4 {
		.login-animation#{$i} {
			opacity: 0;
			animation-name: error-num;
			animation-duration: 0.5s;
			animation-fill-mode: forwards;
			animation-delay: calc($i/10) + s;
		}
	}

	:deep(.login-content-password) {
		display: inline-block !important;
		font-size: 24px !important;
		width: 24px !important;
		height: 14px !important;
		margin-right: 22px !important;
		cursor: pointer;
		vertical-align: middle;
		line-height: 14px !important;

		&:hover {
			color: #909399;
		}
	}
	
	// 更具体的选择器
	:deep(.el-input__suffix .login-content-password) {
		font-size: 24px !important;
		width: 24px !important;
		height: 14px !important;
		margin-right: 22px !important;
	}

	.login-content-captcha {
		width: 142px;
		height: 54px;
		padding: 0;
		border-radius: 0px 0px 0px 0px;
		border: none;
		margin-left: 4px;
		overflow: hidden;
		display: flex;
		align-items: stretch;
		
		:deep(.el-image) {
			width: 100%;
			height: 100%;
			display: flex;
			
			img {
				width: 100%;
				height: 100% !important;
				object-fit: fill;
				display: block;
			}
		}
	}

	.login-content-submit {
		width: 430px;
		height: 55px;
		background: #1677FE;
		border-radius: 4px 4px 4px 4px;
		letter-spacing: 2px;
		font-weight: 800;
		margin-top: 15px;
		border: none;
		
		span {
			width: 91px;
			height: 32px;
			font-family: Source Han Sans, Source Han Sans;
			font-weight: 400;
			font-size: 22px;
			color: #FFFFFF;
			line-height: 32px;
			letter-spacing: 1px;
			text-align: left;
			font-style: normal;
			text-transform: none;
		}
	}
}
</style>
