"""
数据权限规则引擎

负责解析和执行自定义数据权限规则，将 JSON 配置转换为 Django ORM 的 Q 对象。

核心功能：
1. 解析规则配置（字段、操作符、值类型、值）
2. 动态值解析（当前用户、当前部门、部门树等）
3. 逻辑表达式解析（AND、OR、括号）
4. 生成 Django Q 对象
"""
import re
from typing import Dict, List, Any, Optional
from django.db.models import Q
from dvadmin.utils.filters import get_dept
from dvadmin_twodev.basedata.company.models import CompanyModel
import logging

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    数据权限规则引擎
    
    使用示例：
        engine = RuleEngine(request, queryset)
        q_obj = engine.apply_rules(rules_config, logic_expression)
        filtered_queryset = queryset.filter(q_obj)
    """
    
    def __init__(self, request, queryset):
        """
        初始化规则引擎
        
        Args:
            request: Django Request 对象
            queryset: Django QuerySet 对象
        """
        self.request = request
        self.queryset = queryset
        self.user = request.user
        self.model_name = queryset.model.__name__
    
    def apply_rules(self, rules_config: List[dict], logic_expression: str) -> Q:
        """
        应用规则配置
        
        Args:
            rules_config: 规则列表，格式：[
                {
                    "id": 1,
                    "field": "dept_belong_id",
                    "operator": "in",
                    "value_type": "dept_tree",
                    "value": null
                },
                ...
            ]
            logic_expression: 逻辑表达式，如 "(1 OR 2) AND 3"
        
        Returns:
            Django Q 对象
        """
        if not rules_config:
            logger.debug(f"规则配置为空，返回空 Q 对象")
            return Q()
        
        try:
            # 1. 构建每个规则的 Q 对象
            q_dict = {}
            for rule in rules_config:
                rule_id = rule.get('id')
                if rule_id is None:
                    continue
                
                q_obj = self._build_single_rule(rule)
                if q_obj is not None:
                    q_dict[rule_id] = q_obj
            
            logger.debug(f"构建了 {len(q_dict)} 个规则 Q 对象")
            
            # 2. 如果逻辑表达式为空，不使用任何规则（返回空 Q）
            if not logic_expression or not logic_expression.strip():
                logger.debug("逻辑表达式为空，不使用任何规则")
                return Q()
            
            # 3. 根据逻辑表达式组合
            if q_dict:
                final_q = self._parse_logic_expression(logic_expression.strip(), q_dict)
                logger.debug(f"使用逻辑表达式组合: {logic_expression}")
                return final_q
            
            return Q()
        
        except Exception as e:
            logger.error(f"应用规则失败: {e}", exc_info=True)
            return Q()  # 出错时返回空 Q，不影响系统运行
    
    def _build_single_rule(self, rule: dict) -> Optional[Q]:
        """
        构建单个规则的 Q 对象
        
        Args:
            rule: 单个规则配置，格式：
                {
                    "id": 1,
                    "field": "dept_belong_id",
                    "operator": "in",
                    "value_type": "dept_tree",
                    "value": null
                }
        
        Returns:
            Q 对象或 None
        """
        field = rule.get('field')
        operator = rule.get('operator')
        value_type = rule.get('value_type')
        static_value = rule.get('value')
        
        if not field or not operator:
            logger.warning(f"规则配置不完整: {rule}")
            return None
        
        # 1. 解析值
        actual_value = self._resolve_value(value_type, static_value)
        
        # 2. 构建 Q 对象
        q_obj = self._build_q_object(field, operator, actual_value)
        
        logger.debug(f"规则 {rule.get('id')}: {field} {operator} {actual_value}")
        
        return q_obj
    
    def _resolve_value(self, value_type: str, static_value: Any) -> Any:
        """
        解析值类型
        
        Args:
            value_type: 值类型（static, current_user, dept_tree等）
            static_value: 静态值
        
        Returns:
            解析后的实际值
        """
        # 静态值：直接返回
        if value_type == 'static':
            return static_value
        
        # 当前用户ID
        elif value_type == 'current_user':
            return self.user.id
        
        # 当前用户的部门ID
        elif value_type == 'current_dept':
            return getattr(self.user, 'dept_id', None)
        
        # 当前用户的公司ID
        elif value_type == 'current_company':
            # 优先读取 user.company_id，兼容性回退到 user.company_belong_id，并统一为 str
            company_id = getattr(self.user, 'company_id', None) or getattr(self.user, 'company_belong_id', None)
            return str(company_id) if company_id is not None else None
        
        # 当前公司及所有下级公司ID列表
        elif value_type == 'company_tree':
            # 优先读取 user.company_id，兼容性回退到 user.company_belong_id，并统一为 str 列表
            company_id = getattr(self.user, 'company_id', None) or getattr(self.user, 'company_belong_id', None)
            ids = self._get_company_tree_ids(company_id)
            return [str(x) for x in ids]
        
        # 当前部门及所有下级部门ID列表
        elif value_type == 'dept_tree':
            dept_id = getattr(self.user, 'dept_id', None)
            if dept_id:
                return get_dept(dept_id)
            return []
        
        # 动态表达式（谨慎使用）
        elif value_type == 'dynamic':
            return self._eval_dynamic_expression(static_value)
        
        # 默认返回静态值
        return static_value

    def _get_company_tree_ids(self, company_id: Optional[int]) -> List[int]:
        """根据公司ID获取该公司及所有下级公司的ID列表"""
        if not company_id:
            return []
        result_ids: List[int] = []
        queue: List[int] = [company_id]
        while queue:
            # 包含当前层级
            current_ids = list(queue)
            # 加入结果集（去重）
            for cid in current_ids:
                if cid not in result_ids:
                    result_ids.append(cid)
            # 查找下一层子公司
            children = list(
                CompanyModel.objects.filter(parentid__in=current_ids)
                .values_list('id', flat=True)
            )
            # 去重后推进队列
            queue = [cid for cid in children if cid not in result_ids]
        return result_ids
    
    def _eval_dynamic_expression(self, expression: str) -> Any:
        """
        评估动态表达式（安全的 eval）
        
        Args:
            expression: Python 表达式，如 "datetime.now() - timedelta(days=30)"
        
        Returns:
            表达式结果
        """
        try:
            from datetime import datetime, timedelta
            
            # 安全的上下文（只允许特定的函数和对象）
            safe_context = {
                '__builtins__': {},
                'datetime': datetime,
                'timedelta': timedelta,
                'user': self.user,
                'request': self.request,
            }
            
            result = eval(expression, safe_context, {})
            return result
        
        except Exception as e:
            logger.error(f"动态表达式评估失败: {expression}, 错误: {e}")
            return None
    
    def _build_q_object(self, field: str, operator: str, value: Any) -> Q:
        """
        根据字段、操作符、值构建 Django Q 对象
        
        Args:
            field: 字段名，如 "dept_belong_id"
            operator: 操作符，如 "in", "gte", "eq"
            value: 值
        
        Returns:
            Q 对象
        """
        # Django ORM 查询操作符映射
        operator_map = {
            'eq': '',               # 等于
            'ne': '',               # 不等于（用 ~Q 实现）
            'gt': '__gt',           # 大于
            'gte': '__gte',         # 大于等于
            'lt': '__lt',           # 小于
            'lte': '__lte',         # 小于等于
            'in': '__in',           # 包含
            'not_in': '__in',       # 不包含（用 ~Q 实现）
            'contains': '__contains',       # 包含字符串
            'icontains': '__icontains',     # 包含字符串（忽略大小写）
            'startswith': '__startswith',   # 开头匹配
            'endswith': '__endswith',       # 结尾匹配
            'istartswith': '__istartswith', # 开头匹配（忽略大小写）
            'iendswith': '__iendswith',     # 结尾匹配（忽略大小写）
            'isnull': '__isnull',           # 为空
            'regex': '__regex',             # 正则匹配
            'iregex': '__iregex',           # 正则匹配（忽略大小写）
        }
        
        lookup = operator_map.get(operator, '')
        field_lookup = f"{field}{lookup}"

        # 处理 IN 和 NOT_IN：确保 value 是列表（防止字符串被分割）
        if operator in ("in", "not_in"):
            if not isinstance(value, (list, tuple)):
                # 如果 value 是单个值，转换为列表
                value = [value]

        # 针对 CharField 的 *_belong_id 做类型统一（避免 int 与 str 混用导致过滤不到）
        if field in ("company_belong_id", "dept_belong_id"):
            if operator in ("eq", "ne"):
                if value is not None:
                    value = str(value)
            elif operator in ("in", "not_in"):
                # 此时 value 已经是列表了，统一转换为字符串列表
                value = [str(v) for v in value]
        
        # 处理特殊的否定操作符
        if operator == 'ne':
            return ~Q(**{field: value})
        
        elif operator == 'not_in':
            return ~Q(**{f"{field}__in": value})
        
        elif operator == 'isnull':
            # 为空：不关心 value，始终判断为空
            return Q(**{field_lookup: True})
        
        elif operator == 'isnotnull':
            # 不为空：不关心 value，始终判断不为空
            return Q(**{f"{field}__isnull": False})
        
        # 普通操作符
        return Q(**{field_lookup: value})
    
    def _parse_logic_expression(self, expression: str, q_dict: Dict[int, Q]) -> Q:
        """
        解析逻辑表达式，组合多个 Q 对象
        
        Args:
            expression: 逻辑表达式，如 "(1 OR 2) AND 3"
            q_dict: 规则ID到Q对象的映射，如 {1: Q(...), 2: Q(...), 3: Q(...)}
        
        Returns:
            组合后的 Q 对象
        """
        if not expression or not q_dict:
            return Q()
        
        try:
            # 递归处理括号
            return self._evaluate_expression(expression.strip(), q_dict)
        
        except Exception as e:
            logger.error(f"解析逻辑表达式失败: {expression}, 错误: {e}")
            # 出错时默认 AND 组合所有规则
            result = Q()
            for q_obj in q_dict.values():
                result &= q_obj
            return result
    
    def _evaluate_expression(self, expr: str, q_dict: Dict) -> Q:
        """
        递归评估表达式
        
        处理逻辑：
        1. 如果有括号，先处理最内层括号
        2. 评估括号内的表达式
        3. 用临时key替换括号部分
        4. 继续处理外层
        """
        expr = expr.strip()
        
        # 处理括号
        while '(' in expr:
            # 找到最内层的括号
            start = -1
            for i, char in enumerate(expr):
                if char == '(':
                    start = i
                elif char == ')':
                    if start == -1:
                        raise ValueError(f"括号不匹配: {expr}")
                    
                    # 提取括号内的内容
                    inner_expr = expr[start+1:i]
                    
                    # 递归评估括号内的表达式
                    inner_result = self._evaluate_simple_expression(inner_expr, q_dict)
                    
                    # 生成临时 key
                    temp_key = f"TEMP_{id(inner_result)}"
                    q_dict[temp_key] = inner_result
                    
                    # 替换括号部分
                    expr = expr[:start] + temp_key + expr[i+1:]
                    break
        
        # 处理最外层表达式（无括号）
        return self._evaluate_simple_expression(expr, q_dict)
    
    def _evaluate_simple_expression(self, expr: str, q_dict: Dict) -> Q:
        """
        评估简单表达式（无括号）
        
        Args:
            expr: 简单表达式，如 "1 AND 2 OR 3"
            q_dict: 规则字典
        
        Returns:
            Q 对象
        """
        # 分词
        tokens = self._tokenize(expr)
        
        if not tokens:
            return Q()
        
        # 从左到右评估
        result = None
        current_op = None
        
        for token in tokens:
            if token in ['AND', 'OR']:
                current_op = token
            else:
                # 获取 Q 对象
                q_obj = q_dict.get(token)
                
                if q_obj is not None:
                    if result is None:
                        result = q_obj
                    elif current_op == 'AND':
                        result = result & q_obj
                    elif current_op == 'OR':
                        result = result | q_obj
        
        return result if result is not None else Q()
    
    def _tokenize(self, expr: str) -> List:
        """
        分词
        
        Args:
            expr: 表达式，如 "1 AND 2 OR 3"
        
        Returns:
            token 列表，如 [1, 'AND', 2, 'OR', 3]
        """
        tokens = []
        expr = expr.strip().upper()
        
        i = 0
        while i < len(expr):
            # 跳过空格
            if expr[i].isspace():
                i += 1
                continue
            
            # AND
            if expr[i:i+3] == 'AND':
                tokens.append('AND')
                i += 3
            
            # OR
            elif expr[i:i+2] == 'OR':
                tokens.append('OR')
                i += 2
            
            # 数字或临时key
            elif expr[i].isdigit() or expr[i:i+4] == 'TEMP':
                token = ''
                while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                    token += expr[i]
                    i += 1
                
                # 尝试转换为整数
                try:
                    tokens.append(int(token))
                except:
                    tokens.append(token)  # 临时 key
            
            else:
                i += 1
        
        return tokens


class RuleValidator:
    """规则验证器"""
    
    VALID_OPERATORS = [
        'eq', 'ne', 'gt', 'gte', 'lt', 'lte',
        'in', 'not_in', 'contains', 'icontains',
        'startswith', 'endswith', 'isnull', 'isnotnull',
        'regex', 'iregex'
    ]
    
    VALID_VALUE_TYPES = [
        'static', 'current_user', 'current_dept', 'current_company', 'company_tree'
        'dept_tree', 'dynamic'
    ]
    
    @classmethod
    def validate_rules(cls, rules_config: List[dict]) -> tuple[bool, str]:
        """
        验证规则配置
        
        Returns:
            (是否有效, 错误信息)
        """
        if not isinstance(rules_config, list):
            return False, "规则配置必须是列表"
        
        rule_ids = set()
        
        for rule in rules_config:
            # 检查必要字段
            if 'id' not in rule:
                return False, "规则缺少 id 字段"
            
            if 'field' not in rule:
                return False, f"规则 {rule.get('id')} 缺少 field 字段"
            
            if 'operator' not in rule:
                return False, f"规则 {rule.get('id')} 缺少 operator 字段"
            
            # 检查规则ID唯一性
            rule_id = rule.get('id')
            if rule_id in rule_ids:
                return False, f"规则ID重复: {rule_id}"
            rule_ids.add(rule_id)
            
            # 检查操作符有效性
            operator = rule.get('operator')
            if operator not in cls.VALID_OPERATORS:
                return False, f"规则 {rule_id} 的操作符无效: {operator}"
            
            # 检查值类型有效性
            value_type = rule.get('value_type', 'static')
            if value_type not in cls.VALID_VALUE_TYPES:
                return False, f"规则 {rule_id} 的值类型无效: {value_type}"
        
        return True, ""
    
    @classmethod
    def validate_logic_expression(cls, expression: str, rule_ids: set) -> tuple[bool, str]:
        """
        验证逻辑表达式
        
        Args:
            expression: 逻辑表达式
            rule_ids: 规则ID集合
        
        Returns:
            (是否有效, 错误信息)
        """
        if not expression:
            return True, ""  # 空表达式有效（默认AND组合）
        
        # 检查括号匹配
        if expression.count('(') != expression.count(')'):
            return False, "括号不匹配"
        
        # 提取表达式中的所有数字
        expr_rule_ids = set(map(int, re.findall(r'\d+', expression)))
        
        # 检查引用的规则ID是否都存在
        invalid_ids = expr_rule_ids - rule_ids
        if invalid_ids:
            return False, f"表达式引用了不存在的规则ID: {invalid_ids}"
        
        # 检查是否包含所有规则
        unused_ids = rule_ids - expr_rule_ids
        if unused_ids:
            return False, f"以下规则未在表达式中使用: {unused_ids}"
        
        return True, ""

