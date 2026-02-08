import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, UserPageQuery, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import * as api from './api';
import { request } from '/@/utils/service';
import { auth } from '/@/utils/authFunction';
import { ref, Ref, watch, shallowRef, h, nextTick, computed } from 'vue';
// @ts-ignore - defConfig.js 没有类型声明
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';
import { getIndexColumnConfig } from '/@/utils/commonCrud';
import BookingOrderDetailTable from './components/BookingOrderDetailTable.vue';
import * as detailApi from '../../booking_order_detail/BookingOrderDetailModelViewSet/api';
import { ElMessage, ElMessageBox } from 'element-plus';
import { CreateFlow } from '/@/views/plugins/bs-workflow/api/process'; // Import CreateFlow
import { useUserInfo } from '/@/stores/userInfo';

// 客户API前缀
const customerApiPrefix = '/api/CustomerModelViewSet/';
// 预订订单API前缀
const bookingOrderApiPrefix = '/api/BookingOrderModelViewSet/';

//此处为crudOptions配置
export default function ({ crudExpose, context }: { crudExpose: CrudExpose; context?: any }): CreateCrudOptionsRet {
	const userStore = useUserInfo();
	// 客户列表
	const customerList: Ref<any[]> = ref([]);

	// 预订订单列表（用于原预订单选择）
	const bookingOrderList: Ref<any[]> = ref([]);

	// 子表组件的 key，用于强制重新渲染
	const detailTableKey = ref(0);


	// 加载客户列表（从 dwd_customer 表）
	const loadCustomerList = async () => {
		try {
			const res = await request({
				url: customerApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			// 兼容两种返回格式
			const data = res?.data?.results || res?.data || [];
			if (Array.isArray(data)) {
				customerList.value = data.map((item: any) => ({
					value: item.id,
					label: item.company_name || item.customer_code || `客户ID:${item.id}`,
					company_name: item.company_name || '',
					customer_code: item.customer_code || '',
				}));
			}
		} catch (error) {
			// 加载客户列表失败
		}
	};

	// 加载预订订单列表（用于原预订单选择）
	const loadBookingOrderList = async () => {
		try {
			const res = await request({
				url: bookingOrderApiPrefix,
				method: 'get',
				params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
			});
			if (res && res.data && res.data.results && Array.isArray(res.data.results)) {
				bookingOrderList.value = res.data.results.map((item: any) => ({
					value: item.id,
					label: `${item.booking_no || ''} ${item.customer_name || ''}`.trim() || `订单ID:${item.id}`,
				}));
			}
		} catch (error) {
			// 加载预订订单列表失败
		}
	};

	// 获取预订订单列表
	const pageRequest = async (query: any) => {
		return await api.GetList(query);
	};

	// 编辑预订订单（使用删除重建策略）
	const editRequest = async ({ form, row }: EditReq) => {
		if (row.id) {
			form.id = row.id;
		}

		const bookingOrderId = form.id;
		const detailList = form.booking_order_details || [];
		
		if (detailList.length === 0) {
			throw new Error('请至少添加一条预订明细');
		}

		try {
			// 1. 先释放旧的车位分配（这会同时清理 vehicle_ad_position 和 vehicle_ad_resource）
			try {
				await request({
					url: `/api/BookingOrderModelViewSet/${bookingOrderId}/release_positions/`,
					method: 'post',
				});
			} catch (error) {
				// 车位释放失败或无车位需要释放
			}

			// 2. 删除所有旧的明细数据
			try {
				const res = await detailApi.GetList({ booking_order_id: bookingOrderId, limit: 9999 } as any);
				
				// 支持两种数据格式：res.data 直接是数组，或 res.data.results 是数组
				let existingDetails: any[] = [];
				if (res && res.data) {
					if (Array.isArray(res.data)) {
						existingDetails = res.data;
					} else if (res.data.results && Array.isArray(res.data.results)) {
						existingDetails = res.data.results;
					}
				}
				
				for (const detail of existingDetails) {
					await detailApi.DelObj(detail.id);
				}
			} catch (error) {
				throw new Error('删除旧明细数据失败，请重试');
			}

			// 3. 更新主表数据
			// 从form中移除booking_order_details，避免传递给主表更新接口
			const { booking_order_details, ...mainFormData } = form;
			const mainResult = await api.UpdateObj(mainFormData);

			// 4. 创建新的明细数据
			for (let i = 0; i < detailList.length; i++) {
				const detail = detailList[i];
				// 移除id和其他不需要的字段，确保创建新记录
				const { id, create_datetime, update_datetime, creator, modifier, ...detailData } = detail;
				detailData.booking_order_id = bookingOrderId;
				
				await detailApi.AddObj(detailData);
			}

			// 5. 重新分配车位
			try {
				const allocationResult = await request({
					url: `/api/BookingOrderModelViewSet/${bookingOrderId}/allocate_positions/`,
					method: 'post',
				});
				
				if (allocationResult && allocationResult.data && allocationResult.data.success) {
					ElMessage.success('订单更新成功！车位已重新分配');
				} else {
					ElMessage.warning('订单更新成功，但车位分配可能不完整');
				}
			} catch (error: any) {
				// 获取详细错误信息
				let errorMessage = '车位分配失败';
				if (error.response && error.response.data && error.response.data.msg) {
					errorMessage = error.response.data.msg;
				}
				
				ElMessage.error(`订单更新成功，但车位分配失败：${errorMessage}`);
			}

			return mainResult;
		} catch (error: any) {
			ElMessage.error('订单编辑失败：' + (error.message || '未知错误'));
			throw error;
		}
	};

	// 删除预订订单
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};

	// 添加预订订单（使用事务性接口）
	const addRequest = async ({ form }: AddReq) => {
		console.log('[addRequest] 开始提交', { 
			formKeys: Object.keys(form), 
			booking_no: form.booking_no,
			booking_type: form.booking_type,
			booking_status: form.booking_status,
			hasDetails: !!(form.booking_order_details && form.booking_order_details.length > 0)
		});
		
		// 设置预订单类型默认值（新增时字段被隐藏，但提交时需要）
		if (!form.booking_type) {
			form.booking_type = 1; // 默认值：新预订
		}

		// 设置预订单状态默认值（新增时字段被隐藏，但提交时需要）
		if (!form.booking_status) {
			form.booking_status = 3; // 默认值：审批中
		}

		// 检查是否有明细数据
		const detailList = form.booking_order_details || [];
		if (detailList.length === 0) {
			throw new Error('请至少添加一条预订明细');
		}

		console.log('[addRequest] 提交前的表单数据', { 
			booking_no: form.booking_no,
			formData: JSON.stringify(form, null, 2).substring(0, 500) // 只打印前500字符
		});

		// 使用事务性接口创建订单（主表+明细表+车位分配一次性完成）
		try {
			const result = await request({
				url: '/api/BookingOrderModelViewSet/create_with_allocation/',
				method: 'post',
				data: form
			});
			console.log('[addRequest] 提交成功', { result });
			
			// 返回结果（保持与原来的格式一致）
			return {
				code: result.code,
				data: {
					id: result.data.id,
					booking_no: result.data.booking_no
				},
				msg: result.msg
			};
		} catch (error: any) {
			// 获取详细的错误信息
			let errorMessage = '订单创建失败';
			
			if (error.response && error.response.data) {
				const errorData = error.response.data;
				// 后端返回的错误信息在 msg 字段中
				errorMessage = errorData.msg || errorMessage;
			} else if (error.message) {
				errorMessage = error.message;
			}
			
			// 注入样式（确保多行消息正确显示）
			if (!document.getElementById('booking-error-style')) {
				const style = document.createElement('style');
				style.id = 'booking-error-style';
				style.innerHTML = `
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
				`;
				document.head.appendChild(style);
			}
			
			// 显示详细的错误信息（支持换行）
			ElMessage({
				type: 'error',
				message: errorMessage,
				duration: 10000, // 10秒，给用户足够时间阅读详细信息
				dangerouslyUseHTMLString: false, // 使用纯文本，保留换行符
				showClose: true,
				customClass: 'multiline-message',
			});
			
			// 抛出简短错误，避免重复提示
			throw new Error('订单创建失败，请查看详细错误信息');
		}
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
				col: { span: 12 }, // 左右各占50%宽度（每列50%）
				labelWidth: '120px', // 统一label宽度
				labelAlign: 'left', // label文字左对齐
				wrapper: {
					is: 'el-dialog',
					width: '1200px', // 对话框宽度
					closeOnClickModal: false,
					async onOpened({ mode, form }: any) {
						console.log('[onOpened] 表单打开', { mode, formKeys: Object.keys(form), formBookingNo: form.booking_no });
						// 重置标志位，确保新打开对话框时可以加载数据
						form._detailDataLoading = false;
						form._detailDataInitialized = false;
						
						// 新增模式下，自动生成预订单号
						if (mode === 'add') {
							console.log('[onOpened] 新增模式，检查预订单号', { hasBookingNo: !!form.booking_no, bookingNo: form.booking_no });
							if (!form.booking_no) {
								console.log('[onOpened] 预订单号为空，生成预订单号');
								const now = new Date();
								const year = now.getFullYear();
								const month = String(now.getMonth() + 1).padStart(2, '0');
								const day = String(now.getDate()).padStart(2, '0');
								const dateStr = `${year}${month}${day}`;
								const randomStr = String(Math.floor(Math.random() * 9000) + 1000); // 1000-9999
								const bookingNo = `BK-${dateStr}-${randomStr}`;
								console.log('[onOpened] 生成预订单号', { bookingNo });
								// 使用 Object.assign 确保响应式更新
								Object.assign(form, { booking_no: bookingNo });
								console.log('[onOpened] 设置后', { formBookingNo: form.booking_no });
								// 等待多个 tick 确保值被正确渲染
								await nextTick();
								console.log('[onOpened] 第一个 nextTick 后', { formBookingNo: form.booking_no });
								await nextTick();
								console.log('[onOpened] 第二个 nextTick 后', { formBookingNo: form.booking_no });
							}
						}
					},
				},
				async afterOpen({ mode, form }: any) {
					console.log('[afterOpen] 开始执行', { mode, formBookingNo: form.booking_no, formKeys: Object.keys(form) });
					
					// 编辑模式下，加载子表数据
					if (mode === 'edit' && form.id) {
						try {
							const res = await detailApi.GetList({ booking_order_id: form.id, limit: 9999 } as any);
							
							// 支持两种数据格式：res.data 直接是数组，或 res.data.results 是数组
							let dataArray: any[] = [];
							if (res && res.data) {
								if (Array.isArray(res.data)) {
									dataArray = res.data;
								} else if (res.data.results && Array.isArray(res.data.results)) {
									dataArray = res.data.results;
								}
							}
							
							if (dataArray.length > 0) {
								// 设置子表数据
								form.booking_order_details = dataArray;
								// 增加 key 值，强制重新渲染子表组件
								detailTableKey.value++;
								// 等待下一个 tick 确保响应式更新完成
								await nextTick();
								// 再等待一个 tick，确保组件完全渲染
								await nextTick();
							} else {
								form.booking_order_details = [];
								detailTableKey.value++;
							}
							// 标记数据已初始化，后续用户操作（删除等）不会再触发自动加载
							form._detailDataInitialized = true;
						} catch (error) {
							form.booking_order_details = [];
							detailTableKey.value++;
							form._detailDataInitialized = true;
						}
					} else {
						// 新增模式下，初始化为空数组
						form.booking_order_details = [];
						detailTableKey.value++;
						form._detailDataInitialized = true;
					}
				},
			},
			actionbar: {
				buttons: {
					export: {
						show: auth('BookingOrderModelViewSet:Export'),
						text: '导出',
						title: '导出',
						click() {
							return exportRequest(crudExpose.getSearchFormData());
						},
					},
					add: {
						show: auth('BookingOrderModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 280,
				buttons: {
					view: {
						type: 'text',
						order: 1,
						show: auth('BookingOrderModelViewSet:Retrieve'),
					},
					edit: {
						type: 'text',
						order: 2,
						show: auth('BookingOrderModelViewSet:Update'),
					},
					remove: {
						type: 'text',
						order: 4,
						show: auth('BookingOrderModelViewSet:Delete'),
					},
					review: {
						text: '审核',
						type: 'text',
						order: 3,
						show: auth('BookingOrderModelViewSet:Retrieve'),
						click: ({ row }: any) => {
							const dialog = (globalThis as any).__reviewDialog;
							if (dialog) {
								dialog.orderId.value = row.id;
								dialog.orderNo.value = row.booking_no || '';
								dialog.visible.value = true;
							}
						},
					},
					startFlow: {
						text: '发起流程',
						type: 'text',
						order: 5,
						show: true, // 隐藏发起流程按钮
						click: async ({ row }) => {
							try {
								await ElMessageBox.confirm('是否确认发起流程?', '提示', {
									confirmButtonText: '确定',
									cancelButtonText: '取消',
									type: 'warning',
								});

								const loading = ElMessage.success({
									message: '流程发起中...',
									duration: 0,
								});

								const postData = {
									schemeCode: "Test0129", // Adapted scheme code
									processId: row.id,
									title: `预订订单流程-${row.booking_no}`,
									level: "0",
									auditors: null,
									createUserId: userStore.userInfos.id,
								};

								await CreateFlow(postData).then((res: any) => {
									loading.close();
									if (res.code === 2000) {
										ElMessage.success(res.msg || '流程发起成功');
										crudExpose.doRefresh();
									} else {
										ElMessage.error(res.msg || '流程发起失败');
									}
								}).catch((err: any) => {
									loading.close();
									// ElMessage.error('请求失败');
								});

							} catch (e) {
								// Cancelled
							}
						}
					}
				},
			},
			columns: {
				// 序号列
				_index: getIndexColumnConfig(crudExpose),
				
				// 预订单号
				booking_no: {
					title: '预订单号',
					type: 'input',
					search: { 
						show: true,
						component: {
							placeholder: '请输入预订单号进行搜索',
							clearable: true,
							disabled: false, // 明确设置搜索框可编辑
						},
					},
					column: {
						width: 150,
						sortable: 'custom',
					},
					form: {
						show: true,  // 新增和编辑时都显示
						component: {
							placeholder: '系统自动分配',
							disabled: true, // 新增和编辑时都不允许修改
							onInput: (value: any) => {
								console.log('[booking_no字段] onInput 触发', { value });
							},
							onChange: (value: any) => {
								console.log('[booking_no字段] onChange 触发', { value });
							},
						},
					},
				},		

				// 客户（合并 customer_id 和 customer_name）
				customer_id: {
					title: '客户',
					type: 'dict-select',
					search: { 
						show: true,
						// 搜索时支持按客户名称搜索
						component: {
							placeholder: '请选择或搜索客户',
						},
					},
					dict: dict({
						value: 'value',
						label: 'label',
						getData: async () => {
							if (customerList.value.length === 0) {
								await loadCustomerList();
							}
							return customerList.value;
						},
					}),
					column: {
						minWidth: 50,
						sortable: 'custom',
						show: true,
						align: 'left',
						formatter: (context: any) => {
							const value = context.value;
							if (!value) {
								return '-';
							}
							// 从customerList中查找对应的客户信息
							const customer = customerList.value.find((item: any) => item.value === value);
							if (customer) {
								// 优先显示公司名称，如果没有则显示客户编码
								return customer.company_name || customer.customer_code || customer.label || `客户ID:${value}`;
							}
							return `客户ID:${value}`;
						},
					},
					form: {
						rules: [{ required: true, message: '客户必填' }],
						component: {
							placeholder: '请选择客户',
							filterable: true,
							clearable: false,
						},
					},
				},

				// // 预订单类型
				// booking_type: {
				// 	title: '预订单类型',
				// 	type: 'dict-select',
				// 	search: { show: true },
				// 	dict: dict({
				// 		data: [
				// 			{ value: 1, label: '新预订' },
				// 			{ value: 2, label: '续期' },
				// 			{ value: 3, label: '变更' },
				// 		],
				// 	}),
				// 	column: {
				// 		minWidth: 100,
				// 		sortable: 'custom',
				// 		align: 'left',
				// 		show: false, // 隐藏，使用计算字段booking_type_display显示
				// 	},
				// 	form: {
				// 		rules: [{ required: true, message: '预订单类型必填' }],
				// 		value: 1, // 默认值：新预订
				// 		component: {
				// 			placeholder: '请选择预订单类型',
				// 		},
				// 	},
				// },

				// // 预订单类型显示字段
				// booking_type_display: {
				// 	title: '预订单类型',
				// 	type: 'text',
				// 	search: { show: false },
				// 	column: {
				// 		minWidth: 100,
				// 		sortable: false,
				// 		align: 'left',
				// 		show: true,
				// 	},
				// 	form: { show: false },
				// },

				// // 原预订单ID
				// original_booking_id: {
				// 	title: '原预订单',
				// 	type: 'dict-select',
				// 	search: { show: false },
				// 	dict: dict({
				// 		value: 'value',
				// 		label: 'label',
				// 		getData: async () => {
				// 			if (bookingOrderList.value.length === 0) {
				// 				await loadBookingOrderList();
				// 			}
				// 			return bookingOrderList.value;
				// 		},
				// 	}),
				// 	column: {
				// 		minWidth: 200,
				// 		sortable: 'custom',
				// 		show: false,
				// 		formatter: (context: any) => {
				// 			const value = context.value;
				// 			if (!value) {
				// 				return '-';
				// 			}
				// 			const order = bookingOrderList.value.find((item: any) => item.value === value);
				// 			return order ? order.label : `订单ID:${value}`;
				// 		},
				// 	},
				// 	form: {
				// 		show: (context: any) => {
				// 			// 当预订单类型为续期(2)或变更(3)时显示
				// 			const bookingType = context.form.booking_type;
				// 			return bookingType === 2 || bookingType === 3;
				// 		},
				// 		rules: (context: any) => {
				// 			// 当预订单类型为续期(2)或变更(3)时必填
				// 			const bookingType = context.form.booking_type;
				// 			if (bookingType === 2 || bookingType === 3) {
				// 				return [{ required: true, message: '续期或变更预订单必须关联原预订单' }];
				// 			}
				// 			return [];
				// 		},
				// 		component: {
				// 			placeholder: '请选择原预订单（续期/变更时必填）',
				// 			filterable: true,
				// 			clearable: true,
				// 		},
				// 	},
				// },

				// // 预订单状态
				// booking_status: {
				// 	title: '预订单状态',
				// 	type: 'dict-select',
				// 	search: { show: true },
				// 	dict: dict({
				// 		data: [
				// 			{ value: 1, label: '草稿' },
				// 			{ value: 2, label: '待审批' },
				// 			{ value: 3, label: '审批中' },
				// 			{ value: 4, label: '已通过' },
				// 			{ value: 5, label: '已完成' },
				// 			{ value: 6, label: '已取消' },
				// 			{ value: 7, label: '已驳回' },
				// 		],
				// 	}),
				// 	column: {
				// 		minWidth: 100,
				// 		sortable: 'custom',
				// 		align: 'left',
				// 		show: false, // 隐藏，使用计算字段booking_status_display显示
				// 	},
				// 	form: {
				// 		show: (context: any) => {
				// 			// 新增时不显示，编辑时显示
				// 			return context.mode !== 'add';
				// 		},
				// 		rules: [{ required: true, message: '预订单状态必填' }],
				// 		value: 1, // 默认值：草稿
				// 		component: {
				// 			placeholder: '请选择预订单状态',
				// 		},
				// 	},
				// },

				// 预订单状态显示字段
				booking_status_display: {
					title: '预订单状态',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 50,
						sortable: false,
						align: 'left',
						show: true,
					},
					form: { show: false },
				},

				// 预订开始日期
				start_date: {
					title: '投放开始日期',
					type: 'date',
					search: { show: true },
					column: {
						align: 'center',
						width: 150,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						rules: [{ required: true, message: '预订开始日期必填' }],
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择开始日期',
						},
					},
				},

				// 预订结束日期
				end_date: {
					title: '投放结束日期',
					type: 'date',
					search: { show: true },
					column: {
						align: 'center',
						width: 150,
						show: true,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD' },
					},
					form: {
						rules: [{ required: true, message: '预订结束日期必填' }],
						component: {
							format: 'YYYY-MM-DD',
							valueFormat: 'YYYY-MM-DD',
							placeholder: '请选择结束日期',
						},
					},
				},

				// 广告内容描述
				ad_content: {
					title: '广告内容描述',
					type: 'textarea',
					search: { show: true },
					column: {
						minWidth: 100,
						sortable: 'custom',
						show: true,
					},
					form: {
						col: { span: 24 }, // 占满整行
						component: {
							placeholder: '请输入广告内容简述',
							rows: 4,
						},
					},
				},

				// // 已支付金额
				// paid_amount: {
				// 	title: '已支付金额(元)',
				// 	type: 'number',
				// 	search: { show: false },
				// 	column: {
				// 		minWidth: 150,
				// 		sortable: 'custom',
				// 		align: 'right',
				// 		show: true,
				// 		formatter: (context: any) => {
				// 			const value = context.value;
				// 			if (!value) {
				// 				return '-';
				// 			}
				// 			return `¥${Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
				// 		},
				// 	},
				// 	form: {
				// 		component: {
				// 			placeholder: '请输入已支付金额',
				// 			precision: 2,
				// 		},
				// 	},
				// },

				// 审批完成时间
				approved_time: {
					title: '审批完成时间',
					type: 'datetime',
					search: { show: false },
					column: {
						align: 'center',
						width: 160,
						show: false,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						show: false, // 由系统自动设置
					},
				},

				// 提交人ID
				submitter_id: {
					title: '提交人',
					type: 'input',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: false,
					},
					form: {
						show: false, // 由系统自动设置
					},
				},

				// 提交时间
				submit_time: {
					title: '提交时间',
					type: 'datetime',
					search: { show: false },
					column: {
						align: 'center',
						width: 160,
						show: false,
						component: { name: 'fs-date-format', format: 'YYYY-MM-DD HH:mm:ss' },
					},
					form: {
						show: false, // 由系统自动设置
					},
				},

				// 备注
				remark: {
					title: '备注',
					type: 'textarea',
					search: { show: false },
					column: {
						minWidth: 150,
						sortable: 'custom',
						show: false,
					},
					form: {
						col: { span: 24 }, // 占满整行
						component: {
							placeholder: '请输入备注',
							rows: 4,
						},
					},
				},

				// 预订订单明细列表（子表）
				booking_order_details: {
					title: '预订订单明细',
					search: { show: false },
					column: { show: false },
					form: {
						show: true,
						col: { span: 24 }, // 占满整行
						component: {
							render: ({ form }: any) => {
								// 确保 booking_order_details 是数组
								const details = Array.isArray(form.booking_order_details) 
									? form.booking_order_details 
									: [];
								
								// 如果数据为空且是编辑模式，尝试异步加载数据
								// 注意：只有在首次打开对话框时才加载，用户主动删除数据后不再重新加载
								// _detailDataInitialized 标志表示数据已经初始化过（无论是从后端加载还是用户操作后的状态）
								if (details.length === 0 && form.id && !form._detailDataLoading && !form._detailDataInitialized) {
									form._detailDataLoading = true; // 标记正在加载，避免重复加载
									detailApi.GetList({ booking_order_id: form.id, limit: 9999 } as any)
										.then((res: any) => {
											// 支持两种数据格式：res.data 直接是数组，或 res.data.results 是数组
											let dataArray: any[] = [];
											if (res && res.data) {
												if (Array.isArray(res.data)) {
													dataArray = res.data;
												} else if (res.data.results && Array.isArray(res.data.results)) {
													dataArray = res.data.results;
												}
											}
											
											if (dataArray.length > 0) {
												form.booking_order_details = dataArray;
												detailTableKey.value++;
											}
											form._detailDataLoading = false;
											form._detailDataInitialized = true; // 标记数据已初始化
										})
										.catch((error: any) => {
											form._detailDataLoading = false;
											form._detailDataInitialized = true; // 即使失败也标记为已初始化，避免无限重试
										});
								} else if (details.length > 0 && !form._detailDataInitialized) {
									// 如果已经有数据，也标记为已初始化
									form._detailDataInitialized = true;
								}
								
								// 使用 detailTableKey 确保数据更新时强制重新渲染
								return h(BookingOrderDetailTable, {
									modelValue: details,
									bookingOrderId: form.id || null,
									mainOrderStartDate: form.start_date || null,
									mainOrderEndDate: form.end_date || null,
									key: `detail-table-${form.id || 'new'}-${detailTableKey.value}-${details.length}`,
									'onUpdate:modelValue': (value: any) => {
										form.booking_order_details = value;
									},
								});
							},
						},
						value: [], // 默认值为空数组
					},
				},

				// 是否启用显示字段
				is_enabled: {
					title: '是否启用',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 100,
						sortable: false,
						show: false,
						formatter: (context: any) => {
							const value = context.value;
							return value ? '是' : '否';
						},
					},
					form: { show: false },
				},

				// 创建时间
				create_datetime: {
					title: '创建时间',
					type: 'datetime',
					search: { show: false },
					column: {
						show: true,
						align: 'center',
						width: 160,
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
						show: false,
						align: 'center',
						width: 160,
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

