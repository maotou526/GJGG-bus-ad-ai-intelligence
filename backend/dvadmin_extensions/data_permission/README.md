# 自定义数据权限扩展模块

## 📋 概述

本模块扩展了原框架的数据权限功能，提供灵活的自定义规则配置，支持任意字段、任意操作符、动态值和复杂逻辑组合。

### 特性

- ✅ 自定义字段过滤（不限于 dept_belong_id）
- ✅ 丰富的操作符（=, >, <, IN, LIKE等）
- ✅ 动态值类型（当前用户、当前部门、部门树等）
- ✅ 逻辑表达式（AND, OR, 括号组合）
- ✅ 可视化配置界面
- ✅ SQL 实时预览
- ✅ 零新表（扩展原表字段）
- ✅ 代码分离（独立扩展模块）

---

## 🚀 快速开始

### 1. 后端配置

#### 1.1 修改原框架代码

##### ① 扩展模型：添加 `custom_rules` 字段

**文件**：`backend/dvadmin/system/models.py`

在 `RoleMenuButtonPermission` 模型中添加：

```python
class RoleMenuButtonPermission(CoreModel):
    # ... 现有字段 ...
    
    DATASCOPE_CHOICES = (
        (0, "仅本人数据权限"),
        (1, "本部门及以下数据权限"),
        (2, "本部门数据权限"),
        (3, "全部数据权限"),
        (4, "自定数据权限"),
        (5, "自定义规则"),  # ← 新增选项
    )
    
    # ========== 扩展字段 ==========
    custom_rules = models.TextField(
        null=True,
        blank=True,
        default=None,
        verbose_name="自定义数据权限规则",
        help_text="JSON字符串格式的规则配置，当data_range=5时使用"
    )
```

---

##### ② 集成扩展过滤器

**文件**：`backend/dvadmin/utils/filters.py`

在文件开头添加导入：

```python
# ========== 扩展模块集成 ==========
try:
    from dvadmin_extensions.data_permission.filters import CustomRuleDataPermissionFilter
    HAS_CUSTOM_RULE_EXTENSION = True
except ImportError:
    HAS_CUSTOM_RULE_EXTENSION = False
    CustomRuleDataPermissionFilter = None
```

在 `DataLevelPermissionsFilter.filter_queryset()` 方法开头添加：

```python
def filter_queryset(self, request, queryset, view):
    # ========== 扩展模块集成：检查是否已应用自定义规则 ==========
    if getattr(request, '_custom_rule_applied', False):
        return queryset
    
    # ... 原有逻辑 ...
```

---

##### ③ 注册扩展应用

**文件**：`backend/application/settings.py`

添加扩展应用到 `INSTALLED_APPS`：

```python
# ========== 扩展模块（可选功能） ==========
Extension_Apps = [
    'dvadmin_extensions.data_permission',  # 自定义数据权限扩展
]

INSTALLED_APPS += My_Apps + Extension_Apps

# 扩展功能开关
ENABLE_CUSTOM_DATA_PERMISSION = True  # 启用自定义数据权限
```

---

##### ④ 注册扩展路由

**文件**：`backend/application/urls.py`

添加扩展路由：

```python
# ========== 扩展模块路由（扩展功能） ==========
Extension_Urls = (
    path("api/ext/data_permission/", include("dvadmin_extensions.data_permission.urls")),
)

# 合并所有路由
urlpatterns += My_Urls + Extension_Urls
```

---

#### 1.2 执行数据库迁移

**方式1：使用 Django 迁移（推荐）**

```bash
cd backend
python manage.py makemigrations system --name add_custom_rules_field
python manage.py migrate system
```

**方式2：直接执行 SQL**

```sql
-- 添加 custom_rules 字段（TEXT 类型，存储 JSON 字符串）
ALTER TABLE dvadmin_role_menu_button_permission 
ADD COLUMN custom_rules TEXT NULL;
```

---

#### 1.3 重启后端服务

```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

查看日志，确认扩展模块已加载：
```
[INFO] ✅ 自定义数据权限过滤器已注册
```

### 2. 前端配置

#### 2.1 修改文件

##### ① 扩展类型定义

**文件**：`web/src/views/system/role/types.ts`

添加自定义规则相关类型：

```typescript
export interface RoleMenuBtnType {
  // ... 现有字段 ...
  role_menu_btn_perm_id?: string | number;  // 权限记录ID
  custom_rules?: CustomRulesConfig | null;  // ← 新增
}

export interface CustomRulesConfig {
  logic: string;
  rules: RuleItem[];
}

export interface RuleItem {
  id: number;
  field: string;
  operator: string;
  value_type: string;
  value: any;
  label?: string;
}
```

---

##### ② 添加 API 接口

**文件**：`web/src/views/system/role/components/api.ts`

添加扩展 API 函数：

```typescript
// ========== 自定义数据权限扩展 API ==========

/** 获取模型字段列表 */
export function getModelFields(modelName: string) {
    return request({
        url: '/api/ext/data_permission/data_permission_rule/get_field_options/',
        method: 'get',
        params: { model_name: modelName },
    });
}

/** 获取操作符列表 */
export function getOperators(fieldType?: string) {
    return request({
        url: '/api/ext/data_permission/data_permission_rule/get_operator_options/',
        method: 'get',
        params: fieldType ? { field_type: fieldType } : {},
    });
}

/** 获取值类型列表 */
export function getValueTypes() {
    return request({
        url: '/api/ext/data_permission/data_permission_rule/get_value_type_options/',
        method: 'get',
    });
}
```

---

##### ③ 创建规则构建器组件

**文件**：`web/src/views/system/role/components/CustomRuleBuilder.vue`

这是一个新的 Vue 组件，提供可视化的规则配置界面。（完整代码见文件）

核心功能：
- 新增/删除规则
- 配置字段、操作符、值类型、值
- 输入逻辑公式
- 自动加载选项（字段、操作符、值类型）

---

##### ④ 集成到角色权限配置

**文件**：`web/src/views/system/role/components/RoleMenuBtn.vue`

修改1：添加导入

```typescript
import CustomRuleBuilder from './CustomRuleBuilder.vue';
```

修改2：扩展数据权限范围选项

```typescript
const dataPermissionRange = ref([
  { label: '仅本人数据权限', value: 0 },
  { label: '本部门及以下数据权限', value: 1 },
  { label: '本部门数据权限', value: 2 },
  { label: '全部数据权限', value: 3 },
  { label: '自定数据权限', value: 4 },
  { label: '自定义规则', value: 5 },  // ← 新增
]);
```

修改3：动态调整对话框宽度

```vue
<el-dialog 
  v-model="dialogVisible" 
  title="数据权限配置" 
  :width="selectBtn.data_range === 5 ? '1000px' : '400px'"
  :close-on-click-modal="false"
>
```

修改4：添加规则构建器

```vue
<template>
  <el-dialog ...>
    <!-- 现有的选择框 -->
    <el-select v-model="selectBtn.data_range" ...>
    
    <!-- ← 新增：自定义规则构建器 -->
    <CustomRuleBuilder
      v-if="selectBtn.data_range === 5"
      v-model="selectBtn.custom_rules"
      :model-name="currentModelName"
    />
  </el-dialog>
</template>
```

修改5：保存时 JSON 序列化

```typescript
const handleDialogConfirm = async () => {
  const payload: any = {
    role_menu_btn_perm_id: permId,
    data_range: selectBtn.value.data_range,
    dept: selectBtn.value.dept || [],
  };
  
  // ← 新增：处理自定义规则
  if (selectBtn.value.data_range === 5) {
    payload.custom_rules = JSON.stringify(selectBtn.value.custom_rules);
  }
  
  await setRoleMenuBtnDataRange(payload);
};
```

---

#### 2.2 前端使用步骤

1. 打开**系统管理** → **角色管理**
2. 选择一个角色，点击**权限配置**
3. 选择一个菜单
4. 勾选功能按钮（如"查询"）
5. 点击按钮后面的**小齿轮图标** ⚙️
6. 在弹窗中选择**"自定义规则"**
7. 配置自定义规则：
   - 点击"新增规则"
   - 输入字段名（如：`dept_belong_id`）
   - 选择操作符（如：`包含 (IN)`）
   - 选择值类型（如：`当前部门树`）
   - 重复添加多个规则
   - 在逻辑公式框输入：`(1 OR 2) AND 3`
8. 点击"确定"保存

### 3. 后端序列化器修改

#### 扩展序列化器以支持 `custom_rules` 字段

**文件**：`backend/dvadmin/system/views/role_menu_button_permission.py`

##### ① 在序列化器中添加 `custom_rules` 字段

```python
class RoleMenuButtonSerializer(CustomModelSerializer):
    # ... 现有字段 ...
    custom_rules = serializers.SerializerMethodField()
    
    def get_custom_rules(self, instance):
        """获取自定义规则配置（TEXT 转 dict）"""
        obj = self.get_role_menu_btn_prem(instance)
        if obj is None or obj.custom_rules is None:
            return None
        
        if isinstance(obj.custom_rules, str):
            import json
            try:
                return json.loads(obj.custom_rules)
            except:
                return None
        return obj.custom_rules
    
    class Meta:
        model = MenuButton
        fields = ['id', 'menu', 'name', 'isCheck', 'data_range', 
                  'role_menu_btn_perm_id', 'dept', 'custom_rules']  # ← 添加
```

##### ② 在保存接口中处理 `custom_rules`

```python
@action(methods=['PUT'], detail=False, permission_classes=[IsAuthenticated])
def set_role_menu_btn_data_range(self, request):
    """设置角色-菜单-按钮-权限"""
    try:
        data = request.data
        # ... 现有逻辑 ...
        
        # ← 新增：处理自定义规则（data_range=5）
        if instance.data_range == 5:
            custom_rules = data.get('custom_rules')
            if custom_rules:
                if isinstance(custom_rules, str):
                    instance.custom_rules = custom_rules
                else:
                    import json
                    instance.custom_rules = json.dumps(custom_rules, ensure_ascii=False)
            else:
                instance.custom_rules = None
        else:
            instance.custom_rules = None
        
        instance.save()
        # ...
    except Exception as e:
        return ErrorResponse(msg=f"保存失败：{str(e)}")
```

---

## 📖 规则配置详解

### 字段

**字段名称**：数据库表的列名

- 直接输入字段名（如：`dept_belong_id`）
- 必须是模型中实际存在的字段

**常用字段**：
- `dept_belong_id` - 部门归属ID
- `creator_id` - 创建人ID
- `company_id` - 公司ID
- `park_status` - 停车场状态
- `enabled_mark` - 启用标记
- `create_datetime` - 创建时间

### 操作符

| 操作符 | 说明 | 示例 |
|-------|------|------|
| 等于 (=) | 精确匹配 | `park_status = 2` |
| 不等于 (!=) | 不匹配 | `park_status != 0` |
| 大于 (>) | 数值比较 | `parking_space > 50` |
| 大于等于 (>=) | 数值比较 | `park_status >= 2` |
| 小于 (<) | 数值比较 | `parking_space < 100` |
| 小于等于 (<=) | 数值比较 | `park_status <= 2` |
| 包含 (IN) | 在列表中 | `dept_belong_id IN [3, 31, 32]` |
| 不包含 (NOT IN) | 不在列表中 | `dept_belong_id NOT IN [5, 6]` |
| 包含字符串 | 模糊匹配 | `park_name LIKE '%停车场%'` |
| 为空 | NULL 检查 | `description IS NULL` |
| 不为空 | NOT NULL | `description IS NOT NULL` |

### 值类型

| 值类型 | 说明 | 需要输入 | 返回类型 | 示例值 | 常用场景 |
|-------|------|---------|---------|--------|---------|
| **固定值** | 手动输入的值 | ✅ | 任意 | `2`, `"测试"` | 指定状态、类型等 |
| **当前用户** | 当前登录用户ID | ❌ | int | `123` | 只看自己创建的数据 |
| **当前部门** | 当前用户所在部门ID | ❌ | int | `3` | 只看自己部门的数据 |
| **当前公司** | 当前用户所在公司ID | ❌ | int | `1` | 多公司系统隔离 |
| **当前部门树** | 当前部门及所有下级部门 | ❌ | list | `[3, 31, 32, 33]` | 部门经理看下属（最常用）✅ |

**注意**：
- 使用 `当前部门树` 时，操作符应选择 `包含 (IN)`，因为返回的是列表
- 使用 `当前用户` / `当前部门` / `当前公司` 时，操作符应选择 `等于 (=)`，因为返回的是单个值

### 逻辑公式

**语法**：
- 使用规则编号（1, 2, 3...）
- 使用 `AND`（并且）、`OR`（或者）
- 使用括号 `()` 控制优先级

**示例**：

```
简单公式：
- 1 AND 2 AND 3          # 所有规则都满足
- 1 OR 2 OR 3            # 任一规则满足

复杂公式：
- (1 OR 2) AND 3         # (规则1 或 规则2) 并且 规则3
- 1 AND (2 OR 3)         # 规则1 并且 (规则2 或 规则3)
- (1 AND 2) OR (3 AND 4) # (规则1 且 规则2) 或 (规则3 且 规则4)
```

---

## 💡 配置示例

### 示例1：部门权限 + 状态过滤（最常用）

**业务需求**：
- 可以看到：本部门及下级部门的数据
- 或者：我创建的数据
- 并且：状态为运营中（status >= 2）

**规则配置**：

| 规则ID | 字段 | 操作符 | 值类型 | 值 |
|-------|------|--------|--------|-----|
| 1 | dept_belong_id | 包含 (IN) | 当前部门树 | - |
| 2 | creator_id | 等于 (=) | 当前用户 | - |
| 3 | park_status | 大于等于 (>=) | 固定值 | 2 |

**逻辑公式**：`(1 OR 2) AND 3`

**JSON 配置**：
```json
{
  "logic": "(1 OR 2) AND 3",
  "rules": [
    {"id": 1, "field": "dept_belong_id", "operator": "in", "value_type": "dept_tree", "value": null},
    {"id": 2, "field": "creator_id", "operator": "eq", "value_type": "current_user", "value": null},
    {"id": 3, "field": "park_status", "operator": "gte", "value_type": "static", "value": 2}
  ]
}
```

**生成SQL**（假设当前用户ID=123，部门ID=3，下级部门=[31,32]）：
```sql
WHERE (dept_belong_id IN (3, 31, 32) OR creator_id = 123) 
  AND park_status >= 2
```

---

### 示例2：只看自己部门的数据（简单场景）

**业务需求**：
- 只看自己部门的数据（不包含下级部门）

**规则配置**：

| 规则ID | 字段 | 操作符 | 值类型 | 值 |
|-------|------|--------|--------|-----|
| 1 | dept_belong_id | 等于 (=) | 当前部门 | - |

**逻辑公式**：`1`

**JSON 配置**：
```json
{
  "logic": "1",
  "rules": [
    {"id": 1, "field": "dept_belong_id", "operator": "eq", "value_type": "current_dept", "value": null}
  ]
}
```

**生成SQL**：
```sql
WHERE dept_belong_id = 3
```

---

### 示例3：多条件组合

**业务需求**：
- 公司必须是当前公司
- 并且（部门是本部门 或 是公开数据）

**规则配置**：

| 规则ID | 字段 | 操作符 | 值类型 | 值 |
|-------|------|--------|--------|-----|
| 1 | company_id | 等于 (=) | 当前公司 | - |
| 2 | dept_belong_id | 等于 (=) | 当前部门 | - |
| 3 | is_public | 等于 (=) | 固定值 | 1 |

**逻辑公式**：`1 AND (2 OR 3)`

**生成SQL**：
```sql
WHERE company_id = 1 AND (dept_belong_id = 3 OR is_public = 1)
```

---

## 🔧 扩展模块说明

### 目录结构

```
backend/dvadmin_extensions/data_permission/
├── __init__.py              # 模块初始化，指定 default_app_config
├── apps.py                  # 应用配置（自动注册过滤器到 ViewSet）
├── engine.py                # 规则引擎核心（解析JSON，生成Q对象）
├── filters.py               # 扩展过滤器（CustomRuleDataPermissionFilter）
├── serializers.py           # API序列化器
├── views.py                 # API视图（DataPermissionRuleViewSet）
├── urls.py                  # 路由配置
└── README.md                # 本文档
```

### 核心文件详解

#### `apps.py` - 应用配置

```python
class DataPermissionConfig(AppConfig):
    name = 'dvadmin_extensions.data_permission'
    
    def ready(self):
        """Django 启动时自动执行，注册扩展过滤器"""
        from dvadmin.utils import viewset
        from .filters import CustomRuleDataPermissionFilter
        
        # 插入到 extra_filter_class 最前面（优先级最高）
        viewset.CustomModelViewSet.extra_filter_class.insert(
            0,
            CustomRuleDataPermissionFilter
        )
```

**作用**：
- 在 Django 启动时自动注册过滤器
- 无需修改原框架代码
- 可通过 `INSTALLED_APPS` 控制启用/禁用

---

#### `engine.py` - 规则引擎

**核心类**：`RuleEngine`

**主要方法**：
- `apply_rules()` - 应用规则列表，返回组合的 Q 对象
- `_build_single_rule()` - 构建单个规则的 Q 对象
- `_resolve_value()` - 解析动态值（current_user, dept_tree等）
- `_build_q_object()` - 根据操作符构建 Q 对象
- `_parse_logic_expression()` - 解析逻辑表达式（AND/OR/括号）

**示例**：
```python
engine = RuleEngine(request, queryset)
q = engine.apply_rules(
    rules=[{"id": 1, "field": "dept_belong_id", "operator": "in", 
            "value_type": "dept_tree", "value": null}],
    logic="1"
)
# 返回：Q(dept_belong_id__in=[3, 31, 32])
```

---

#### `filters.py` - 扩展过滤器

**核心类**：`CustomRuleDataPermissionFilter`

**工作流程**：
1. 检查是否启用（配置开关、用户登录、非超管）
2. 根据当前 API + Method 查找 MenuButton
3. 根据用户角色 + MenuButton 查找自定义规则（data_range=5）
4. 解析 JSON 字符串为字典
5. 调用 RuleEngine 生成 Q 对象
6. 应用到 queryset 并设置标志位

---

#### `views.py` - API 视图

**核心类**：`DataPermissionRuleViewSet`

**提供的接口**：
- `get_field_options()` - 获取模型字段列表
- `get_operator_options()` - 获取操作符列表
- `get_value_type_options()` - 获取值类型列表

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/ext/data_permission/data_permission_rule/get_field_options/` | GET | 获取模型字段列表 |
| `/api/ext/data_permission/data_permission_rule/get_operator_options/` | GET | 获取操作符列表 |
| `/api/ext/data_permission/data_permission_rule/get_value_type_options/` | GET | 获取值类型列表 |

### 数据存储

自定义规则以 **JSON 字符串**格式存储在 `dvadmin_role_menu_button_permission.custom_rules` 字段（TEXT 类型）：

```json
{
  "logic": "(1 OR 2) AND 3",
  "rules": [
    {
      "id": 1,
      "field": "dept_belong_id",
      "operator": "in",
      "value_type": "dept_tree",
      "value": null,
      "label": "本部门及下级数据"
    },
    {
      "id": 2,
      "field": "creator_id",
      "operator": "eq",
      "value_type": "current_user",
      "value": null,
      "label": "我创建的数据"
    },
    {
      "id": 3,
      "field": "park_status",
      "operator": "gte",
      "value_type": "static",
      "value": 2,
      "label": "状态 >= 2"
    }
  ]
}
```

**字段说明**：
- `logic`：逻辑表达式字符串
- `rules`：规则数组
  - `id`：规则编号（必须）
  - `field`：字段名（必须）
  - `operator`：操作符（必须）
  - `value_type`：值类型（必须）
  - `value`：值（static 类型时必须，其他类型可为 null）
  - `label`：规则标签（可选，用于显示）

**数据库字段类型**：
- 字段类型：`TEXT`
- 存储格式：JSON 字符串
- 前端提交：使用 `JSON.stringify()` 转换为字符串
- 后端读取：使用 `json.loads()` 解析为字典

---

## 🎯 工作原理

### 过滤器执行流程

```
用户请求 → CustomPermission（接口权限）
  ↓
CustomRuleDataPermissionFilter（扩展过滤器）
  ├─ 检查 data_range 是否为 5
  ├─ 读取 custom_rules JSON
  ├─ 使用 RuleEngine 解析规则
  ├─ 生成 Q 对象
  ├─ 应用到 queryset
  └─ 设置 request._custom_rule_applied = True
  ↓
DataLevelPermissionsFilter（原框架过滤器）
  └─ 检查 _custom_rule_applied，如果为 True 则跳过
  ↓
返回过滤后的数据
```

### 规则引擎核心

**核心类**：`RuleEngine`（位于 `engine.py`）

```python
class RuleEngine:
    def apply_rules(rules_list, logic_expression):
        # 1. 解析每个规则
        for rule in rules_list:
            field = rule['field']        # 如 "dept_belong_id"
            operator = rule['operator']  # 如 "in"
            value_type = rule['value_type']  # 如 "dept_tree"
            value = rule['value']        # 静态值或 null
            
            # 2. 解析动态值
            actual_value = resolve_value(value_type, value)
            # static → 直接返回 value
            # current_user → 123 (当前用户ID)
            # current_dept → 3 (当前部门ID)
            # dept_tree → [3, 31, 32] (部门树)
            
            # 3. 构建 Q 对象
            q = build_q(field, operator, actual_value)
            # Q(dept_belong_id__in=[3, 31, 32])
        
        # 4. 根据逻辑表达式组合
        parse_logic("(1 OR 2) AND 3", q_dict)
        # 结果：(Q1 | Q2) & Q3
```

**支持的动态值类型**：
- `static` - 固定值（直接使用 value）
- `current_user` - 当前用户ID（`request.user.id`）
- `current_dept` - 当前部门ID（`request.user.dept_id`）
- `current_company` - 当前公司ID（`request.user.company_id`）
- `dept_tree` - 当前部门树（`get_dept(user.dept_id)` 递归获取下级）
- `dynamic` - 动态表达式（高级用法，谨慎使用）

---

## 📝 最佳实践

### 1. 规则命名建议

为规则添加有意义的描述（前端可扩展）：

```json
{
  "id": 1,
  "field": "dept_belong_id",
  "operator": "in",
  "value_type": "dept_tree",
  "value": null,
  "label": "本部门及下级数据"  // 可选
}
```

### 2. 逻辑公式建议

- 简单场景：直接用 `AND` 连接
- 复杂场景：使用括号明确优先级
- 避免过于复杂的嵌套

### 3. 性能优化

- 优先使用索引字段（dept_belong_id, creator等）
- 避免对大文本字段使用 LIKE
- 复杂规则建议在数据库层面建立视图

---

## ⚠️ 注意事项

1. **字段名必须存在**：输入的字段名必须是模型中实际存在的字段，建议从字段列表选择
2. **操作符与值类型匹配**：
   - 使用 `IN` / `NOT IN` 操作符时，值类型应该返回列表（如 `dept_tree`）
   - 使用 `=` / `>` / `<` 等操作符时，值类型应该返回单个值（如 `current_user`、`current_dept`）
3. **逻辑表达式语法**：
   - 必须使用规则ID（数字），如 `1 AND 2`
   - 支持括号、AND、OR（大小写不敏感）
   - 括号必须配对
4. **权限隔离**：不同角色、不同按钮可以配置不同的规则
5. **向后兼容**：原有的 0-4 数据权限范围仍然有效
6. **数据库字段类型**：`custom_rules` 是 TEXT 类型，存储 JSON 字符串

---

## 🐛 故障排查

### 问题1：API 404

**症状**：前端请求 `/api/ext/data_permission/...` 返回 404

**原因**：
- 后端服务未重启
- 扩展模块未加载
- URL 配置错误

**解决**：
1. 检查 `settings.py` 的 `INSTALLED_APPS` 是否包含 `'dvadmin_extensions.data_permission'`
2. 检查 `urls.py` 是否包含扩展路由
3. 重启后端服务
4. 查看日志确认扩展模块已加载

---

### 问题2：保存后不生效

**症状**：配置了自定义规则，但数据仍然显示所有记录

**原因**：
1. `custom_rules` 字段未添加到数据库
2. 过滤器未注册
3. 规则配置有错误（字段名错误、逻辑表达式错误）

**解决**：
1. 执行 SQL 添加字段或运行迁移（见上文"执行数据库迁移"）
2. 检查后端日志，查看是否有错误信息
3. 检查规则配置是否正确（字段名、操作符、值类型匹配）
4. 确认 `data_range` 是否设置为 `5`

---

### 问题3：TypeError: 'int' object is not iterable

**症状**：后端报错 `'int' object is not iterable`

**原因**：操作符与值类型不匹配
- 使用了 `IN` 操作符，但值类型返回的是单个值（如 `current_dept`）

**解决**：
- 方案1：改操作符为 `等于 (=)`
- 方案2：改值类型为 `当前部门树`（返回列表）

**正确组合**：
```
✅ field="dept_belong_id", operator="in", value_type="dept_tree"
✅ field="dept_belong_id", operator="eq", value_type="current_dept"
❌ field="dept_belong_id", operator="in", value_type="current_dept"  // 错误！
```

---

### 问题4：FieldError: Cannot resolve keyword 'xxx' into field

**症状**：后端报错字段不存在

**原因**：
- 字段名拼写错误（如 `dep_belong_id` 应该是 `dept_belong_id`）
- 字段确实不存在于模型中

**解决**：
1. 检查字段名拼写
2. 查看模型定义，确认字段名称
3. 使用"获取字段选项" API 查看可用字段
4. 在前端使用字段输入框的自动补全功能

---

### 问题5：规则配置丢失

**症状**：刷新页面后规则配置消失

**原因**：
- 前端没有正确保存（点击了取消）
- 后端保存失败但前端没有提示
- `role_menu_btn_perm_id` 为空或为 0

**解决**：
1. 确保点击"确定"按钮保存
2. 查看浏览器控制台是否有错误
3. 确保先勾选按钮，再配置数据权限
4. 检查后端日志确认是否保存成功

---

## 📚 扩展开发指南

### 添加新的值类型

**步骤1**：编辑 `engine.py` 的 `_resolve_value()` 方法

```python
def _resolve_value(self, value_type: str, static_value: Any) -> Any:
    # 添加新的值类型
    if value_type == 'last_30_days':
        from datetime import datetime, timedelta
        return datetime.now() - timedelta(days=30)
    
    # ... 其他值类型
```

**步骤2**：更新 `RuleValidator.VALID_VALUE_TYPES` 列表

```python
VALID_VALUE_TYPES = [
    'static', 'current_user', 'current_dept', 'current_company',
    'dept_tree', 'dynamic',
    'last_30_days'  # ← 添加新值类型
]
```

**步骤3**：在 `views.py` 的 `get_value_type_options()` 中添加选项

```python
{
    "value": "last_30_days",
    "label": "最近30天 - 30天前的日期时间",
    "description": "30天前的日期时间",
    "need_input": False
}
```

---

### 添加新的操作符

**步骤1**：编辑 `engine.py` 的 `_build_q_object()` 方法

```python
def _build_q_object(self, field: str, operator: str, value: Any) -> Q:
    operator_map = {
        # ... 现有操作符 ...
        'year_eq': '__year',  # 年份相等
        'month_eq': '__month',  # 月份相等
    }
    
    lookup = operator_map.get(operator, '')
    field_lookup = f"{field}{lookup}"
    
    return Q(**{field_lookup: value})
```

**步骤2**：更新 `RuleValidator.VALID_OPERATORS` 列表

```python
VALID_OPERATORS = [
    'eq', 'ne', 'gt', 'gte', 'lt', 'lte',
    'in', 'not_in', 'contains', 'icontains',
    'startswith', 'endswith', 'isnull', 'isnotnull',
    'regex', 'iregex',
    'year_eq', 'month_eq'  # ← 添加新操作符
]
```

**步骤3**：在 `views.py` 的 `get_operator_options()` 中添加选项

```python
{"value": "year_eq", "label": "年份等于", "description": "日期字段的年份匹配"},
{"value": "month_eq", "label": "月份等于", "description": "日期字段的月份匹配"},
```

---

## 📁 完整文件清单

### 原框架修改（4个文件）

| 文件路径 | 修改内容 | 修改类型 |
|---------|---------|---------|
| `backend/dvadmin/system/models.py` | `RoleMenuButtonPermission` 添加 `custom_rules` 字段和选项 | 扩展字段 |
| `backend/dvadmin/utils/filters.py` | `DataLevelPermissionsFilter` 集成扩展过滤器检查 | 集成代码 |
| `backend/application/settings.py` | 注册扩展应用到 `INSTALLED_APPS` | 配置 |
| `backend/application/urls.py` | 注册扩展路由到 `Extension_Urls` | 路由 |

### 扩展模块（新增7个文件）

| 文件路径 | 说明 | 代码行数 |
|---------|------|---------|
| `backend/dvadmin_extensions/__init__.py` | 扩展包初始化 | ~10 |
| `backend/dvadmin_extensions/data_permission/__init__.py` | 模块初始化，指定 AppConfig | ~20 |
| `backend/dvadmin_extensions/data_permission/apps.py` | 应用配置，自动注册过滤器 | ~40 |
| `backend/dvadmin_extensions/data_permission/engine.py` | 规则引擎核心（解析、组合） | ~500 |
| `backend/dvadmin_extensions/data_permission/filters.py` | 扩展过滤器（应用规则） | ~200 |
| `backend/dvadmin_extensions/data_permission/views.py` | API 视图（字段/操作符/值类型） | ~200 |
| `backend/dvadmin_extensions/data_permission/serializers.py` | 序列化器 | ~120 |
| `backend/dvadmin_extensions/data_permission/urls.py` | 路由配置 | ~15 |
| `backend/dvadmin_extensions/data_permission/README.md` | 本文档 | ~900 |

### 前端修改（3个文件）

| 文件路径 | 修改内容 | 修改类型 |
|---------|---------|---------|
| `web/src/views/system/role/types.ts` | 添加 `CustomRulesConfig`、`RuleItem` 等类型 | 新增类型 |
| `web/src/views/system/role/components/api.ts` | 添加扩展 API 函数（字段/操作符/值类型） | 新增函数 |
| `web/src/views/system/role/components/RoleMenuBtn.vue` | 集成自定义规则构建器，处理保存逻辑 | 扩展功能 |
| `web/src/views/system/role/components/CustomRuleBuilder.vue` | 规则构建器组件（新文件） | ~360 |

---

## 📞 技术支持

### 模块信息
- **模块路径**：`backend/dvadmin_extensions/data_permission/`
- **前端组件**：`web/src/views/system/role/components/CustomRuleBuilder.vue`
- **API 路由前缀**：`/api/ext/data_permission/`
- **创建日期**：2025-10-28
- **最后更新**：2025-10-29
- **版本**：1.0.1

### 依赖的原框架功能
- `dvadmin.utils.filters.get_dept()` - 递归获取部门树
- `dvadmin.utils.filters.DataLevelPermissionsFilter` - 原数据权限过滤器
- `dvadmin.utils.viewset.CustomModelViewSet` - ViewSet 基类及过滤器注册机制
- `dvadmin.system.models.RoleMenuButtonPermission` - 权限配置模型
- `dvadmin.system.models.MenuButton` - 菜单按钮模型

### 常见问题快速链接
- [操作符与值类型不匹配](#问题3-typeerror-int-object-is-not-iterable)
- [字段名错误](#问题4-fielderror-cannot-resolve-keyword-xxx-into-field)
- [保存后不生效](#问题2-保存后不生效)
- [如何添加新的值类型](#添加新的值类型)
- [如何添加新的操作符](#添加新的操作符)

---

## 🎉 完成！

现在你的系统支持非常灵活的自定义数据权限配置了！

**核心优势**：
- ✅ **零新表**：复用原框架的 `RoleMenuButtonPermission` 模型
- ✅ **代码分离**：扩展代码独立于原框架，升级无冲突
- ✅ **动态注入**：通过 `apps.py` 自动注册，无需修改原框架
- ✅ **向后兼容**：不影响原有的 0-4 数据权限类型
- ✅ **灵活强大**：支持任意字段、任意操作符、复杂逻辑组合
- ✅ **易于使用**：前端可视化配置，实时 SQL 预览

