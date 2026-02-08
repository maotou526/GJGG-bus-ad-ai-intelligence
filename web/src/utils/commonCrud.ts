import { dict, compute } from '@fast-crud/fast-crud';
import { shallowRef } from 'vue';
import deptFormat from '/@/components/dept-format/index.vue';
import tableSelector from '/@/components/tableSelector/index.vue';
import { request } from '/@/utils/service';
import XEUtils from 'xe-utils';

/** 1. 每个字段可选属性 */
export interface CrudFieldOption {
	form?: boolean;
	table?: boolean;
	search?: boolean;
	width?: number;
}

/** 2. 总配置接口 */
export interface CrudOptions {
	create_datetime?: CrudFieldOption;
	update_datetime?: CrudFieldOption;
	creator_name?: CrudFieldOption;
	modifier_name?: CrudFieldOption;
	dept_belong_id?: CrudFieldOption;
	description?: CrudFieldOption;
}

/** 3. 默认完整配置 */
const defaultOptions: Required<CrudOptions> = {
	create_datetime: { form: false, table: false, search: false, width: 160 },
	update_datetime: { form: false, table: false, search: false, width: 160 },
	creator_name: { form: false, table: false, search: false, width: 100 },
	modifier_name: { form: false, table: false, search: false, width: 100 },
	dept_belong_id: { form: false, table: false, search: false, width: 300 },
	description: { form: false, table: false, search: false, width: 100 },
};

/** 4. mergeOptions 函数 */
function mergeOptions(baseOptions: Required<CrudOptions>, userOptions: CrudOptions = {}): Required<CrudOptions> {
	const result = { ...baseOptions };
	for (const key in userOptions) {
		if (Object.prototype.hasOwnProperty.call(userOptions, key)) {
			const baseField = result[key as keyof CrudOptions];
			const userField = userOptions[key as keyof CrudOptions];
			if (baseField && userField) {
				result[key as keyof CrudOptions] = { ...baseField, ...userField };
			}
		}
	}
	return result;
}

/**
 * 最终暴露的 commonCrudConfig
 * @param options 用户自定义配置（可传可不传，不传就用默认）
 */
export const commonCrudConfig = (options: CrudOptions = {}) => {
	// ① 合并
	const merged = mergeOptions(defaultOptions, options);

	// ② 用 merged 中的值生成真正的 CRUD 配置
	return {
		dept_belong_id: {
			title: '所属部门',
			type: 'dict-tree',
			search: {
				show: merged.dept_belong_id.search,
			},
			dict: dict({
				url: '/api/system/dept/all_dept/',
				isTree: true,
				value: 'id',
				label: 'name',
				children: 'children',
			}),
			column: {
				align: 'center',
				width: merged.dept_belong_id.width,
				show: merged.dept_belong_id.table,
				component: {
					// fast-crud里自定义组件常用"component.is"
					is: shallowRef(deptFormat),
					vModel: 'modelValue',
				},
			},
			form: {
				show: merged.dept_belong_id.form,
				component: {
					multiple: false,
					clearable: true,
					props: {
						checkStrictly: true,
						props: {
							label: 'name',
							value: 'id',
						},
					},
				},
				helper: '默认不填则为当前创建用户的部门ID',
			},
		},
		description: {
			title: '备注',
			search: {
				show: merged.description.search,
			},
			type: 'textarea',
			column: {
				width: merged.description.width,
				show: merged.description.table,
			},
			form: {
				show: merged.description.form,
				component: {
					placeholder: '请输入内容',
					showWordLimit: true,
					maxlength: '200',
				},
			},
			viewForm: {
				show: true,
			},
		},

		modifier_name: {
			title: '修改人',
			search: {
				show: merged.modifier_name.search,
			},
			column: {
				width: merged.modifier_name.width,
				show: merged.modifier_name.table,
			},
			form: {
				show: merged.modifier_name.form,
			},
			viewForm: {
				show: true,
			},
		},

		creator_name: {
			title: '创建人',
			search: {
				show: merged.creator_name.search,
			},
			column: {
				width: merged.creator_name.width,
				show: merged.creator_name.table,
			},
			form: {
				show: merged.creator_name.form,
			},
			viewForm: {
				show: true,
			},
		},

		update_datetime: {
			title: '更新时间',
			type: 'datetime',
			search: {
				show: merged.update_datetime.search,
				col: { span: 8 },
				component: {
					type: 'datetimerange',
					props: {
						'start-placeholder': '开始时间',
						'end-placeholder': '结束时间',
						'value-format': 'YYYY-MM-DD HH:mm:ss',
						'picker-options': {
							shortcuts: [
								{
									text: '最近一周',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
										picker.$emit('pick', [start, end]);
									},
								},
								{
									text: '最近一个月',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
										picker.$emit('pick', [start, end]);
									},
								},
								{
									text: '最近三个月',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
										picker.$emit('pick', [start, end]);
									},
								},
							],
						},
					},
				},
				valueResolve(context: any) {
					const { value } = context;
					if (value) {
						context.form.update_datetime_after = value[0];
						context.form.update_datetime_before = value[1];
						delete context.form.update_datetime;
					}
				},
			},
			column: {
				width: merged.update_datetime.width,
				show: merged.update_datetime.table,
			},
			form: {
				show: merged.update_datetime.form,
			},
			viewForm: {
				show: true,
			},
		},

		create_datetime: {
			title: '创建时间',
			type: 'datetime',
			search: {
				show: merged.create_datetime.search,
				col: { span: 8 },
				component: {
					type: 'datetimerange',
					props: {
						'start-placeholder': '开始时间',
						'end-placeholder': '结束时间',
						'value-format': 'YYYY-MM-DD HH:mm:ss',
						'picker-options': {
							shortcuts: [
								{
									text: '最近一周',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
										picker.$emit('pick', [start, end]);
									},
								},
								{
									text: '最近一个月',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
										picker.$emit('pick', [start, end]);
									},
								},
								{
									text: '最近三个月',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
										picker.$emit('pick', [start, end]);
									},
								},
							],
						},
					},
				},
				valueResolve(context: any) {
					const { value } = context;
					if (value) {
						context.form.create_datetime_after = value[0];
						context.form.create_datetime_before = value[1];
						delete context.form.create_datetime;
					}
				},
			},
			column: {
				width: merged.create_datetime.width,
				show: merged.create_datetime.table,
			},
			form: {
				show: merged.create_datetime.form,
			},
			viewForm: {
				show: true,
			},
		},
	};
};

/**
 * 数据源管理器
 * 用于管理从数据库中获取的数据，提供缓存、查找、刷新等功能
 * 所有页面共享同一个缓存，避免重复请求相同的数据源
 */
class DataSourceManager {
	private static cacheMap = new Map<string, any[]>();
	private static loadingMap = new Map<string, boolean>();
	private static timestampMap = new Map<string, number>(); // 缓存时间戳

	/**
	 * 预加载数据源数据
	 * @param key 缓存键（通常是 url）
	 * @param url 数据接口地址
	 * @param params 请求参数（可选）
	 * @param forceRefresh 是否强制刷新（默认 false）
	 */
	static async preload(key: string, url: string, params?: any, forceRefresh: boolean = false) {
		// 如果强制刷新或缓存不存在，则重新加载
		if (forceRefresh || !this.cacheMap.has(key)) {
			if (this.loadingMap.get(key)) {
				return; // 正在加载中，避免重复请求
			}

			this.loadingMap.set(key, true);
			try {
				const res: any = await request({ url, params: { limit: 9999, ...params } });
				this.cacheMap.set(key, res.data || []);
				this.timestampMap.set(key, Date.now());
			} catch (e) {
				console.error(`加载数据源失败 [${key}]:`, e);
			} finally {
				this.loadingMap.set(key, false);
			}
		}
	}

	/**
	 * 从缓存中查找数据标签
	 * @param key 缓存键
	 * @param value 要查找的值
	 * @param valueField 值字段名（默认 'id'）
	 * @param labelField 标签字段名（默认 'name'）
	 * @param isTree 是否为树形结构（默认 false）
	 * @returns 找到的标签值，找不到则返回原值
	 */
	static findLabel(key: string, value: any, valueField: string = 'id', labelField: string = 'name', isTree: boolean = false): string {
		if (!value) return '';

		const data = this.cacheMap.get(key) || [];
		if (data.length === 0) return value; // 缓存未加载时返回原值

		if (isTree) {
			// 树形结构使用 XEUtils.findTree
			const found = XEUtils.findTree(data, (item: any) => item[valueField] == value);
			return found ? found.item[labelField] || value : value;
		} else {
			// 平铺结构直接查找
			const found = data.find((item: any) => item[valueField] == value);
			return found ? found[labelField] || value : value;
		}
	}

	/**
	 * 手动刷新数据源缓存
	 * @param key 缓存键
	 * @param url 数据接口地址
	 * @param params 请求参数（可选）
	 */
	static async refreshCache(key: string, url: string, params?: any) {
		await this.preload(key, url, params, true);
	}

	/**
	 * 获取缓存时间戳（用于判断缓存是否过期）
	 * @param key 缓存键
	 * @returns 时间戳，如果不存在返回 0
	 */
	static getCacheTimestamp(key: string): number {
		return this.timestampMap.get(key) || 0;
	}

	/**
	 * 清除缓存
	 * @param key 缓存键，如果不传则清除所有缓存
	 */
	static clearCache(key?: string) {
		if (key) {
			this.cacheMap.delete(key);
			this.loadingMap.delete(key);
			this.timestampMap.delete(key);
		} else {
			this.cacheMap.clear();
			this.loadingMap.clear();
			this.timestampMap.clear();
		}
	}

	/**
	 * 获取缓存数据
	 * @param key 缓存键
	 * @returns 缓存的数据数组
	 */
	static getData(key: string): any[] {
		return this.cacheMap.get(key) || [];
	}
}

/**
 * 通用的数据源格式化器配置
 * 用于 column.formatter，支持自动缓存和树形查找
 * 从数据库中获取数据源，根据 ID 自动查找对应的显示名称
 *
 * @param options 配置选项
 * @param options.url 数据接口地址（必填）
 * @param options.value 值字段名（默认 'id'）
 * @param options.label 标签字段名（默认 'name'）
 * @param options.isTree 是否为树形结构（默认 false）
 * @param options.params 请求参数（可选）
 * @param options.displayField 后端返回的显示字段（可选，优先级最高）
 * @param options.fallback 找不到时的回退值（默认返回原 value）
 * @param options.autoRefresh 是否自动刷新（默认 false）
 * @param options.refreshInterval 自动刷新间隔（毫秒，默认 5 分钟）
 *
 * @example
 * // 简单使用（平铺结构）
 * company_id: {
 *   title: '公司',
 *   ...getDataSourceFormatterConfig({
 *     url: '/api/CompanyModelViewSet/',
 *     value: 'id',
 *     label: 'shortname'
 *   })
 * }
 *
 * @example
 * // 树形结构
 * parent_id: {
 *   title: '上级',
 *   ...getDataSourceFormatterConfig({
 *     url: '/api/CompanyModelViewSet/',
 *     value: 'id',
 *     label: 'shortname',
 *     isTree: true
 *   })
 * }
 */
export const getDataSourceFormatterConfig = (options: {
	url: string;
	value?: string;
	label?: string;
	isTree?: boolean;
	params?: any;
	displayField?: string; // 后端返回的显示字段名（如 'company_belong_name'）
	fallback?: (value: any) => string; // 自定义回退逻辑
	autoRefresh?: boolean; // 是否自动刷新（默认 false）
	refreshInterval?: number; // 自动刷新间隔（毫秒，默认 5 分钟）
}) => {
	const {
		url,
		value = 'id',
		label = 'name',
		isTree = false,
		params,
		displayField,
		fallback,
		autoRefresh = false,
		refreshInterval = 5 * 60 * 1000, // 默认5分钟
	} = options;

	// 使用 url 作为缓存键
	const cacheKey = url;

	// 预加载数据（异步，不阻塞）
	DataSourceManager.preload(cacheKey, url, params);

	// 如果启用自动刷新，设置定时器
	if (autoRefresh) {
		setInterval(() => {
			DataSourceManager.refreshCache(cacheKey, url, params);
		}, refreshInterval);
	}

	return {
		column: {
			formatter(context: any) {
				const { value: cellValue, row } = context;
				if (!cellValue) return '';

				// 1. 优先使用 row 中的显示字段（如果后端返回了）
				if (displayField && row?.[displayField]) {
					return row[displayField];
				}

				// 2. 从缓存中查找
				const labelValue = DataSourceManager.findLabel(cacheKey, cellValue, value, label, isTree);

				// 3. 如果找不到且有自定义回退逻辑，使用回退
				if (fallback && labelValue === cellValue) {
					return fallback(cellValue);
				}

				return labelValue;
			},
		},
	};
};

/**
 * 手动刷新数据源缓存的工具函数（供外部调用）
 * 例如：在新增/编辑成功后调用此函数刷新缓存
 *
 * @param url 数据接口地址
 * @param params 请求参数（可选）
 *
 * @example
 * // 在 crud.tsx 的 afterSubmit 中
 * form: {
 *   afterSubmit: async ({ form, mode }) => {
 *     if (mode === 'add' || mode === 'edit') {
 *       refreshDataSourceCache('/api/CompanyModelViewSet/');
 *     }
 *   }
 * }
 */
export const refreshDataSourceCache = (url: string, params?: any) => {
	const cacheKey = url;
	DataSourceManager.refreshCache(cacheKey, url, params);
};

/**
 * 通用的公司选择器配置
 * @param options 配置选项
 * @param options.onChange 公司变化时的回调函数（可选），接收 (value, context, crudExpose) 参数
 * @param options.loadMethod 自定义加载方法（可选），默认使用标准加载方法
 * @param options.crudExpose crudExpose 实例（可选），用于在 onChange 中使用
 * @param options.required 是否必填（默认 true）
 * @returns 公司选择器的字段配置对象
 */
export const getCompanySelectorConfig = (
	options: {
		onChange?: (value: any, row: any, context: any, crudExpose?: any) => void | Promise<void>;
		loadMethod?: (tree: any, treeNode: any, resolve: Function) => void;
		crudExpose?: any;
		required?: boolean;
	} = {}
) => {
	const { onChange, loadMethod, crudExpose, required = true } = options;

	// 默认加载方法
	const defaultLoadMethod = (tree: any, treeNode: any, resolve: Function) => {
		request({ url: '/api/CompanyModelViewSet/', params: { parentid: tree.id, limit: 999 } }).then((res: any) => {
			resolve(res.data || []);
		});
	};

	// 使用通用数据源格式化器配置
	const formatterConfig = getDataSourceFormatterConfig({
		url: '/api/CompanyModelViewSet/all_company/',
		value: 'id',
		label: 'shortname',
		isTree: true,
		displayField: 'company_belong_name', // 后端可能返回的字段
	});
	return {
		title: '所属公司',
		type: 'table-selector',
		// ...formatterConfig,
		column: {
			...formatterConfig.column,
			minWidth: 100, // ← 从 100 改为 150
			sortable: 'custom',
		},
		form: {
			rules: required
				? [
						{
							required: true,
							message: '所属公司必填',
						},
				  ]
				: [],
			component: {
				name: shallowRef(tableSelector),
				vModel: 'modelValue',
				displayLabel: compute((context: any) => {
					const value = context.form?.company_belong_id;
					if (!value) return null;

					// 从缓存中查找
					const cacheKey = '/api/CompanyModelViewSet/all_company/';
					const companyName = DataSourceManager.findLabel(
						cacheKey,
						value,
						'id',
						'shortname',
						true // isTree
					);

					// 如果缓存中有数据，返回名称；否则返回 null（让 tableSelector 自己查找）
					return companyName !== value ? companyName : null;
				}),
				tableConfig: {
					url: '/api/CompanyModelViewSet/',
					label: 'shortname',
					value: 'id',
					isTree: true,
					isMultiple: false,
					lazy: true,
					load: loadMethod || defaultLoadMethod,
					treeProps: { children: 'children', hasChildren: 'hasChild' },
					columns: [
						{ prop: 'shortname', label: '名称', width: 200 },
						{ prop: 'encode', label: '编码' },
					],
				},
				// 监听 table-selector 的值变化事件
				...(onChange && {
					// 值变化（仅传值）
					'onUpdate:modelValue': compute((context: any) => {
						return async (value: any) => {
							// 保持向后兼容：只传 value、context、crudExpose
							await onChange(value, context, crudExpose);
						};
					}),
					// 行对象变化（传递选中行）
					'onUpdate:rowValue': compute((context: any) => {
						return async (row: any) => {
							// 兼容更丰富的回调签名：value + row
							const value = context?.form?.company_belong_id;
							// 若业务侧回调只接收3参不会报错，多出的 row 参数会被忽略
							await (onChange as any)(value, row, context, crudExpose);
						};
					}),
				}),
			},
		},
	};
};

/**
 * 线路选择器表格列配置
 */
interface RoadlineTableColumn {
	/** 线路选择器可用字段类型（与后端RoadlineModelSimpleSerializer的fields保持一致） */
	prop: 'id' | 'line_name' | 'company_name' | 'normal_code' | 'ygc_code' | 'exec_day' | 'expiry_day';
	label: string;
	width?: number;
}

/**
 * 通用的线路选择器配置
 * @param options 配置选项
 * @param options.onChange 线路变化时的回调函数（可选），接收 (value, row, context, crudExpose) 参数
 * @param options.crudExpose crudExpose 实例（可选），用于在 onChange 中使用
 * @param options.required 是否必填（默认 true）
 * @param options.fieldName 表单字段名（默认 'roadline_id'）
 * @param options.urlParams 额外的URL参数（可选），可以是对象或函数。如果是函数，接收 (context) 参数，返回参数对象。仅在新增模式下传递参数时，函数中可通过 context.mode === 'add' 判断
 * @param options.title 字段标题（默认 '所属线路'）
 * @param options.requiredMessage 必填验证消息（默认 '所属线路必填'）
 * @param options.columnMinWidth 列表列最小宽度（默认 100）
 * @param options.tableColumns 下拉选择器的表格列配置（默认显示线路名称和线路编码）
 * @returns 线路选择器的字段配置对象
 */
export const getRoadlineSelectorConfig = (
	options: {
		onChange?: (value: any, row: any, context: any, crudExpose?: any) => void | Promise<void>;
		crudExpose?: any;
		required?: boolean;
		fieldName?: string;
		urlParams?: Record<string, any> | ((context: any) => Record<string, any> | undefined);
		title?: string;
		requiredMessage?: string;
		columnMinWidth?: number;
		tableColumns?: RoadlineTableColumn[];
	} = {}
) => {
	const {
		onChange,
		crudExpose,
		required = true,
		fieldName = 'roadline_id',
		urlParams,
		title = '所属线路',
		requiredMessage = '所属线路必填',
		columnMinWidth = 100,
		tableColumns = [
			{ prop: 'line_name', label: '线路名称', width: 200 },
			{ prop: 'normal_code', label: '线路编码' },
		],
	} = options;

	// ==================== 公共配置 ====================
	// 字段映射配置
	const FIELD_CONFIG = {
		value: 'id',
		label: 'line_name',
		displayField: 'roadline_name', // 后端可能返回的显示字段
	} as const;

	// URL配置说明：
	// 1. FORMATTER_URL: 用于列表列的格式化显示（formatter），用于获取全量线路数据
	const FORMATTER_URL = '/api/RoadlineModelViewSet/';

	// 2. SELECTOR_URL: 用于表单中的下拉选择器（table-selector），用于获取过滤后的线路数据，供下拉选择数据的时候使用
	const SELECTOR_BASE_URL = '/api/RoadlineModelViewSet/get_all/?fields=simple';

	// ==================== 列表列配置 ====================
	// 使用通用数据源格式化器配置，用于表格列的ID到名称转换
	const columnConfig = getDataSourceFormatterConfig({
		url: FORMATTER_URL,
		value: FIELD_CONFIG.value,
		label: FIELD_CONFIG.label,
		isTree: false,
		displayField: FIELD_CONFIG.displayField,
	});

	// ==================== 构建table-selector的URL参数 ====================
	const buildSelectorUrl = (context: any): string => {
		const params: Record<string, any> = {};

		// 处理额外的URL参数
		if (urlParams) {
			const extraParams = typeof urlParams === 'function' ? urlParams(context) : urlParams;
			if (extraParams) {
				Object.assign(params, extraParams);
			}
		}

		// 构建查询字符串
		const queryString = Object.keys(params)
			.map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
			.join('&');

		return queryString ? `${SELECTOR_BASE_URL}?${queryString}` : SELECTOR_BASE_URL;
	};

	// ==================== 从缓存中查找线路名称（用于表单显示） ====================
	const getRoadlineNameFromCache = (value: any): string | null => {
		if (!value) return null;

		const roadlineName = DataSourceManager.findLabel(
			FORMATTER_URL,
			value,
			FIELD_CONFIG.value,
			FIELD_CONFIG.label,
			false
		);

		// 直接返回查找结果：如果找到则返回名称，如果没找到则返回原值（ID，这种情况下显示ID也比不显示好）
		return roadlineName;
	};

	// ==================== 返回值配置 ====================
	return {
		title,
		type: 'table-selector',
		// 列表列配置：使用formatter将ID转换为名称显示
		column: {
			...columnConfig.column,
			minWidth: columnMinWidth,
			// sortable: 'custom',
		},
		// 表单配置
		form: {
			rules: required
				? [
						{
							required: true,
							message: requiredMessage,
						},
				  ]
				: [],
			component: {
				name: shallowRef(tableSelector),
				vModel: 'modelValue',
				// 表单显示标签：从缓存中获取线路名称
				displayLabel: compute((context: any) => {
					return getRoadlineNameFromCache(context.form?.[fieldName]);
				}),
				// 下拉选择器配置：使用标准接口，支持动态过滤
				tableConfig: compute((context: any) => ({
					url: buildSelectorUrl(context),
					label: FIELD_CONFIG.label,
					value: FIELD_CONFIG.value,
					isTree: false,
					isMultiple: false,
					columns: tableColumns,
				})),
				// 监听值变化事件
				...(onChange && {
					'onUpdate:modelValue': compute((context: any) => {
						return async (value: any) => {
							await onChange(value, context, crudExpose);
						};
					}),
					'onUpdate:rowValue': compute((context: any) => {
						return async (row: any) => {
							const value = context?.form?.[fieldName];
							await (onChange as any)(value, row, context, crudExpose);
						};
					}),
				}),
			},
		},
	};
};

/**
 * 通用的序号列配置
 * 支持跨页连续编号，自动从 crudExpose 获取分页信息
 *
 * @param crudExpose crudExpose 实例（必填），用于获取分页信息
 * @param options 可选配置
 * @param options.title 列标题（默认 '序号'）
 * @param options.width 列宽度（默认 '50px'）
 * @param options.align 对齐方式（默认 'center'）
 *
 * @example
 * // 在 crud.tsx 中使用
 * export default function ({ crudExpose }: { crudExpose: CrudExpose }) {
 *   return {
 *     crudOptions: {
 *       columns: {
 *         _index: getIndexColumnConfig(crudExpose),
 *         // ... 其他列
 *       }
 *     }
 *   };
 * }
 *
 * @example
 * // 自定义标题和宽度
 * _index: getIndexColumnConfig(crudExpose, {
 *   title: '编号',
 *   width: '80px'
 * })
 */
export const getIndexColumnConfig = (
	crudExpose: any,
	options: {
		title?: string;
		width?: string | number;
		align?: 'left' | 'center' | 'right';
	} = {}
) => {
	const { title = '序号', width = '50px', align = 'center' } = options;

	return {
		title,
		form: { show: false },
		column: {
			align,
			width,
			columnSetDisabled: true, // 禁止在列设置中选择
			formatter: (context: any) => {
				// 直接从 crudExpose 获取分页信息，无需维护外部变量
				// context.index 从 0 开始，需要 +1 让序号从 1 开始
				const index = (context.index ?? 0) + 1;
				const pagination = crudExpose?.crudBinding?.value?.pagination;
				return ((pagination?.currentPage ?? 1) - 1) * (pagination?.pageSize ?? 20) + index;
			},
		},
	};
};
