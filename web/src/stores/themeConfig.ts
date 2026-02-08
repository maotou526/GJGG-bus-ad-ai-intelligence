/*
 * @Description: 
 * @Version: 1.0
 * @Autor: 王晨
 * @Date: 2025-10-09 15:13:09
 * @LastEditors: 王晨
 * @LastEditTime: 2026-01-21 09:48:48
 */
import { defineStore } from 'pinia';

/**
 * 布局配置
 * 修复：https://gitee.com/lyt-top/vue-next-admin/issues/I567R1，感谢@lanbao123
 * 2020.05.28 by lyt 优化。开发时配置不生效问题
 * 修改配置时：
 * 1、需要每次都清理 `window.localStorage` 浏览器永久缓存
 * 2、或者点击布局配置最底部 `一键恢复默认` 按钮即可看到效果
 */
export const useThemeConfig = defineStore('themeConfig', {
	state: (): ThemeConfigState => ({
		themeConfig: {
			isDrawer: false,
			primary: '#379fee',
			isIsDark: false,
			topBar: '#01172d',
			topBarColor: '#ffffff',
			isTopBarColorGradual: false,
			menuBar: '#01172d',
			menuBarColor: '#eaeaea',
			menuBarActiveColor: 'rgba(255,255,255,0.1)',
			isMenuBarColorGradual: false,
			columnsMenuBar: '#334054',
			columnsMenuBarColor: '#e6e6e6',
			isColumnsMenuBarColorGradual: false,
			isColumnsMenuHoverPreload: false,
			isCollapse: false,
			isUniqueOpened: true,
			isFixedHeader: false,
			isFixedHeaderChange: true,
			isClassicSplitMenu: false,
			isLockScreen: false,
			lockScreenTime: 30,
			isShowLogo: true,
			isShowLogoChange: false,
			isBreadcrumb: false,
			isTagsview: true,
			isBreadcrumbIcon: true,
			isTagsviewIcon: true,
			isCacheTagsView: true,
			isSortableTagsView: true,
			isShareTagsView: false,
			isFooter: true,
			isGrayscale: false,
			isInvert: false,
			isWartermark: false,
			wartermarkText: '',
			tagsStyle: 'tags-style-five',
			animation: 'slide-right',
			columnsAsideStyle: 'columns-round',
			columnsAsideLayout: 'columns-vertical',
			layout: 'classic',
			isRequestRoutes: true,
			globalTitle: '智擎交通广告云脑平台',
			globalViceTitle: '智擎交通广告云脑平台',
			globalViceTitleMsg: '智擎交通广告云脑平台',
			globalI18n: 'zh-cn',
			globalComponentSize: 'default',
		},
	}),
	actions: {
		setThemeConfig(data: ThemeConfigState) {
			this.themeConfig = data.themeConfig;
		},
	},
});
