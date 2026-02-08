import { nextTick } from 'vue';
import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { dictionary } from '/@/utils/dictionary';
import { successMessage, errorNotification } from '/@/utils/message';
import { auth } from '/@/utils/authFunction';
import { getCompanySelectorConfig, getIndexColumnConfig } from '/@/utils/commonCrud';
import { listPageDefSingleLineCfg } from '/@/layout/listPage/defConfig';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		const res = await api.GetList(query);
		// 确保返回的数据包含 hasChild 字段（用于树形懒加载图标显示）
		if (res.data && Array.isArray(res.data)) {
			res.data = res.data.map((item: any) => {
				// 删除可能存在的空 children，避免影响懒加载展开图标显示
				if (Object.prototype.hasOwnProperty.call(item, 'children')) {
					delete item.children;
				}
				// 如果后端返回了 hasChild，确保字段名正确（Element Plus 树表需要 hasChild 字段）
				if (item.hasChild === undefined && item.haschild !== undefined) {
					item.hasChild = item.haschild;
				}
				// 确保 hasChild 是布尔值
				if (item.hasChild !== undefined) {
					item.hasChild = Boolean(item.hasChild);
				}
				return item;
			});
		}
		return res;
	};
	const editRequest = async ({ form, row }: EditReq) => {
		// 校验：上级不能选择自身
		const nextParentId = (form as any)?.parentid ?? row.parentid;
		if (row?.id && nextParentId && String(nextParentId) === String(row.id)) {
			// 明显弹窗提示
			errorNotification('保存失败：上级公司不能选择自身');
			return Promise.reject(new Error('保存失败：上级公司不能选择自身'));
		}
		// 提取必要的基础字段（排除计算字段）
		const baseFields = {
			id: row.id,
			parentid: row.parentid ?? null, // 确保 parentid 被保留（子项的关键字段）
			category: row.category,
			sortcode: row.sortcode,
			enabled_mark: row.enabled_mark ?? 1,
			delete_mark: row.delete_mark ?? 0,
		};

		// 合并基础字段和表单数据，确保所有字段都被包含
		const updateData = {
			...baseFields,
			...form, // 覆盖用户修改的字段（全称、简称、编码等）
			id: row.id, // 确保ID存在
		};

		return await api.UpdateObj(updateData);
	};
	const delRequest = async ({ row }: DelReq) => {
		const result = await api.DelObj(row.id);
		// 删除成功后，清空树形缓存并刷新表格
		const tableRef = crudExpose.getBaseTableRef();
		if (tableRef?.store?.states) {
			// 清空已渲染数据与树结构缓存
			tableRef.store.states.data && (tableRef.store.states.data.value = []);
			tableRef.store.states.treeData && (tableRef.store.states.treeData.value = []);
			tableRef.store.states.lazyTreeNodeMap && (tableRef.store.states.lazyTreeNodeMap.value = {});
		}
		// 使用 nextTick 确保 DOM 更新后再刷新，让树表状态正确恢复
		nextTick(() => {
			// 刷新列表（重新加载根节点）
			crudExpose.doRefresh();
		});
		return result;
	};
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	const loadContentMethod = (tree: any, treeNode: any, resolve: Function) => {
		// 注意：这里直接调用 api.GetList，仅携带 parentid，避免被全局筛选条件干扰
		api.GetList({ parentid: tree.id } as any).then((res: any) => {
			// 确保子节点数据也包含 hasChild 字段
			const data = res.data || [];
			const processedData = data.map((item: any) => {
				// 删除可能存在的空 children，避免影响懒加载展开图标显示
				if (Object.prototype.hasOwnProperty.call(item, 'children')) {
					delete item.children;
				}
				if (item.hasChild === undefined && item.haschild !== undefined) {
					item.hasChild = item.haschild;
				}
				if (item.hasChild !== undefined) {
					item.hasChild = Boolean(item.hasChild);
				}
				return item;
			});
			resolve(processedData);
		});
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
			actionbar: {
				buttons: {
					add: {
						show: auth('CompanyModelViewSet:Create'),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 200,
				buttons: {
					view: { show: false },
					edit: { iconRight: 'Edit', type: 'text', show: auth('CompanyModelViewSet:Update') },
					remove: { iconRight: 'Delete', type: 'text', show: auth('CompanyModelViewSet:Delete') },
				},
			},
			form: {
				afterSubmit({ mode }: any) {
					const tableRef = crudExpose.getBaseTableRef();
					if (tableRef?.store?.states) {
						// 清空已渲染数据与树结构缓存
						tableRef.store.states.data && (tableRef.store.states.data.value = []);
						tableRef.store.states.treeData && (tableRef.store.states.treeData.value = []);
						tableRef.store.states.lazyTreeNodeMap && (tableRef.store.states.lazyTreeNodeMap.value = {});
					}
					// 使用 nextTick 确保 DOM 更新后再刷新，让树表状态正确恢复
					nextTick(() => {
						// 刷新列表（重新加载根节点）
						crudExpose.doRefresh();
					});
				},
			},
			pagination: { show: false },
			table: {
				rowKey: 'id',
				lazy: true,
				load: loadContentMethod,
				treeProps: { children: 'children', hasChildren: 'hasChild' },
			},
		columns: {
			// 序号列（跨页连续编号）
			_index: getIndexColumnConfig(crudExpose,{width:80}),
			search: {
				title: '关键词',
				column: { show: false },
					search: {
						show: true,
						component: {
							props: { clearable: true },
							placeholder: '请输入公司名称/简称/编码',
						},
					},
				form: { show: false },
			},
			fullname: {
					title: '全称',
					search: { show: false },
					type: 'input',
					column: { show: true },
					form: {
						rules: [{ required: true, message: '全称必填项' }],
						component: { placeholder: '请输入全称' },
					},
				},
				shortname: {
					title: '简称',
					search: { show: false },
					treeNode: true,
					type: 'input',
					column: { minWidth: 120 },
					form: {
						rules: [{ required: true, message: '简称必填项' }],
						component: { placeholder: '请输入名称' },
					},
				},
				category: {
					title: '公司分类',
					search: { show: false },
					type: 'number',
					column: { show: false },
					form: {
						rules: [{ required: true, message: '公司分类必填项' }],
						value: 1, // 默认值为1
						show: false,
						component: { placeholder: '请输入公司分类（数字）' },
					},
				},
				parentid: {
					...getCompanySelectorConfig({
						loadMethod: loadContentMethod,
						crudExpose,
						required: false, // 上级公司不是必填的
					}),
					title: '上级',
					search: { disabled: true },
					width: 130,
					column: { show: false }
				},
				encode: {
					title: '编码',
					search: { show: false },
					type: 'input',
					column: { minWidth: 90 },
					form: {
						rules: [{ required: true, message: '编码必填项' }],
						component: { placeholder: '请输入编码' },
					},
				},
				sortcode: {
					title: '排序',
					search: { show: false },
					type: 'number',
					column: { show: false },
					form: {
						rules: [{ required: true, message: '排序必填项' }],
						value: 1, // 默认值为1
						component: { placeholder: '请输入排序' },
					},
				},
				// 启用状态
				enabled_mark: {
					title: '启用状态',
					type: 'dict-select',
					search: { show: true },
					dict: dict({
						data: [
							{ value: 1, label: '启用' },
							{ value: 0, label: '禁用' },
						],
					}),
					column: {
						align: 'left',
						minWidth: 120,
						sortable: 'custom',
						show: true, // 隐藏原始字段，使用显示字段
					},
					form: {
						rules: [{ required: true, message: '启用状态必填' }],
						value: 1, // 默认值为启用
						component: {
							placeholder: '请选择启用状态',
						},
					},
				},
			},
		},
	};
};
