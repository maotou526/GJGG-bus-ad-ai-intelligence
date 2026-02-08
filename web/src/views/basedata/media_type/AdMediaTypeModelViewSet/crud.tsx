import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet, CreateCrudOptionsProps, compute } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ElMessageBox, ElMessage, ElLoading } from 'element-plus';
import { ref, h, nextTick } from 'vue';
// @ts-ignore - defConfig.js 没有类型声明
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import ComponentTypeSelector from './components/ComponentTypeSelector.vue';

//此处为crudOptions配置
export default function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	// 子组件组件的 key，用于强制重新渲染
	const componentTypeSelectorKey = ref(0);

	// 获取媒体类型列表（一次性加载全部数据，不分页）
	const pageRequest = async (query: any) => {
		// 保留原有查询条件（search 表单），只覆盖分页相关参数
		const reqParams: any = {
			...query,
			// 兼容后端常用的多种分页参数写法
			limit: 9999,
			pageSize: 9999,
			page: 1,
			offset: 0,
		};
		return await api.GetList(reqParams);
	};

	// 编辑媒体类型
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		// 验证类型名称不能重复（如果名称有变化）
		if (form.media_name && form.media_name !== row.media_name) {
			try {
				const checkResponse = await api.GetList({
					media_name: form.media_name,
					delete_mark: 0,
					limit: 1,
				} as any);
				const existingData = checkResponse.data?.results || checkResponse.data || [];
				if (Array.isArray(existingData) && existingData.length > 0) {
					// 排除当前记录
					const otherRecords = existingData.filter((item: any) => item.id !== form.id);
					if (otherRecords.length > 0) {
						ElMessage.error(`类型名称"${form.media_name}"已存在，不能重复`);
						throw new Error(`类型名称"${form.media_name}"已存在，不能重复`);
					}
				}
			} catch (error: any) {
				// 如果错误信息已经显示，直接抛出
				if (error.message && error.message.includes('已存在')) {
					throw error;
				}
				// 其他错误（如网络错误）不影响提交，让后端验证处理
				console.warn('检查类型名称重复时出错:', error);
			}
		}

		// 处理 spec_config：如果是字符串，尝试解析为 JSON
		if (form.spec_config && typeof form.spec_config === 'string') {
			try {
				form.spec_config = JSON.parse(form.spec_config);
			} catch (e) {
				// 如果解析失败，保持原值或设为 null
				ElMessage.warning('规格参数格式不正确，将保存为空');
				form.spec_config = null;
			}
		}

		// 保存组合关系数据
		const compositions = form.component_types;
		const isComposite = form.is_composite;
		
		// 先保存媒体类型主数据
		const result = await api.UpdateObj(form);
		
		// 如果是组合类型且有选中的基础类型，保存组合关系
		if (isComposite && compositions && Array.isArray(compositions) && compositions.length > 0) {
			try {
				const compositionData = compositions.map((comp: any, index: number) => ({
					component_type_id: comp.id,
					sort_order: comp.sort_order || index + 1,
				}));
				const compositionResult = await api.SaveCompositions(result.data.id || form.id, compositionData);
				console.log('保存组合关系成功:', compositionResult);
			} catch (error: any) {
				console.error('保存组合关系失败:', error);
				ElMessage.error('保存组合关系失败: ' + (error.message || '未知错误'));
				throw error; // 抛出错误，让表单知道保存失败
			}
		}
		
		// 清理临时字段
		delete form.component_types;
		
		// 显示成功提示
		ElMessage.success('编辑成功');
		
		return result;
	};

	// 删除媒体类型
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加媒体类型
	const addRequest = async ({ form }: AddReq) => {
		// 验证类型名称不能重复
		if (form.media_name) {
			try {
				const checkResponse = await api.GetList({
					media_name: form.media_name,
					delete_mark: 0,
					limit: 1,
				} as any);
				const existingData = checkResponse.data?.results || checkResponse.data || [];
				if (Array.isArray(existingData) && existingData.length > 0) {
					ElMessage.error(`类型名称"${form.media_name}"已存在，不能重复`);
					throw new Error(`类型名称"${form.media_name}"已存在，不能重复`);
				}
			} catch (error: any) {
				// 如果错误信息已经显示，直接抛出
				if (error.message && error.message.includes('已存在')) {
					throw error;
				}
				// 其他错误（如网络错误）不影响提交，让后端验证处理
				console.warn('检查类型名称重复时出错:', error);
			}
		}

		// 处理 spec_config：如果是字符串，尝试解析为 JSON
		if (form.spec_config && typeof form.spec_config === 'string') {
			try {
				form.spec_config = JSON.parse(form.spec_config);
			} catch (e) {
				// 如果解析失败，保持原值或设为 null
				ElMessage.warning('规格参数格式不正确，将保存为空');
				form.spec_config = null;
			}
		}

		// 保存组合关系数据
		const compositions = form.component_types;
		const isComposite = form.is_composite;
		
		// 先保存媒体类型主数据
		const result = await api.AddObj(form);
		
		// 如果是组合类型且有选中的基础类型，保存组合关系
		if (isComposite && compositions && Array.isArray(compositions) && compositions.length > 0) {
			try {
				const compositionData = compositions.map((comp: any, index: number) => ({
					component_type_id: comp.id,
					sort_order: comp.sort_order || index + 1,
				}));
				await api.SaveCompositions(result.data.id, compositionData);
			} catch (error: any) {
				console.error('保存组合关系失败:', error);
				ElMessage.warning('保存组合关系失败: ' + (error.message || '未知错误'));
			}
		}
		
		// 清理临时字段
		delete form.component_types;
		
		return result;
	};

	// 导出数据
	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	return {
		crudOptions: {
			...listPageDefSingleLineCfg,
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			form: {
				col: { span: 12 },
				labelWidth: '100px',
			wrapper: {
				is: 'el-dialog',
				width: '1000px', // 增加宽度以容纳左右分栏组件
				closeOnClickModal: false, // 禁用点击空白处关闭弹窗
				async onOpened({ mode, form }: any) {
					console.log('[onOpened] 表单打开', { 
						mode, 
						formId: form.id, 
						is_composite: form.is_composite, 
						is_composite_type: typeof form.is_composite,
						formKeys: Object.keys(form) 
					});
					// 重置标志位，确保新打开对话框时可以加载数据
					form._componentTypesDataLoading = false;
					form._componentTypesDataInitialized = false;
					
					// 判断是否为组合类型（兼容布尔值、字符串、数字）
					const isComposite = form.is_composite === true || form.is_composite === 'true' || form.is_composite === 1 || form.is_composite === '1';
					
					// 编辑或查看模式下，如果是组合类型，加载已有的组合关系
					if ((mode === 'edit' || mode === 'view') && isComposite && form.id) {
						try {
							console.log('[onOpened] 开始加载组合关系, id:', form.id);
							const response = await api.GetCompositions(form.id);
							console.log('[onOpened] ========== 组合关系完整响应 ==========');
							console.log('[onOpened] response:', JSON.stringify(response, null, 2));
							console.log('[onOpened] response.data:', response.data);
							console.log('[onOpened] response.data 类型:', typeof response.data);
							console.log('[onOpened] response.data 是否为数组:', Array.isArray(response.data));
							if (response.data && typeof response.data === 'object') {
								console.log('[onOpened] response.data 的键:', Object.keys(response.data));
								if (response.data.results) {
									console.log('[onOpened] response.data.results:', response.data.results);
									console.log('[onOpened] response.data.results 是否为数组:', Array.isArray(response.data.results));
									if (Array.isArray(response.data.results) && response.data.results.length > 0) {
										console.log('[onOpened] response.data.results[0]:', response.data.results[0]);
										console.log('[onOpened] response.data.results[0] 的键:', Object.keys(response.data.results[0]));
									}
								}
							}
							console.log('[onOpened] =========================================');
							
							let compositions = [];
							if (response.data) {
								if (response.data.results && Array.isArray(response.data.results)) {
									compositions = response.data.results;
									console.log('[onOpened] 使用 response.data.results, 数量:', compositions.length);
								} else if (Array.isArray(response.data)) {
									compositions = response.data;
									console.log('[onOpened] 使用 response.data, 数量:', compositions.length);
								} else {
									console.log('[onOpened] 数据格式不符合预期，response.data:', response.data);
								}
							} else {
								console.log('[onOpened] response.data 为空');
							}
							
							console.log('[onOpened] 解析后的组合关系 compositions:', compositions);
							if (compositions.length > 0) {
								console.log('[onOpened] 第一条组合关系数据:', compositions[0]);
								console.log('[onOpened] 第一条数据的字段:', Object.keys(compositions[0]));
								compositions.forEach((comp: any, index: number) => {
									console.log(`[onOpened] compositions[${index}]:`, {
										component_type_id: comp.component_type_id,
										component_type_name: comp.component_type_name,
										sort_order: comp.sort_order,
										所有字段: Object.keys(comp),
										完整数据: comp
									});
								});
							}
							
							if (compositions.length > 0) {
								// 转换为组件需要的格式
								const componentTypes = compositions.map((comp: any) => ({
									id: String(comp.component_type_id), // 确保 id 是字符串类型
									media_name: comp.component_type_name || '',
									sort_order: comp.sort_order || 0,
								}));
								
								console.log('[onOpened] 转换后的 component_types:', componentTypes);
								
								// 先更新数据
								form.component_types = componentTypes;
								
								// 等待响应式更新
								await nextTick();
								
								// 增加 key 值，强制重新渲染子组件
								componentTypeSelectorKey.value++;
								
								// 再等待一个 tick，确保组件完全渲染
								await nextTick();
								
								console.log('[onOpened] 数据设置完成, form.component_types:', form.component_types);
							} else {
								console.log('[onOpened] 没有组合关系数据');
								form.component_types = [];
								componentTypeSelectorKey.value++;
							}
							// 标记数据已初始化
							form._componentTypesDataInitialized = true;
						} catch (error) {
							console.error('[onOpened] 加载组合关系失败:', error);
							form.component_types = [];
							componentTypeSelectorKey.value++;
							form._componentTypesDataInitialized = true;
						}
					} else {
						// 新增模式或非组合类型，初始化为空数组
						console.log('[onOpened] 新增模式或非组合类型，初始化为空数组', { mode, isComposite, hasId: !!form.id });
						if (!form.component_types) {
							form.component_types = [];
						}
						componentTypeSelectorKey.value++;
						form._componentTypesDataInitialized = true;
					}
				},
			},
			afterSubmit({ mode }: any) {
				// 提交成功后刷新列表
				crudExpose.doRefresh();
			},
			async afterOpen({ mode, form }: any) {
				console.log('[afterOpen] 开始执行', { 
					mode, 
					formId: form.id, 
					is_composite: form.is_composite, 
					is_composite_type: typeof form.is_composite,
					formKeys: Object.keys(form) 
				});
				
				// 判断是否为组合类型（兼容布尔值、字符串、数字）
				const isComposite = form.is_composite === true || form.is_composite === 'true' || form.is_composite === 1 || form.is_composite === '1';
				
				// 编辑或查看模式下，如果是组合类型，加载已有的组合关系
				if ((mode === 'edit' || mode === 'view') && isComposite && form.id) {
					try {
						console.log('[afterOpen] 开始加载组合关系, id:', form.id);
						const response = await api.GetCompositions(form.id);
						console.log('[afterOpen] ========== 组合关系完整响应 ==========');
						console.log('[afterOpen] response:', JSON.stringify(response, null, 2));
						console.log('[afterOpen] response.data:', response.data);
						console.log('[afterOpen] response.data 类型:', typeof response.data);
						console.log('[afterOpen] response.data 是否为数组:', Array.isArray(response.data));
						if (response.data && typeof response.data === 'object') {
							console.log('[afterOpen] response.data 的键:', Object.keys(response.data));
							if (response.data.results) {
								console.log('[afterOpen] response.data.results:', response.data.results);
								console.log('[afterOpen] response.data.results 是否为数组:', Array.isArray(response.data.results));
								if (Array.isArray(response.data.results) && response.data.results.length > 0) {
									console.log('[afterOpen] response.data.results[0]:', response.data.results[0]);
									console.log('[afterOpen] response.data.results[0] 的键:', Object.keys(response.data.results[0]));
								}
							}
						}
						console.log('[afterOpen] =========================================');
						
						let compositions = [];
						if (response.data) {
							if (response.data.results && Array.isArray(response.data.results)) {
								compositions = response.data.results;
								console.log('[afterOpen] 使用 response.data.results, 数量:', compositions.length);
							} else if (Array.isArray(response.data)) {
								compositions = response.data;
								console.log('[afterOpen] 使用 response.data, 数量:', compositions.length);
							} else {
								console.log('[afterOpen] 数据格式不符合预期，response.data:', response.data);
							}
						} else {
							console.log('[afterOpen] response.data 为空');
						}
						
						console.log('[afterOpen] 解析后的组合关系 compositions:', compositions);
						if (compositions.length > 0) {
							console.log('[afterOpen] 第一条组合关系数据:', compositions[0]);
							console.log('[afterOpen] 第一条数据的字段:', Object.keys(compositions[0]));
							compositions.forEach((comp: any, index: number) => {
								console.log(`[afterOpen] compositions[${index}]:`, {
									component_type_id: comp.component_type_id,
									component_type_name: comp.component_type_name,
									sort_order: comp.sort_order,
									所有字段: Object.keys(comp),
									完整数据: comp
								});
							});
						}
						
						if (compositions.length > 0) {
							// 转换为组件需要的格式
							const componentTypes = compositions.map((comp: any) => ({
								id: String(comp.component_type_id), // 确保 id 是字符串类型
								media_name: comp.component_type_name || '',
								sort_order: comp.sort_order || 0,
							}));
							
							console.log('[afterOpen] 转换后的 component_types:', componentTypes);
							
							// 先更新数据
							form.component_types = componentTypes;
							
							// 等待响应式更新
							await nextTick();
							
							// 增加 key 值，强制重新渲染子组件
							componentTypeSelectorKey.value++;
							
							// 再等待一个 tick，确保组件完全渲染
							await nextTick();
							
							console.log('[afterOpen] 数据设置完成, form.component_types:', form.component_types);
						} else {
							console.log('[afterOpen] 没有组合关系数据');
							form.component_types = [];
							componentTypeSelectorKey.value++;
						}
						// 标记数据已初始化
						form._componentTypesDataInitialized = true;
					} catch (error) {
						console.error('[afterOpen] 加载组合关系失败:', error);
						form.component_types = [];
						componentTypeSelectorKey.value++;
						form._componentTypesDataInitialized = true;
					}
				} else {
					// 新增模式或非组合类型，初始化为空数组
					console.log('[afterOpen] 新增模式或非组合类型，初始化为空数组', { mode, isComposite, hasId: !!form.id });
					if (!form.component_types) {
						form.component_types = [];
					}
					componentTypeSelectorKey.value++;
					form._componentTypesDataInitialized = true;
				}
			},
				onChange({ form, key, value }: any) {
					// 当 is_composite 变化时，如果不是组合类型，清空已选的基础类型
					if (key === 'is_composite') {
						const isComposite = value === true || value === 'true' || value === 1;
						if (!isComposite) {
							form.component_types = [];
							// 更新 key 以强制重新渲染组件
							componentTypeSelectorKey.value++;
						} else {
							// 当切换为组合类型时，也更新 key 以确保组件正确渲染
							componentTypeSelectorKey.value++;
						}
					}
				},
			},
			// 前端不展示分页组件，页面一次性展示全部数据
			pagination: { show: false },
			table: {
				rowKey: 'id',
			},
			actionbar: {
				buttons: {
					export: {
						// 注释编号:django-vue3-admin-crud210716:注意这个auth里面的值，最好是使用index.vue文件里面的name值并加上请求动作的单词
						show: auth('AdMediaTypeModelViewSet:Export'),
						text: '导出', //按钮文字
						title: '导出', //鼠标停留显示的信息
						click() {
							return exportRequest(crudExpose.getSearchFormData());
							// return exportRequest(crudExpose!.getSearchFormData())    // 注意这个crudExpose!.getSearchFormData()，一些低版本的环境是需要添加!的
						},
					},
					add: {
						show: auth('AdMediaTypeModelViewSet:Create'),
					},
				},
			},
		rowHandle: {
			//固定右侧
			fixed: 'right',
			width: 200,
			buttons: {
				view: {
					type: 'text',
					order: 1,
					show: auth('AdMediaTypeModelViewSet:Retrieve'),
				},
				edit: {
					type: 'text',
					order: 2,
					show: auth('AdMediaTypeModelViewSet:Update'),
				},
			remove: {
				type: 'text',
				order: 3,
				show: auth('AdMediaTypeModelViewSet:Delete'),
			},
			},
		},
			columns: {
			// 序号列（跨页连续编号）
			_index: getIndexColumnConfig(crudExpose, {
				width: 80,
			}),
			// 类型名称
			media_name: {
				title: '类型名称',
				type: 'input',
				search: { show: true },
				column: {
					minWidth: 150,
					sortable: 'custom',
					align: 'left',
				},
					form: {
						rules: [{ required: true, message: '类型名称必填' }],
						component: {
							placeholder: '请输入类型名称，如：全车身、大三侧、车头、普通灯箱',
							disabled: compute(({ mode }: any) => mode === 'view'),
						},
					},
				},
			// 大类归属
			media_category: {
				title: '大类归属',
				type: 'dict-select',
				search: { show: true },
				dict: dict({
					data: [
						{ value: 1, label: '车身广告' },
						{ value: 2, label: '站点广告' },
					],
				}),
				column: {
					minWidth: 150,
					sortable: 'custom',
					align: 'left',
					show: false, // 隐藏原始字段，使用显示字段
					component: {
						name: 'fs-dict-tag',
					},
				},
					form: {
						rules: [{ required: true, message: '大类归属必填' }],
						component: {
							placeholder: '请选择大类归属',
							disabled: compute(({ mode }: any) => mode === 'view'),
						},
					},
				},
			// 大类归属显示字段
			media_category_display: {
				title: '大类归属',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 150,
					sortable: false,
					align: 'left',
				},
					form: { show: false }, // 表单中不显示
				},
			// 是否组合类型
			is_composite: {
				title: '类型类别',
				type: 'dict-select',
				search: { show: true },
				dict: dict({
					data: [
						{ value: true, label: '组合类型' },
						{ value: false, label: '基础类型' },
					],
				}),
				column: {
					minWidth: 120,
					sortable: 'custom',
					align: 'left',
					show: false, // 隐藏原始字段，使用显示字段
					component: {
						name: 'fs-dict-tag',
					},
				},
					form: {
						rules: [{ required: true, message: '是否组合类型必填' }],
						value: true, // 默认基础类型
						component: {
							placeholder: '请选择是否组合类型',
							disabled: compute(({ mode }: any) => mode === 'view'),
						},
					},
				},
			// 是否组合类型显示字段
			is_composite_display: {
				title: '类型',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 100,
					sortable: false,
					align: 'left',
				},
					form: { show: false }, // 表单中不显示
				},
			// 规格参数
			spec_config: {
				title: '规格参数',
				type: 'textarea',
				search: { show: false },
				column: {
					minWidth: 200,
					sortable: false,
					align: 'left',
					show: false, // 默认隐藏，JSON格式数据
					formatter: (context: any) => {
						const value = context.value;
						if (!value) return '-';
						try {
							return JSON.stringify(value, null, 2);
						} catch {
							return value;
						}
					},
				},
					// 新增/编辑表单中不展示规格参数字段
					form: {
						show: false,
					},
				},
			// 制作要求
			fabrication_req: {
				title: '制作要求',
				type: 'textarea',
				search: { show: false },
				column: {
					minWidth: 200,
					sortable: false,
					align: 'left',
					show: false, // 默认隐藏
					formatter: (context: any) => {
						const value = context.value;
						if (!value) return '-';
						// 只显示前50个字符
						return value.length > 50 ? value.substring(0, 50) + '...' : value;
					},
				},
					// 新增/编辑表单中不展示制作要求字段
					form: {
						show: false,
					},
				},
			// 刊例价基准
			// base_price: {
			// 	title: '刊例价基准',
			// 	type: 'number',
			// 	search: { show: false },
			// 	column: {
			// 		minWidth: 120,
			// 		sortable: 'custom',
			// 		align: 'right',
			// 		formatter: (context: any) => {
			// 			const value = context.value;
			// 			if (value === null || value === undefined) return '-';
			// 			return '¥' + parseFloat(value).toFixed(2);
			// 		},
			// 	},
			// 		// 新增/编辑表单中不展示刊例价基准字段
			// 		form: {
			// 			show: false,
			// 		},
			// 	},
			// // 显示顺序
			// sort_order: {
			// 	title: '显示顺序',
			// 	type: 'number',
			// 	search: { show: false },
			// 	column: {
			// 		minWidth: 100,
			// 		sortable: 'custom',
			// 		align: 'right',
			// 	},
			// 		// 新增/编辑表单中不展示显示顺序字段
			// 		form: {
			// 			show: false,
			// 		},
			// 	},
		// 启用状态
		enabled_mark: {
			title: '启用状态',
			type: 'dict-select',
			search: { show: false }, // 隐藏搜索
			dict: dict({
				data: [
					{ value: 1, label: '启用', color: 'success' },
					{ value: 0, label: '禁用', color: 'danger' },
				],
			}),
			column: {
				minWidth: 100,
				sortable: 'custom',
				align: 'left',
				show: false,  // 隐藏列
				component: {
					name: 'fs-dict-tag',
				},
			},
			form: {
				value: 1, // 默认启用
				component: {
					placeholder: '请选择启用状态',
					disabled: compute(({ mode }: any) => mode === 'view'),
				},
			},
		},
			// 描述
			description: {
				title: '描述',
				type: 'textarea',
				search: { show: false },
				column: {
					minWidth: 200,
					sortable: false,
					align: 'left',
					show: false, // 默认隐藏
					formatter: (context: any) => {
						const value = context.value;
						if (!value) return '-';
						// 只显示前30个字符
						return value.length > 30 ? value.substring(0, 30) + '...' : value;
					},
				},
					form: {
						col: { span: 24 }, // 占满整行
						component: {
							placeholder: '请输入描述信息',
							rows: 3,
							disabled: compute(({ mode }: any) => mode === 'view'),
						},
					},
				},
			// 基础类型选择（仅组合类型显示）
			component_types: {
				title: '基础类型选择',
				type: 'component',
				search: { show: false },
				column: { show: false },
				form: {
					col: { span: 24 }, // 占满整行
					show: compute(({ form }: any) => {
						// 仅在类型类别为组合类型时显示
						// 处理布尔值和字符串值的情况
						const isComposite = form.is_composite;
						return isComposite === true || isComposite === 'true' || isComposite === 1;
					}),
					component: {
						render: ({ form, mode }: any) => {
							// 确保 component_types 是数组
							const componentTypes = Array.isArray(form.component_types) 
								? form.component_types 
								: [];
							
							console.log('[render] 渲染 ComponentTypeSelector', {
								formId: form.id,
								componentTypesLength: componentTypes.length,
								componentTypes: componentTypes,
								key: componentTypeSelectorKey.value,
								mode: mode,
							});
							
							// 使用 componentTypeSelectorKey 确保数据更新时强制重新渲染
							return h(ComponentTypeSelector, {
								modelValue: componentTypes,
								mediaCategory: form.media_category,
								disabled: mode === 'view',
								key: `component-type-selector-${form.id || 'new'}-${componentTypeSelectorKey.value}-${componentTypes.length}`,
								'onUpdate:modelValue': (value: any) => {
									if (mode !== 'view') {
										console.log('[render] onUpdate:modelValue', value);
										form.component_types = value;
									}
								},
							});
						},
					},
					value: [], // 默认值
				},
			},
		// 创建人
		creator_name: {
			title: '创建人',
			type: 'text',
			search: { show: false },
			column: {
				minWidth: 120,
				sortable: false,
				align: 'left',
				show: false,  // 隐藏列
			},
				form: {
					show: false,
				},
			},
			// 修改人
			modifier_name: {
				title: '修改人',
				type: 'text',
				search: { show: false },
				column: {
					minWidth: 120,
					sortable: false,
					align: 'left',
					show: false, // 默认隐藏
				},
					form: {
						show: false,
					},
				},
		// 创建时间
		create_datetime: {
			title: '创建时间',
			type: 'datetime',
			search: { show: false },
			column: {
				align: 'left',
				width: 160,
				sortable: 'custom',
				show: false, // 隐藏列
				component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
			},
					form: {
						show: false,
					},
				},
			// 更新时间
			update_datetime: {
				title: '更新时间',
				type: 'datetime',
				search: { show: false },
				column: {
					align: 'left',
					width: 160,
					sortable: 'custom',
					show: false, // 默认隐藏
					component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
				},
					form: {
						show: false,
					},
				},
			},
		},
	};
}

