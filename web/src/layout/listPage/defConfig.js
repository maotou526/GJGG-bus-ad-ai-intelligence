import ListPage from '/@/layout/listPage/index.vue';
import { shallowRef } from 'vue';

let listPageDefSingleLineCfg = {
	container: {
		is: shallowRef(ListPage), //可以将自定义布局组件全局注册，这里只需要配置name即可
		// is: 'fs-layout-card', //可以将自定义布局组件全局注册，这里只需要配置name即可
	},
	// 搜索配置
	search: {
		container: {
			// layout: 'multi-line',
			layout: 'single-line',
		},
		col: {
			span: 4,
		},
		options: {
			labelWidth: '100px',
			labelPosition: 'top', // label 在上面，输入框在下面
		},
	},
};

let listPageDefMultiLineCfg = {
	container: {
		is: shallowRef(ListPage), //可以将自定义布局组件全局注册，这里只需要配置name即可
		// is: 'fs-layout-card', //可以将自定义布局组件全局注册，这里只需要配置name即可
	},
	// 搜索配置
	search: {
		container: {
			layout: 'multi-line',
		},
		col: {
			span: 4,
		},
		options: {
			labelWidth: '100px',
			labelPosition: 'top', // label 在上面，输入框在下面
		},
	},
};
export { listPageDefSingleLineCfg, listPageDefMultiLineCfg };
