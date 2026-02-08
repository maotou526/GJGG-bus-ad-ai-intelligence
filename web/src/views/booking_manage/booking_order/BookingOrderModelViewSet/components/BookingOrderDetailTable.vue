<template>
  <div class="booking-order-detail-table">
    <fs-crud ref="crudRef" v-bind="crudBinding"></fs-crud>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue';
import { useFs, CreateCrudOptionsProps, CreateCrudOptionsRet, dict } from '@fast-crud/fast-crud';
import { request } from '/@/utils/service';

// API前缀
const roadlineApiPrefix = '/api/RoadlineModelViewSet/';
const companyApiPrefix = '/api/CompanyModelViewSet/';
const mediaTypeApiPrefix = '/api/AdMediaTypeModelViewSet/';

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  bookingOrderId: {
    type: [Number, String],
    default: null
  },
  mainOrderStartDate: {
    type: String,
    default: null
  },
  mainOrderEndDate: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['update:modelValue']);

// 线路列表
const roadlineList = ref<any[]>([]);
// 公司列表
const companyList = ref<any[]>([]);
// 媒体类型列表（完整列表，用于过滤）
const allMediaTypeList = ref<any[]>([]);
// 媒体类型列表（当前过滤后的列表）
const mediaTypeList = ref<any[]>([]);

// 加载线路列表
const loadRoadlineList = async () => {
  try {
    const res = await request({
      url: roadlineApiPrefix,
      method: 'get',
      params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
    });
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
      roadlineList.value = dataArray.map((item: any) => ({
        value: item.id,
        label: item.line_name || `线路ID:${item.id}`,
        company_belong_id: item.company_belong_id || null, // 保存营运公司ID
        company_name: item.company_name || null, // 保存公司名称
      }));
    }
  } catch (error) {
    // 静默处理错误
  }
};

// 加载公司列表
const loadCompanyList = async () => {
  try {
    const res = await request({
      url: companyApiPrefix,
      method: 'get',
      params: { limit: 9999, enabled_mark: 1, delete_mark: 0 },
    });
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
      companyList.value = dataArray.map((item: any) => ({
        value: item.id,
        label: item.shortname || `公司ID:${item.id}`,
      }));
    }
  } catch (error) {
    // 静默处理错误
  }
};

// 加载所有媒体类型列表（完整数据源）
const loadAllMediaTypeList = async () => {
  try {
    // 后端逻辑：如果不传 is_composite，默认只返回组合类型
    // 所以需要分别请求组合类型和非组合类型，然后合并
    const [compositeRes, nonCompositeRes] = await Promise.all([
      // 请求组合类型 (is_composite=true)
      request({
        url: mediaTypeApiPrefix,
        method: 'get',
        params: { 
          limit: 9999, 
          enabled_mark: 1, 
          delete_mark: 0,
          is_composite: 'true' // 明确指定获取组合类型
        },
      }),
      // 请求非组合类型 (is_composite=false)
      request({
        url: mediaTypeApiPrefix,
        method: 'get',
        params: { 
          limit: 9999, 
          enabled_mark: 1, 
          delete_mark: 0,
          is_composite: 'false' // 明确指定获取非组合类型
        },
      }),
    ]);
    
    // 合并两个请求的结果
    let compositeArray: any[] = [];
    let nonCompositeArray: any[] = [];
    
    // 处理组合类型数据
    if (compositeRes && compositeRes.data) {
      if (Array.isArray(compositeRes.data)) {
        compositeArray = compositeRes.data;
      } else if (compositeRes.data.results && Array.isArray(compositeRes.data.results)) {
        compositeArray = compositeRes.data.results;
      }
    }
    
    // 处理非组合类型数据
    if (nonCompositeRes && nonCompositeRes.data) {
      if (Array.isArray(nonCompositeRes.data)) {
        nonCompositeArray = nonCompositeRes.data;
      } else if (nonCompositeRes.data.results && Array.isArray(nonCompositeRes.data.results)) {
        nonCompositeArray = nonCompositeRes.data.results;
      }
    }
    
    // 合并数据
    const allData = [...compositeArray, ...nonCompositeArray];
    
    if (allData.length > 0) {
      allMediaTypeList.value = allData.map((item: any) => ({
        value: item.id,
        label: item.media_name || `媒体类型ID:${item.id}`,
        is_composite: item.is_composite || false,
      }));
    }
  } catch (error) {
    // 静默处理错误
  }
};

// 根据 is_composite 值获取过滤后的媒体类型列表
const getFilteredMediaTypeList = (isComposite: boolean | null): any[] => {
  // 确保完整数据源已加载
  if (allMediaTypeList.value.length === 0) {
    return [];
  }
  
  if (isComposite === null || isComposite === undefined) {
    // 如果 is_composite 未设置，返回所有数据
    return allMediaTypeList.value;
  }
  
  // 根据 is_composite 值过滤
  const filtered = allMediaTypeList.value.filter((item: any) => item.is_composite === isComposite);
  return filtered;
};

const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  return {
    crudOptions: {
      request: {
        // 本地模式不需要 removeRequest，我们用 click 接管删除逻辑
      },
      mode: {
        name: 'local',
        isMergeWhenUpdate: true,
        isAppendWhenAdd: true
      },
      actionbar: {
        buttons: {
          add: { show: false }, // 隐藏顶部添加按钮
        }
      },
      editable: {
        enabled: true,
        mode: 'row',
        activeDefault: true
      },
      table: {
        headerCellStyle: () => {
          return {};
        },
      },
      rowHandle: {
        fixed: 'right',
        width: 150,
        title: '操作',
        buttons: {
          view: {
            show: false, // 隐藏查看按钮
          },
          edit: {
            type: 'text',
            order: 1,
            show: true,
            text: '编辑',
            title: '编辑',
          },
          remove: {
            type: 'text',
            order: 2,
            show: true,
            text: '删除',
            title: '删除',
            // 完全接管删除逻辑
            click: async ({ row, index }: any) => {
              // 优先使用 props.modelValue 作为当前数据源
              let currentData: any[] = [];
              if (props.modelValue && Array.isArray(props.modelValue) && props.modelValue.length > 0) {
                currentData = [...props.modelValue];
              } else if (crudBinding.value?.data && Array.isArray(crudBinding.value.data) && crudBinding.value.data.length > 0) {
                currentData = [...crudBinding.value.data];
              }
              
              if (currentData.length > 0) {
                // 找到要删除的行的索引
                const dataIndex = currentData.findIndex((item: any) => {
                  // 如果有 id，按 id 匹配；否则用引用比较
                  if (row.id && item.id) {
                    return item.id === row.id;
                  }
                  return item === row;
                });
                
                if (dataIndex > -1) {
                  // 从数组中删除
                  currentData.splice(dataIndex, 1);
                  
                  // 更新 crudBinding.value.data
                  if (crudBinding.value) {
                    crudBinding.value.data = currentData;
                  }
                  
                  // 更新长度记录
                  lastDataLength = currentData.length;
                  
                  // 强制重置标志
                  isUpdatingFromProps = false;
                  
                  // emit 到父组件
                  isEmittingToParent = true;
                  emit('update:modelValue', currentData);
                  
                  await nextTick();
                  isEmittingToParent = false;
                }
              }
            },
          },
        },
      },
      form: {
        wrapper: {
          width: '1200px'
        },
        col: {
          span: 12
        },
        labelWidth: '120px',
        async afterOpen({ mode, form }: any) {
          // 确保下拉数据源已加载
          if (roadlineList.value.length === 0 || companyList.value.length === 0 || allMediaTypeList.value.length === 0) {
            await Promise.all([
              loadRoadlineList(),
              loadCompanyList(),
              loadAllMediaTypeList()
            ]);
          }
          // 如果当前行的日期为空，使用主单的日期作为默认值
          if (props.mainOrderStartDate && !form.start_date) {
            form.start_date = props.mainOrderStartDate;
          }
          if (props.mainOrderEndDate && !form.end_date) {
            form.end_date = props.mainOrderEndDate;
          }
          // 如果线路已选择，根据线路的 company_belong_id 自动设置营运公司
          if (form.roadline_id) {
            // 确保线路列表已加载
            if (roadlineList.value.length === 0) {
              await loadRoadlineList();
            }
            const selectedRoadline = roadlineList.value.find((item: any) => item.value === form.roadline_id);
            if (selectedRoadline) {
              if (selectedRoadline.company_belong_id) {
                form.roadline_company_id = selectedRoadline.company_belong_id;
              } else {
                console.warn('线路数据中未找到 company_belong_id，线路ID:', form.roadline_id, '线路数据:', selectedRoadline);
              }
            } else {
              console.warn('未找到对应的线路数据，线路ID:', form.roadline_id);
            }
          }
        },
        async beforeSubmit({ form, mode }: any) {
          // 提交前，确保所有有线路的行都有营运公司ID
          if (form.roadline_id) {
            // 如果营运公司ID为空，尝试从线路数据中获取
            if (!form.roadline_company_id) {
              // 确保线路列表已加载
              if (roadlineList.value.length === 0) {
                await loadRoadlineList();
              }
              const selectedRoadline = roadlineList.value.find((item: any) => item.value === form.roadline_id);
              if (selectedRoadline && selectedRoadline.company_belong_id) {
                form.roadline_company_id = selectedRoadline.company_belong_id;
              } else {
                // 如果仍然找不到，尝试直接从API获取该线路的详细信息
                try {
                  const roadlineRes = await request({
                    url: `${roadlineApiPrefix}${form.roadline_id}/`,
                    method: 'get',
                  });
                  if (roadlineRes && roadlineRes.data && roadlineRes.data.company_belong_id) {
                    form.roadline_company_id = roadlineRes.data.company_belong_id;
                    // 同时更新线路列表缓存
                    const cachedRoadline = roadlineList.value.find((item: any) => item.value === form.roadline_id);
                    if (cachedRoadline) {
                      cachedRoadline.company_belong_id = roadlineRes.data.company_belong_id;
                    }
                  }
                } catch (error) {
                  console.error('获取线路详细信息失败:', error);
                }
              }
            }
            // 最终验证：如果线路已选择但营运公司ID仍为空，抛出错误
            if (!form.roadline_company_id) {
              throw new Error(`线路 "${form.roadline_id}" 未关联营运公司，无法提交`);
            }
          }
        },
        afterSubmit({ mode }) {
          // 提交后更新数据
          const tableData = crudExpose.getTableData();
          emit('update:modelValue', tableData);
        }
      },
      toolbar: {
        show: false
      },
      search: {
        disabled: true,
        show: false
      },
      pagination: {
        show: false
      },
      columns: {
        // 线路ID
        roadline_id: {
          title: '线路',
          type: 'dict-select',
          dict: dict({
            value: 'value',
            label: 'label',
            getData: async () => {
              // 确保数据已加载
              if (roadlineList.value.length === 0) {
                await loadRoadlineList();
              }
              // 如果还是没有数据，再次尝试加载
              if (roadlineList.value.length === 0) {
                await loadRoadlineList();
              }
              return roadlineList.value;
            },
          }),
          column: {
            minWidth: 150,
            show: true,
            formatter: (context: any) => {
              const value = context.value;
              if (!value) return '-';
              const item = roadlineList.value.find((item: any) => item.value === value);
              return item ? item.label : `线路ID:${value}`;
            },
          },
          form: {
            rules: [{ required: true, message: '线路必填' }],
            component: {
              placeholder: '请选择线路',
              filterable: true,
              clearable: false,
              onChange: async ({ value, form }: any) => {
                // 当线路改变时，自动将线路的 company_belong_id 赋值给 roadline_company_id
                if (value) {
                  // 确保线路列表已加载
                  if (roadlineList.value.length === 0) {
                    await loadRoadlineList();
                  }
                  const selectedRoadline = roadlineList.value.find((item: any) => item.value === value);
                  if (selectedRoadline) {
                    if (selectedRoadline.company_belong_id) {
                      form.roadline_company_id = selectedRoadline.company_belong_id;
                    } else {
                      console.warn('线路数据中未找到 company_belong_id，线路ID:', value, '线路数据:', selectedRoadline);
                    }
                  } else {
                    console.warn('未找到对应的线路数据，线路ID:', value);
                  }
                } else {
                  // 如果线路被清空，也清空营运公司
                  form.roadline_company_id = null;
                }
              },
            },
          },
        },

        // 营运公司ID
        roadline_company_id: {
          title: '营运公司',
          type: 'dict-select',
          dict: dict({
            value: 'value',
            label: 'label',
            getData: async () => {
              // 确保数据已加载
              if (companyList.value.length === 0) {
                await loadCompanyList();
              }
              // 如果还是没有数据，再次尝试加载
              if (companyList.value.length === 0) {
                await loadCompanyList();
              }
              return companyList.value;
            },
          }),
          column: {
            minWidth: 150,
            show: true,
            formatter: (context: any) => {
              // 根据当前行的 roadline_id 找到对应的线路，显示线路的 company_name
              const row = context.row;
              if (row && row.roadline_id) {
                const selectedRoadline = roadlineList.value.find((item: any) => item.value === row.roadline_id);
                if (selectedRoadline && selectedRoadline.company_name) {
                  return selectedRoadline.company_name;
                }
              }
              // 如果找不到线路或线路没有 company_name，返回 '-'
              return '-';
            },
          },
          form: {
            show: false, // 隐藏表单字段，不在编辑时显示
            rules: [{ required: true, message: '营运公司必填' }],
          },
        },

        // 媒体类型ID
        media_type_id: {
          title: '媒体类型',
          type: 'dict-select',
          dict: dict({
            value: 'value',
            label: 'label',
            getData: async () => {
              // 确保完整数据源已加载
              if (allMediaTypeList.value.length === 0) {
                await loadAllMediaTypeList();
              }
              // 返回所有媒体类型（不再根据 is_composite 过滤）
              return allMediaTypeList.value;
            },
          }),
          column: {
            minWidth: 150,
            show: true,
            formatter: (context: any) => {
              const value = context.value;
              if (!value) return '-';
              const item = allMediaTypeList.value.find((item: any) => item.value === value);
              return item ? item.label : `媒体类型ID:${value}`;
            },
          },
          form: {
            rules: [{ required: true, message: '媒体类型必填' }],
            component: {
              placeholder: '请选择媒体类型',
              filterable: true,
              clearable: false,
            },
          },
        },



        // 预订数量
        quantity: {
          title: '预订数量',
          type: 'number',
          column: {
            minWidth: 100,
            show: true,
            align: 'right',
            formatter: (context: any) => {
              return context.value ? `${context.value}辆` : '-';
            },
          },
          form: {
            rules: [
              { required: true, message: '预订数量必填' },
              { type: 'number', min: 1, message: '预订数量必须大于0' },
            ],
            component: {
              placeholder: '请输入预订的车辆数量',
              precision: 0,
              min: 1,
            },
          },
        },

        // 投放开始日期
        start_date: {
          title: '投放开始日期',
          type: 'date',
          column: {
            minWidth: 120,
            show: true,
            align: 'center',
          },
          form: {
            rules: [{ required: true, message: '投放开始日期必填' }],
            component: {
              placeholder: '请选择投放开始日期',
              type: 'date',
              valueFormat: 'YYYY-MM-DD',
            },
          },
        },

        // 投放结束日期
        end_date: {
          title: '投放结束日期',
          type: 'date',
          column: {
            minWidth: 120,
            show: true,
            align: 'center',
          },
          form: {
            rules: [
              { required: true, message: '投放结束日期必填' },
              {
                validator: (rule: any, value: any, callback: any, source: any, options: any) => {
                  const startDate = source.start_date;
                  if (startDate && value && new Date(value) < new Date(startDate)) {
                    callback(new Error('结束日期不能早于开始日期'));
                  } else {
                    callback();
                  }
                },
              },
            ],
            component: {
              placeholder: '请选择投放结束日期',
              type: 'date',
              valueFormat: 'YYYY-MM-DD',
            },
          },
        },
      }
    }
  };
};

const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions });

// 防止循环更新的标志
let isUpdatingFromProps = false;
let isEmittingToParent = false;
// 用于跟踪数据长度变化
let lastDataLength = 0;
// 标记组件是否已完成初始化（避免初始化期间 emit 空数据覆盖父组件数据）
let isInitialized = false;
// 组件实例 ID，用于调试
const instanceId = Date.now().toString(36) + Math.random().toString(36).substr(2, 5);

// 监听外部数据变化，同步到表格（参考 crudTable.vue 的实现）
watch(
  () => props.modelValue,
  (value = []) => {
    // 如果正在向父组件发送数据，跳过
    if (isEmittingToParent) {
      return;
    }
    
    if (crudBinding.value) {
      const dataArray = Array.isArray(value) ? value : [];
      
      // 如果数据有变化，强制更新
      if (JSON.stringify(crudBinding.value.data) !== JSON.stringify(dataArray)) {
        isUpdatingFromProps = true;
        crudBinding.value.data = dataArray;
        lastDataLength = dataArray.length;  // 同步更新 lastDataLength
        
        // 如果收到非空数据，标记组件已初始化
        if (dataArray.length > 0) {
          isInitialized = true;
        }
        
        // 数据更新后重新添加按钮
        nextTick(() => {
          addPlusButtonToHeader();
          isUpdatingFromProps = false;
        });
      }
    }
  },
  {
    immediate: true,
    deep: true
  }
);

// 监听表格数据变化，同步到外部
watch(
  () => crudBinding.value.data,
  (value) => {
    // 如果是从 props 更新的，跳过 emit
    if (isUpdatingFromProps) {
      lastDataLength = value?.length || 0;
      return;
    }
    
    const currentLength = value?.length || 0;
    
    // 如果组件还未初始化完成，且数据为空，不 emit（防止初始化时覆盖父组件数据）
    if (!isInitialized && currentLength === 0) {
      return;
    }
    
    // 更新长度记录
    lastDataLength = currentLength;
    
    isEmittingToParent = true;
    emit('update:modelValue', value || []);
    
    // 数据变化后重新添加按钮
    nextTick(() => {
      addPlusButtonToHeader();
      isEmittingToParent = false;
    });
  },
  {
    deep: true,
    immediate: false
  }
);

// 注意：不再监听 editable?.activeRows，因为这会导致数据被意外清空
// 数据同步改为在添加/删除/编辑完成时手动 emit

// 添加行的方法
const handleAddRow = () => {
  // 优先使用 props.modelValue 作为当前数据源（这是父组件传入的真实数据）
  // 其次使用 crudBinding.value.data，最后使用 getTableData()
  let currentData: any[] = [];
  
  if (props.modelValue && Array.isArray(props.modelValue) && props.modelValue.length > 0) {
    currentData = [...props.modelValue];
  } else if (crudBinding.value?.data && Array.isArray(crudBinding.value.data) && crudBinding.value.data.length > 0) {
    currentData = [...crudBinding.value.data];
  } else {
    const tableData = crudExpose.getTableData();
    currentData = tableData ? [...tableData] : [];
  }
  
  // 创建新的空行，使用主单日期作为默认值
  const newRow: any = {
    roadline_id: null,
    roadline_company_id: null,
    media_type_id: null,
    quantity: 1,
    start_date: props.mainOrderStartDate || null,
    end_date: props.mainOrderEndDate || null,
  };
  
  // 创建新数组
  const newData = [...currentData, newRow];
  
  // 设置标志，防止 emit 后被 props watch 覆盖
  isEmittingToParent = true;
  
  // 更新表格数据
  if (crudBinding.value) {
    crudBinding.value.data = newData;
  }
  lastDataLength = newData.length;
  
  // 通知父组件数据变化
  emit('update:modelValue', newData);
  
  // 等待下一个 tick 后重置标志
  nextTick(() => {
    isEmittingToParent = false;
    // 重新添加 + 按钮
    addPlusButtonToHeader();
  });
};

// 暴露方法给父组件
defineExpose({
  getTableData: () => crudExpose.getTableData(),
});

// 初始化时加载数据
onMounted(async () => {
  // 设置标志，防止初始化时 emit 空数据覆盖父组件的数据
  isUpdatingFromProps = true;
  
  // 先加载所有下拉数据源
  await Promise.all([
    loadRoadlineList(),
    loadCompanyList(),
    loadAllMediaTypeList()
  ]);
  
  // 确保初始化时设置表格数据（使用 crudBinding.value.data，参考 crudTable.vue）
  if (crudBinding.value) {
    crudBinding.value.data = props.modelValue || [];
    lastDataLength = crudBinding.value.data.length;
  }
  
  // 在操作列标题中添加"+"按钮
  nextTick(() => {
    addPlusButtonToHeader();
    // 重置标志
    isUpdatingFromProps = false;
    // 标记组件已初始化完成
    isInitialized = true;
  });
});

// 监听 props.modelValue 变化，确保下拉数据源已加载（这个 watch 主要用于加载下拉数据源）
watch(
  () => props.modelValue,
  async (newVal) => {
    // 当数据变化时（编辑窗口打开），确保下拉数据源已加载
    if (newVal !== undefined) {
      // 如果数据源为空，重新加载
      if (roadlineList.value.length === 0 || companyList.value.length === 0 || allMediaTypeList.value.length === 0) {
        await Promise.all([
          loadRoadlineList(),
          loadCompanyList(),
          loadAllMediaTypeList()
        ]);
      }
    }
  },
  { immediate: true }
);

// 在操作列标题中添加"+"按钮的方法
const addPlusButtonToHeader = () => {
  // 查找操作列的表头
  const tableHeader = document.querySelector('.booking-order-detail-table .el-table__header-wrapper');
  if (tableHeader) {
    // 查找所有表头单元格
    const headerCells = tableHeader.querySelectorAll('.el-table__header th');
    headerCells.forEach((cell: any) => {
      const cellText = cell.textContent?.trim();
      // 如果找到"操作"列
      if (cellText && cellText.includes('操作')) {
        const cellContent = cell.querySelector('.cell') || cell;
        if (cellContent) {
          // 关键修复：先移除已存在的按钮（可能是旧组件实例创建的）
          const existingBtn = cellContent.querySelector('.add-row-btn');
          if (existingBtn) {
            existingBtn.remove();
          }
          
          // 创建新的"+"按钮，绑定到当前组件实例
          const addBtn = document.createElement('button');
          addBtn.className = 'add-row-btn';
          addBtn.textContent = '+';
          addBtn.style.cssText = 'margin-left: 8px; padding: 2px 8px; border: 1px solid #409eff; background: #409eff; color: white; border-radius: 4px; cursor: pointer; font-size: 14px; line-height: 1.5; min-width: 24px;';
          addBtn.onclick = (e) => {
            e.stopPropagation();
            handleAddRow();
          };
          
          // 确保单元格内容是 flex 布局，文字居中
          cellContent.style.display = 'flex';
          cellContent.style.alignItems = 'center';
          cellContent.style.justifyContent = 'center';
          cellContent.style.position = 'relative';
          
          // 添加按钮，定位到右侧
          addBtn.style.position = 'absolute';
          addBtn.style.right = '0';
          cellContent.appendChild(addBtn);
        }
      }
    });
  }
};

</script>

<style scoped>
.booking-order-detail-table {
  width: 100%;
  min-height: 200px;
}

.booking-order-detail-table :deep(.fs-crud) {
  width: 100%;
}

.booking-order-detail-table :deep(.fs-crud-table) {
  width: 100%;
}
</style>

