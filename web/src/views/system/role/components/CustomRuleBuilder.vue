<template>
  <div class="custom-rule-builder">
    <!-- 工具栏 -->
    <div class="rule-toolbar">
      <el-button size="small" type="primary" icon="Plus" @click="addRule">
        新增规则
      </el-button>
      <span class="tips-text">
        提示：添加规则后，在逻辑公式中使用规则编号组合，如：(1 OR 2) AND 3
      </span>
    </div>

    <!-- 规则列表 -->
    <div class="rules-list" v-if="rules.length > 0">
      <div v-for="(rule, index) in rules" :key="rule.id" class="rule-item">
        <div class="rule-header">
          <span class="rule-number">规则 {{ rule.id }}</span>
          <el-button 
            link 
            type="danger" 
            size="small" 
            icon="Delete"
            @click="removeRule(index)"
          >
            删除
          </el-button>
        </div>
        
        <div class="rule-content">
          <div class="rule-row">
            <!-- 字段输入 -->
            <div class="rule-field">
              <label>字段</label>
              <el-input
                v-model="rule.field"
                placeholder="如：dept_belong_id"
                clearable
              />
            </div>
            
            <!-- 操作符选择 -->
            <div class="rule-field">
              <label>操作符</label>
              <el-select 
                v-model="rule.operator" 
                placeholder="选择"
              >
                <el-option 
                  v-for="op in operatorOptions" 
                  :key="op.value"
                  :label="op.label"
                  :value="op.value"
                />
              </el-select>
            </div>
            
            <!-- 值类型选择 -->
            <div class="rule-field">
              <label>值类型</label>
              <el-select 
                v-model="rule.value_type" 
                placeholder="选择"
                @change="onValueTypeChange(rule)"
              >
                <el-option 
                  v-for="vt in valueTypeOptions" 
                  :key="vt.value"
                  :label="vt.label"
                  :value="vt.value"
                />
              </el-select>
            </div>
            
            <!-- 值输入（仅当值类型需要输入时显示） -->
            <div class="rule-field" v-if="needInput(rule.value_type)">
              <label>值</label>
              <el-input 
                v-model="rule.value" 
                placeholder="输入值"
              />
            </div>
            
            <!-- 值说明（不需要输入时显示） -->
            <div class="rule-field rule-value-desc" v-else>
              <label>值</label>
              <el-tag type="info">
                {{ getValueDescription(rule.value_type) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <el-empty 
      v-else 
      description="暂无规则，点击「新增规则」开始配置"
      :image-size="80"
    />

    <!-- 逻辑公式 -->
    <div class="logic-section" v-if="rules.length > 0">
      <div class="section-title">逻辑公式</div>
      <el-input 
        v-model="logic" 
        placeholder="使用规则编号编写逻辑公式，如：(1 OR 2) AND 3"
        clearable
      >
        <template #prepend>公式</template>
      </el-input>
      <div class="logic-help">
        <span>支持运算符：AND（并且）、OR（或者）、()（括号）</span>
        <span>当前规则：{{ rules.map(r => r.id).join(', ') }}</span>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, computed } from 'vue';
import { getModelFields, getOperators, getValueTypes } from './api';
import { ElMessage } from 'element-plus';

interface RuleItem {
  id: number;
  field: string;
  operator: string;
  value_type: string;
  value: any;
}

interface Props {
  modelValue?: {
    logic: string;
    rules: RuleItem[];
  } | null;
  modelName?: string;  // 模型名称（可选，为空则不加载字段选项）
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  modelName: ''
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: { logic: string; rules: RuleItem[] }): void;
}>();

// 规则列表
const rules = ref<RuleItem[]>([]);
// 逻辑公式
const logic = ref('');
// 字段选项
const fieldOptions = ref<any[]>([]);
// 操作符选项
const operatorOptions = ref<any[]>([]);
// 值类型选项
const valueTypeOptions = ref<any[]>([]);

// 初始化数据
watch(
  () => props.modelValue,
  (val) => {
    if (val && val.rules) {
      logic.value = val.logic || '';
      rules.value = JSON.parse(JSON.stringify(val.rules));
    } else {
      logic.value = '';
      rules.value = [];
    }
  },
  { immediate: true }
);

// 监听变化，向父组件同步（使用防抖优化性能）
let syncTimer: any = null;
watch(
  [rules, logic],
  () => {
    // 防抖：避免频繁触发
    if (syncTimer) {
      clearTimeout(syncTimer);
    }
    syncTimer = setTimeout(() => {
      emit('update:modelValue', {
        logic: logic.value,
        rules: rules.value
      });
    }, 300);  // 300ms 防抖
  },
  { deep: true }
);

// 新增规则
const addRule = () => {
  // 自动编号：取当前最大ID + 1
  const maxId = rules.value.length > 0 
    ? Math.max(...rules.value.map(r => r.id)) 
    : 0;
  
  const newRule: RuleItem = {
    id: maxId + 1,
    field: '',
    operator: 'eq',
    value_type: 'static',
    value: ''
  };
  
  rules.value.push(newRule);
  ElMessage.success(`已添加规则 ${newRule.id}`);
};

// 删除规则
const removeRule = (index: number) => {
  const ruleId = rules.value[index].id;
  rules.value.splice(index, 1);
  ElMessage.success(`已删除规则 ${ruleId}`);
};

// 值类型改变时的处理
const onValueTypeChange = (rule: RuleItem) => {
  // 如果切换到不需要输入的值类型，清空 value
  if (!needInput(rule.value_type)) {
    rule.value = null;
  }
};

// 判断是否需要输入值
const needInput = (valueType: string) => {
  const vt = valueTypeOptions.value.find((v: any) => v.value === valueType);
  return vt ? vt.need_input : true;
};

// 获取值类型的说明
const getValueDescription = (valueType: string) => {
  const vt = valueTypeOptions.value.find((v: any) => v.value === valueType);
  return vt ? vt.description : '';
};

// 获取值类型的提示
const getValueTypeHint = (valueType: string) => {
  const hints: Record<string, string> = {
    'static': '请输入具体的值',
  };
  return hints[valueType] || '';
};

// 加载选项数据
onMounted(async () => {
  try {
    // 加载字段选项（仅当提供了模型名时）
    if (props.modelName) {
      const fieldsRes = await getModelFields(props.modelName);
      if (fieldsRes.data) {
        fieldOptions.value = fieldsRes.data;
      }
    }
    
    // 加载操作符选项
    const opsRes = await getOperators();
    if (opsRes.data) {
      operatorOptions.value = opsRes.data;
    }
    
    // 加载值类型选项
    const vtsRes = await getValueTypes();
    if (vtsRes.data) {
      valueTypeOptions.value = vtsRes.data;
    }
  } catch (error) {
    console.error('加载选项失败:', error);
    // 不阻止使用，字段可以手动输入
  }
});
</script>

<style scoped lang="scss">
.custom-rule-builder {
  margin-top: 16px;
  
  .rule-toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    
    .tips-text {
      color: #909399;
      font-size: 12px;
      margin-left: auto;
    }
  }
  
  .rules-list {
    max-height: 500px;
    overflow-y: auto;
    
    .rule-item {
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      padding: 12px;
      margin-bottom: 12px;
      background: #fafafa;
      
      .rule-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        
        .rule-number {
          font-weight: bold;
          color: #409eff;
          font-size: 14px;
        }
      }
      
      .rule-content {
        .rule-row {
          display: flex;
          gap: 12px;
          align-items: flex-start;
          
          .rule-field {
            flex: 1;
            min-width: 0;
            
            label {
              display: block;
              font-size: 12px;
              color: #606266;
              margin-bottom: 4px;
              font-weight: 500;
            }
            
            :deep(.el-input),
            :deep(.el-select) {
              width: 100%;
            }
            
            &.rule-value-desc {
              display: flex;
              flex-direction: column;
              justify-content: flex-start;
              
              .el-tag {
                margin-top: 4px;
              }
            }
          }
        }
      }
    }
  }
  
  .logic-section {
    margin-top: 20px;
    padding: 16px;
    background: #f0f9ff;
    border-radius: 4px;
    border: 1px solid #d9ecff;
    
    .section-title {
      font-weight: bold;
      margin-bottom: 10px;
      color: #303133;
    }
    
    .logic-help {
      display: flex;
      justify-content: space-between;
      margin-top: 8px;
      font-size: 12px;
      color: #606266;
    }
  }
}
</style>

