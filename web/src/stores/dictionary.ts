import { defineStore } from 'pinia';
import { DictionaryStates } from './interface';
import { request } from '../utils/service';

export const urlPrefix = '/api/init/dictionary/';
export const BUTTON_VALUE_TO_COLOR_MAPPING: any = {
	1: 'success',
	true: 'success',
	0: 'danger',
	false: 'danger',
	Search: 'warning', // 查询
	Update: 'primary', // 编辑
	Create: 'success', // 新增
	Retrieve: 'info', // 单例
	Delete: 'danger', // 删除
};

export function getButtonSettings(objectSettings: any) {
	return objectSettings.map((item: any) => ({
		label: item.label,
		value: item.value,
		color: item.color || BUTTON_VALUE_TO_COLOR_MAPPING[item.value],
	}));
}

/**
 * 字典管理数据
 * @methods getSystemDictionarys 获取系统字典数据
 */
export const DictionaryStore = defineStore('Dictionary', {
	state: (): DictionaryStates => ({
		data: {},
	}),
	actions: {
		async getSystemDictionarys() {
			request({
				url: '/api/init/dictionary/?dictionary_key=all',
				method: 'get',
			}).then((ret: { data: [] }) => {
				// 转换数据格式并保存到pinia
				let dataList = ret.data;
				dataList.forEach((item: any) => {
					let childrens = item.children;
					// console.log(item);
					// this.data[item.value] = childrens;
					childrens.forEach((children:any, index:any) => {
						switch (children.type) {
							case 1:
								// type=1 明确为数字类型
								children.value = Number(children.value)
								break
							case 6:
								// type=6 为布尔类型
								children.value = children.value === 'true'
								break
							default:
								// 其他类型：如果value是纯数字字符串，自动转为数字
								// 这样可以兼容后端字典type配置错误的情况
								if (typeof children.value === 'string' && /^\d+$/.test(children.value)) {
									children.value = Number(children.value)
								}
								break
						}
					})
				this.data[item.value]=childrens
				});
			});
		},
	},
	persist: {
		enabled: true,
	},
});
