'''
Description: 流程引擎核心类（完整实现版）
Version: 2.0
Author: System
Date: 2026-01-22
LastEditors: Google Antigravity AI
LastEditTime: 2026-01-22
参考: NWFProcessBLL.cs (力软原始实现)
'''
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

# 导入模型
from dvadmin_twodev.node_workflow.scheme.models import WorkflowSchemeModel
from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel
from dvadmin_twodev.node_workflow.process.models import WorkflowProcessModel
from dvadmin_twodev.node_workflow.task.models import WorkflowTaskModel
from dvadmin_twodev.node_workflow.taskrelation.models import WorkflowTaskRelationModel
from dvadmin_twodev.node_workflow.taskmsg.models import WorkflowTaskMsgModel
from dvadmin_twodev.node_workflow.confluence.models import WorkflowConfluenceModel

# 导入用户系统（根据实际项目调整）
try:
    from dvadmin.system.models import Users, Role, Post, Dept
except ImportError:
    Users = None
    Role = None
    Post = None
    Dept = None


class WorkflowEngineConfig:
    """流程引擎配置类"""
    
    def __init__(self):
        self.scheme_content = None  # 流程模板内容
        self.current_user = None  # 当前操作用户
        self.create_user = None  # 流程创建人
        self.process_id = None  # 流程实例ID
        self.task_id = None  # 当前任务ID
        self.auditors = {}  # 手动指定的审核人 {node_id: [user_ids]}
        self.form_data = {} # 业务表单数据
        
        # 委托方法（用于扩展）
        self.db_find_table = None  # 数据库查询委托
        self.get_agree_num = None  # 获取同意数委托
        self.get_disagree_num = None  # 获取不同意数委托
        self.custom_auditor_hooks = {}  # 自定义审核人计算钩子


class WorkflowEngine:
    """
    流程引擎核心类（完整实现）
    
    参考力软NWFProcessBLL.cs实现，包含：
    - bootstrap(): 引擎初始化
    - get_node_auditors(): 计算节点审核人（8种类型）
    - calc_condition(): 计算条件表达式
    - calc_confluence(): 计算会签结果
    """
    
    def __init__(self, config: WorkflowEngineConfig = None):
        """
        初始化流程引擎
        
        Args:
            config: 引擎配置对象
        """
        self.config = config or WorkflowEngineConfig()
        self.nodes_map = {}  # 节点ID到节点信息的映射
        self.state = 0  # 流程状态：0=正常, 1=重新发起, 2=结束
        
        # 如果有流程模板内容，构建节点映射
        if self.config.scheme_content:
            self._build_nodes_map()
    
    def _build_nodes_map(self):
        """构建节点映射字典"""
        scheme_content = self.config.scheme_content
        if isinstance(scheme_content, str):
            scheme_content = json.loads(scheme_content)
        
        for node in scheme_content.get('nodes', []):
            self.nodes_map[node.get('id')] = node
    
    # ==================== 核心方法1: 引擎启动 ====================
    
    @classmethod
    def bootstrap(cls, scheme_code: str = None, process_id: str = None, 
                  task_id: str = None, user=None) -> 'WorkflowEngine':
        """
        流程引擎启动初始化（对应力软_Bootstraper方法）
        
        Args:
            scheme_code: 流程模板编码（创建新流程时使用）
            process_id: 流程实例ID（处理现有流程时使用）
            task_id: 任务ID（审批任务时使用）
            user: 当前用户对象
            
        Returns:
            初始化好的WorkflowEngine实例
            
        Raises:
            ValueError: 参数错误或数据不存在
        """
        config = WorkflowEngineConfig()
        
        # 设置当前用户
        if user:
            config.current_user = {
                'id': str(user.id),
                'account': getattr(user, 'username', ''),
                'name': getattr(user, 'name', '') or getattr(user, 'username', ''),
                'dept_id': str(getattr(user, 'dept_id', '')),
                'company_id': str(getattr(user, 'company_id', ''))
            }
        
        # 场景1: 根据流程编码初始化（创建新流程）
        if scheme_code:
            scheme_info = WorkflowSchemeInfoModel.objects.filter(
                code=scheme_code,
                enabled_mark=1
            ).first()
            
            if not scheme_info:
                raise ValueError(f"流程模板不存在或已禁用: {scheme_code}")
            
            if not scheme_info.scheme_id:
                raise ValueError(f"流程模板未配置启用版本: {scheme_code}")
            
            scheme = WorkflowSchemeModel.objects.filter(
                id=scheme_info.scheme_id,
                type=1  # 正式版本
            ).first()
            
            if not scheme:
                raise ValueError(f"流程模板版本不存在: {scheme_info.scheme_id}")
            
            # 从缓存或数据库加载流程模板内容
            cache_key = f'workflow_scheme_{scheme.id}'
            scheme_content = cache.get(cache_key)
            if not scheme_content:
                scheme_content = json.loads(scheme.content) if isinstance(scheme.content, str) else scheme.content
                cache.set(cache_key, scheme_content, 3600)  # 缓存1小时
            
            config.scheme_content = scheme_content
            
            # 创建流程时，当前用户就是发起人
            if user:
                config.create_user = config.current_user
            
        # 1. 如果有process_id，加载流程实例和模板内容
        if process_id:
            process = WorkflowProcessModel.objects.filter(id=process_id).first()
            if not process:
                raise ValueError(f"流程实例不存在: {process_id}")
            
            config.scheme_code = process.scheme_code
            
            # 设置流程发起人
            if process.creator_id:
                config.create_user = {
                    'id': str(process.creator_id),
                    'name': process.creator_name or ''
                }
            
            # 优先从Redis获取模板内容（TODO）
            # 目前从SchemeModel获取
            scheme = WorkflowSchemeModel.objects.filter(id=process.scheme_id).first()
            if not scheme or not scheme.content:
                scheme_content = {}
                # raise ValueError("流程模板内容为空")
                
            config.scheme_content = json.loads(scheme.content) if scheme.content else {}
            
        # 2. 如果只有scheme_code（创建流程时），加载最新模板
        elif scheme_code:
            scheme_info = WorkflowSchemeInfoModel.objects.filter(code=scheme_code).first()
            if not scheme_info:
                raise ValueError(f"流程模板不存在: {scheme_code}")
                
            scheme = WorkflowSchemeModel.objects.filter(
                id=scheme_info.scheme_id,
                type=1  # 正式版本
            ).first()
            
            if not scheme or not scheme.content:
                scheme_content = {}
                # raise ValueError("流程模板内容为空")
                
            config.scheme_content = json.loads(scheme.content) if scheme.content else {}
            
            # 创建流程时，当前用户就是发起人
            if user:
                config.create_user = config.current_user
            
        else:
            raise ValueError("启动引擎必须提供scheme_code或process_id")
            
        return cls(config)
    
    # ==================== 核心方法2: 节点审核人计算 ====================
    
    def get_node_auditors(self, node_auditor_list: List[Dict], node_info: Dict,
                         prev_node_id: str = None) -> List[Dict]:
        """
        计算节点审核人列表（对应力软_GetNodeAuditors方法）
        
        这是整个流程引擎最核心的方法之一，支持8种审核人类型
        
        Args:
            node_auditor_list: 节点配置的审核人列表
            node_info: 节点信息
            prev_node_id: 上一节点ID（用于历史审核人复用）
            
        Returns:
            审核人列表 [{'id': user_id, 'name': user_name, ...}, ...]
        """
        # 1. 检查是否有历史审核人（节点之前审核过）
        if prev_node_id and self.config.process_id:
            history_auditors = self._get_history_auditors(node_info['id'])
            if history_auditors:
                # 多人审核且配置了复用规则
                is_all_auditor = node_info.get('isAllAuditor', '1')
                auditor_again_type = node_info.get('auditorAgainType', '1')
                
                if is_all_auditor == '2' and auditor_again_type == '1':
                    # 只让未通过的人重新审核
                    return [a for a in history_auditors if a.get('result') != 1]
                else:
                    # 所有历史审核人都重新审核
                    return history_auditors
        
        # 2. 计算新的审核人
        auditors = []
        
        for auditor_config in node_auditor_list:
            # 兼容字符串和数字类型（前端可能传 "8" 或 8）
            auditor_type = auditor_config.get('type')
            try:
                auditor_type = int(auditor_type) if auditor_type is not None else None
            except (ValueError, TypeError):
                auditor_type = None

            # Type 1: 岗位
            if auditor_type == 1:
                auditors.extend(self._get_auditors_by_post(auditor_config))
            
            # Type 2: 角色
            elif auditor_type == 2:
                auditors.extend(self._get_auditors_by_role(auditor_config))
            
            # Type 3: 用户
            elif auditor_type == 3:
                auditors.extend(self._get_auditors_by_user(auditor_config))
            
            # Type 4: 上下级
            elif auditor_type == 4:
                auditors.extend(self._get_auditors_by_level(auditor_config))
            
            # Type 5: 表单字段
            elif auditor_type == 5:
                auditors.extend(self._get_auditors_by_field(auditor_config))
            
            # Type 6: 某节点执行人
            elif auditor_type == 6:
                auditors.extend(self._get_auditors_by_node(auditor_config))
            
            # Type 7: 发起人
            elif auditor_type == 7:
                if self.config.create_user:
                    auditors.append(self.config.create_user)
            
            # Type 8: IOC注入/自定义钩子
            # 根据过滤类型做不同处理（参考力软 NWFProcessBLL.cs 第811-828行）
            elif auditor_type == 8:
                ioc_users = self._get_auditors_by_hook(auditor_config)
                if ioc_users:
                    # 获取过滤类型（从返回结果的 _filter_type 字段获取）
                    filter_type = ioc_users[0].get('_filter_type', 1) if ioc_users else 1

                    if filter_type == 1:
                        # 类型1：替换 - IOC结果直接覆盖之前所有来源
                        auditors = [u for u in ioc_users]
                    elif filter_type == 2:
                        # 类型2：排除 - 从已有列表中移除IOC返回的人
                        ioc_user_ids = {u['id'] for u in ioc_users}
                        auditors = [a for a in auditors if a['id'] not in ioc_user_ids]
                    elif filter_type == 3:
                        # 类型3：合并 - 并集，去重添加
                        existing_ids = {a['id'] for a in auditors}
                        for u in ioc_users:
                            if u['id'] not in existing_ids:
                                auditors.append(u)
                                existing_ids.add(u['id'])

                    # 清理 _filter_type 标记
                    for a in auditors:
                        a.pop('_filter_type', None)
        
        # 3. 去重
        unique_auditors = self._deduplicate_users(auditors)
        
        # 4. 无审核人默认规则
        if not unique_auditors:
            no_people_gz = node_info.get('noPeopleGz', '1')
            if no_people_gz == '3':
                raise ValueError(f"节点 {node_info.get('name')} 没有审核人，无法提交流程")
            
            # 默认使用超级管理员
            unique_auditors = self._get_default_auditors()
        
        return unique_auditors
    
    def _get_history_auditors(self, node_id: str) -> List[Dict]:
        """获取历史审核人（节点之前审核过）"""
        if not self.config.process_id:
            return []
        
        # 查询该节点的历史任务
        task = WorkflowTaskModel.objects.filter(
            process_id=self.config.process_id,
            node_id=node_id,
            is_finished=0  # 未完成
        ).first()
        
        if not task:
            return []
        
        # 查询任务执行人
        task_relations = WorkflowTaskRelationModel.objects.filter(
            task_id=task.id
        )
        
        auditors = []
        for relation in task_relations:
            if Users:
                try:
                    user = Users.objects.get(id=relation.user_id)
                    auditors.append({
                        'id': str(user.id),
                        'name': getattr(user, 'name', '') or getattr(user, 'username', ''),
                        'result': relation.result  # 之前的审批结果
                    })
                except Exception:
                    pass
        
        return auditors
    
    # ==================== 审核人类型1: 岗位 ====================
    
    def _get_auditors_by_post(self, auditor_config: Dict) -> List[Dict]:
        """
        根据岗位获取审核人
        
        支持条件过滤:
        - condition=1: 同部门
        - condition=2: 同公司
        """
        if not Post or not Users:
            return []
        
        post_ids = auditor_config.get('auditorId', '').split(',')
        condition = auditor_config.get('condition', '0')
        
        # 查询岗位下的用户
        users = Users.objects.filter(
            post__id__in=post_ids,
            is_active=True
        ).distinct()
        
        # 条件过滤
        if condition == '1' and self.config.current_user:
            # 同部门
            users = users.filter(dept_id=self.config.current_user.get('dept_id'))
        elif condition == '2' and self.config.current_user:
            # 同公司
            users = users.filter(company_id=self.config.current_user.get('company_id'))
        
        return [self._user_to_dict(u) for u in users]
    
    # ==================== 审核人类型2: 角色 ====================
    
    def _get_auditors_by_role(self, auditor_config: Dict) -> List[Dict]:
        """
        根据角色获取审核人
        
        支持条件过滤:
        - condition=1: 同部门
        - condition=2: 同公司
        - condition=3: 存在上级关系
        - condition=4: 存在下级关系
        """
        if not Role or not Users:
            return []
        
        role_ids = auditor_config.get('auditorId', '').split(',')
        condition = auditor_config.get('condition', '0')
        
        # 查询角色下的用户
        users = Users.objects.filter(
            role__id__in=role_ids,
            is_active=True
        ).distinct()
        
        # 条件过滤
        if condition == '1' and self.config.current_user:
            # 同部门
            users = users.filter(dept_id=self.config.current_user.get('dept_id'))
        elif condition == '2' and self.config.current_user:
            # 同公司
            users = users.filter(company_id=self.config.current_user.get('company_id'))
        elif condition in ['3', '4']:
            # 上下级关系（需要根据实际系统实现）
            # TODO: 实现上下级关系过滤
            pass
        
        return [self._user_to_dict(u) for u in users]
    
    # ==================== 审核人类型3: 用户 ====================
    
    def _get_auditors_by_user(self, auditor_config: Dict) -> List[Dict]:
        """直接指定用户ID列表"""
        if not Users:
            return []
        
        user_ids = auditor_config.get('auditorId', '').split(',')
        users = Users.objects.filter(id__in=user_ids, is_active=True)
        
        return [self._user_to_dict(u) for u in users]
    
    # ==================== 审核人类型4: 上下级 ====================
    
    def _get_auditors_by_level(self, auditor_config: Dict) -> List[Dict]:
        """
        根据岗位层级关系获取审核人
        
        auditorId:
        - 1-5: 向上1-5级
        - 6-10: 向下1-5级
        """
        if not Users or not self.config.current_user:
            return []
        
        level = int(auditor_config.get('auditorId', '0'))
        
        # TODO: 实现岗位层级查询
        # 需要根据实际系统的组织架构实现
        # 这里仅提供框架
        
        return []
    
    # ==================== 审核人类型5: 表单字段 ====================
    
    def _get_auditors_by_field(self, auditor_config: Dict) -> List[Dict]:
        """
        从业务表单字段动态读取审核人
        
        格式: dbId|table|relationId|userId字段
        示例: default|order|process_id|auditor_id
        """
        if not Users:
            return []
        
        field_config = auditor_config.get('auditorId', '')
        parts = field_config.split('|')
        
        if len(parts) < 3:
            return []
        
        db_id = parts[0] if parts[0] else 'default'
        table_name = parts[1]
        relation_field = parts[2] if len(parts) > 2 else 'process_id'
        user_field = parts[3] if len(parts) > 3 else 'user_id'
        
        # 动态查询业务表
        from django.db import connections
        
        user_ids = []
        try:
            with connections[db_id].cursor() as cursor:
                cursor.execute(
                    f"SELECT {user_field} FROM {table_name} WHERE {relation_field} = %s",
                    [self.config.process_id]
                )
                rows = cursor.fetchall()
                user_ids = [str(row[0]) for row in rows if row[0]]
        except Exception as e:
            # 查询失败，返回空列表
            print(f"查询表单字段审核人失败: {e}")
            return []
        
        if not user_ids:
            return []
        
        users = Users.objects.filter(id__in=user_ids, is_active=True)
        return [self._user_to_dict(u) for u in users]
    
    # ==================== 审核人类型6: 某节点执行人 ====================
    
    def _get_auditors_by_node(self, auditor_config: Dict) -> List[Dict]:
        """使用之前某个节点的审核人"""
        if not self.config.process_id:
            return []
        
        target_node_id = auditor_config.get('auditorId', '')
        
        # 查询目标节点的任务日志
        from dvadmin_twodev.node_workflow.tasklog.models import WorkflowTaskLogModel
        
        task_logs = WorkflowTaskLogModel.objects.filter(
            process_id=self.config.process_id,
            node_id=target_node_id
        ).order_by('-create_datetime')
        
        auditors = []
        seen_ids = set()
        
        for log in task_logs:
            if log.task_user_id and log.task_user_id not in seen_ids:
                seen_ids.add(log.task_user_id)
                auditors.append({
                    'id': log.task_user_id,
                    'name': log.task_user_name or ''
                })
        
        return auditors
    
    # ==================== 审核人类型8: IOC注入/自定义钩子 ====================

    def _get_auditors_by_hook(self, auditor_config: Dict) -> List[Dict]:
        """
        通过IOC注入方法计算审核人

        auditorId 格式: "方法名|过滤类型"
        过滤类型:
            1 = 作为审核人来源（直接使用IOC返回的用户）
            2 = 排除这些人员（从已有列表中排除）- 需要外部处理
            3 = 合并人员（与已有列表合并）- 需要外部处理

        参考力软 NWFProcessBLL.cs case 8 的实现
        """
        auditor_id = auditor_config.get('auditorId', '')
        if not auditor_id:
            return []

        # 解析格式: "方法名|过滤类型"
        parts = auditor_id.split('|')
        method_name = parts[0]
        filter_type = int(parts[1]) if len(parts) > 1 else 1

        # 先尝试使用IOC注册表
        try:
            from dvadmin_twodev.node_workflow.ioc import ioc_registry, WfMethodParameter

            if ioc_registry.is_registered(method_name):
                # 构造参数
                params = WfMethodParameter(
                    process_id=self.config.process_id,
                    task_id=self.config.task_id,
                    node_id=None,  # 可从当前上下文获取
                    user_id=self.config.current_user.get('id') if self.config.current_user else None,
                    user_name=self.config.current_user.get('name') if self.config.current_user else None,
                    company_id=self.config.current_user.get('company_id') if self.config.current_user else None,
                    dept_id=self.config.current_user.get('dept_id') if self.config.current_user else None,
                    form_data=self.config.form_data or {},
                    scheme_code=getattr(self.config, 'scheme_code', None),
                    current_users=[],  # 当前已有的审核人（用于过滤类型2、3）
                    extra={}
                )

                # 调用IOC方法获取用户ID
                user_ids = ioc_registry.get_user_ids_by_ioc(method_name, params)

                if not user_ids:
                    return []

                # 查询用户详情
                if not Users:
                    return []

                users = Users.objects.filter(id__in=user_ids, is_active=True)
                result = [self._user_to_dict(u) for u in users]

                # 标记过滤类型，供外部处理
                for r in result:
                    r['_filter_type'] = filter_type

                return result
        except ImportError as e:
            print(f"IOC模块导入失败: {e}")
        except Exception as e:
            print(f"IOC方法调用失败: {e}")

        # 回退到旧的自定义钩子机制
        if method_name in self.config.custom_auditor_hooks:
            hook_func = self.config.custom_auditor_hooks[method_name]
            try:
                return hook_func(self.config.process_id, self.config.current_user)
            except Exception as e:
                print(f"自定义审核人钩子执行失败: {e}")
                return []

        print(f"IOC方法 {method_name} 未注册")
        return []
    
    # ==================== 辅助方法 ====================
    
    def _user_to_dict(self, user) -> Dict:
        """将User对象转换为字典"""
        return {
            'id': str(user.id),
            'account': getattr(user, 'username', ''),
            'name': getattr(user, 'name', '') or getattr(user, 'username', ''),
            'dept_id': str(getattr(user, 'dept_id', '')),
            'company_id': str(getattr(user, 'company_id', ''))
        }
    
    def _deduplicate_users(self, users: List[Dict]) -> List[Dict]:
        """用户去重"""
        seen = set()
        result = []
        for user in users:
            if user['id'] not in seen:
                seen.add(user['id'])
                result.append(user)
        return result
    
    def _get_default_auditors(self) -> List[Dict]:
        """获取默认审核人（超级管理员）"""
        if not Users:
            return []
        
        # 查询超级管理员（is_superuser=True或特定角色）
        admins = Users.objects.filter(is_superuser=True, is_active=True)[:5]
        return [self._user_to_dict(u) for u in admins]
    
    # ==================== 核心方法3: 获取节点信息 ====================
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点信息"""
        return self.nodes_map.get(node_id)
    
    def get_start_node(self) -> Optional[Dict[str, Any]]:
        """获取开始节点"""
        for node in self.nodes_map.values():
            if node.get('type') == 'startround':
                return node
        return None
    
    def get_next_nodes(self, node_id: str, operation_code: str) -> List[Dict[str, Any]]:
        """
        根据当前节点ID和操作码，找到下一节点列表
        
        Args:
            node_id: 当前节点ID
            operation_code: 操作码（agree/disagree/lrtimeout等）
            
        Returns:
            下一节点列表
        """
        next_nodes = []
        scheme_content = self.config.scheme_content
        if isinstance(scheme_content, str):
            scheme_content = json.loads(scheme_content)
        
        lines = scheme_content.get('lines', [])
        
        # 找到从当前节点出发的连线
        for line in lines:
            if line.get('from') == node_id:
                # 判断连线是否符合操作码
                is_ok = False
                strategy = line.get('strategy', '1')
                agree_list = line.get('agreeList', '')
                
                if not strategy or strategy == '1':
                    # 策略1：所有操作都可以通过
                    is_ok = True
                else:
                    # 策略2：需要匹配操作码列表
                    code_list = agree_list.split(',') if agree_list else []
                    if operation_code in code_list:
                        is_ok = True
                
                if is_ok:
                    to_node_id = line.get('to')
                    if to_node_id in self.nodes_map:
                        next_nodes.append(self.nodes_map[to_node_id])
        
        return next_nodes
    
    def get_next_task_nodes(self, begin_node: Dict[str, Any], operation_code: str, 
                           is_get_auditors: bool = False) -> List[Dict[str, Any]]:
        """
        获取接下来的任务节点信息（递归处理条件节点、会签节点等）
        
        Args:
            begin_node: 起始节点
            operation_code: 操作码（agree/disagree）
            is_get_auditors: 是否获取审核人（用于预览）
            
        Returns:
            任务节点列表
        """
        result_nodes = []
        next_nodes = self.get_next_nodes(begin_node.get('id'), operation_code)
        
        for node in next_nodes:
            # 如果手动指定了审核人，覆盖节点配置
            if node.get('id') in self.config.auditors:
                node['auditors'] = [
{
                    'type': 3,  # 用户类型
                    'auditorId': ','.join(self.config.auditors[node.get('id')])
                }]
            
            node_type = node.get('type')
            
            if node_type == 'conditionnode':
                # 条件节点：递归处理
                if not is_get_auditors:
                    condition_result = self.calc_condition(node)
                    if condition_result:
                        result_nodes.extend(self.get_next_task_nodes(node, 'agree', is_get_auditors))
                    else:
                        result_nodes.extend(self.get_next_task_nodes(node, 'disagree', is_get_auditors))
                else:
                    # 获取审核人时，返回所有分支
                    result_nodes.extend(self.get_next_task_nodes(node, 'agree', is_get_auditors))
                    result_nodes.extend(self.get_next_task_nodes(node, 'disagree', is_get_auditors))
            
            elif node_type == 'confluencenode':
                # 会签节点
                if not is_get_auditors:
                    confluence_res = self.calc_confluence(node, begin_node.get('id'), operation_code == 'agree')
                    node['confluenceRes'] = confluence_res
                    if confluence_res == 1:
                        result_nodes.extend(self.get_next_task_nodes(node, 'agree', False))
                    elif confluence_res == -1:
                        result_nodes.extend(self.get_next_task_nodes(node, 'disagree', False))
                    result_nodes.append(node)
                else:
                    result_nodes.append(node)
            
            elif node_type == 'auditornode':
                # 传阅节点
                result_nodes.append(node)
            
            elif node_type == 'childwfnode':
                # 子流程节点
                result_nodes.append(node)
                if node.get('childType') == '2':  # 异步子流程
                    result_nodes.extend(self.get_next_task_nodes(node, 'agree', is_get_auditors))
            
            elif node_type == 'startround':
                # 开始节点：需要重新审核
                result_nodes.append(node)
                self.state = 1  # 重新发起
            
            elif node_type == 'endround':
                # 结束节点
                self.state = 2  # 流程结束
            
            else:
                # 默认：普通审批节点
                result_nodes.append(node)
        
        return result_nodes
    
    # ==================== 核心方法4: 条件计算 ====================
    
    def calc_condition(self, condition_node: Dict[str, Any]) -> bool:
        """
        计算条件节点的条件表达式
        
        支持:
        - 字段比较 (==, !=, >, <, >=, <=)
        - 逻辑运算 (AND, OR, NOT)
        - 从表单数据读取字段值
        
        Args:
            condition_node: 条件节点信息
            
        Returns:
            True表示条件成立，False表示不成立
        """
        # 获取条件表达式
        condition_expr = condition_node.get('condition', '')
        
        if not condition_expr:
            return True
        
        if not self.config.form_data:
            # 如果没有表单数据，默认返回True（避免阻塞），或根据业务需求返回False
            return True
            
        conditions = condition_node.get('conditions', [])
        if not conditions:
            return True
            
        # 默认使用 AND 逻辑
        # 如果需要支持 OR，需读取 conditionLogic 字段
        
        is_match = True
        for cond in conditions:
            field = cond.get('field')
            operator = cond.get('operator') or cond.get('compare') # 兼容字段名
            expect_value = cond.get('value')
            
            if not field or not operator:
                continue
                
            actual_value = self.config.form_data.get(field)
            
            # 类型转换尝试 (数字比较)
            try:
                # 尝试转浮点数比较
                if isinstance(actual_value, (int, float, str)) and str(actual_value).replace('.', '', 1).isdigit():
                     actual_val_num = float(actual_value)
                     expect_val_num = float(expect_value)
                     
                     if operator == '==':
                         if actual_val_num != expect_val_num: is_match = False
                     elif operator == '!=':
                         if actual_val_num == expect_val_num: is_match = False
                     elif operator == '>':
                         if not (actual_val_num > expect_val_num): is_match = False
                     elif operator == '>=':
                         if not (actual_val_num >= expect_val_num): is_match = False
                     elif operator == '<':
                         if not (actual_val_num < expect_val_num): is_match = False
                     elif operator == '<=':
                         if not (actual_val_num <= expect_val_num): is_match = False
                     else:
                         # 未知操作符
                         pass
                else:
                    # 字符串比较
                    actual_str = str(actual_value) if actual_value is not None else ''
                    expect_str = str(expect_value) if expect_value is not None else ''
                    
                    if operator == '==':
                        if actual_str != expect_str: is_match = False
                    elif operator == '!=':
                        if actual_str == expect_str: is_match = False
                    elif operator == 'contains':
                         if expect_str not in actual_str: is_match = False
                    else:
                        # 字符串不支持 > < 等，或者默认 False
                        pass
                        
            except Exception:
                # 转换失败或比较出错，视为不匹配
                is_match = False
                
            if not is_match:
                break
                
        return is_match
    
    # ==================== 核心方法5: 会签计算 ====================
    
    def calc_confluence(self, confluence_node: Dict[str, Any], 
                       form_node_id: str, is_agree: bool) -> int:
        """
        计算会签结果
        
        Args:
            confluence_node: 会签节点
            form_node_id: 表单节点ID（发起会签的节点）
            is_agree: 当前操作是否同意
            
        Returns:
            1=会签通过, -1=会签不通过, 0=会签未完成
        """
        if not self.config.process_id:
            return 0
        
        node_id = confluence_node.get('id')
        
        # 获取该节点最新的任务
        # 注意：如果流程回退，可能会有多个同节点的任务，取最新的一个
        task = WorkflowTaskModel.objects.filter(
            process_id=self.config.process_id,
            node_id=node_id
        ).order_by('-create_datetime').first() # 假设有create_datetime字段，如果没有则用id或time
        
        if not task:
            # 可能是第一次进入，还没创建任务？但calc_confluence通常在审批时调用
            return 0
            
        # 查询任务的所有执行人关系
        relations = WorkflowTaskRelationModel.objects.filter(
            task_id=task.id
        )
        
        if not relations.exists():
            return 0
            
        total_count = relations.count()
        # 结果: 0=未处理, 1=同意, 2=不同意
        agree_count = relations.filter(result=1).count()
        disagree_count = relations.filter(result=2).count()
        processed_count = agree_count + disagree_count
        
        # 还有人未处理 (result=0)
        # 注意：串行会签时，后面的人result=0且mark=1(或0)，总之result=0就是未表态
        if processed_count < total_count:
            # 特殊情况：如果是一票否决，且已经有人不同意，是否提前结束？
            # 规则2: 一票否决
            confluence_gz = confluence_node.get('confluenceGz', '1')
            if confluence_gz == '2' and disagree_count > 0:
                return -1
            return 0
        
        # 获取会签规则
        confluence_gz = confluence_node.get('confluenceGz', '1')
        confluence_percent = int(confluence_node.get('confluencePercent', '100'))
        
        # 规则1: 全部同意
        if confluence_gz == '1':
            if agree_count == total_count:
                return 1
            return -1
        
        # 规则2: 一票否决
        elif confluence_gz == '2':
            if disagree_count > 0:
                return -1
            return 1
        
        # 规则3: 比例规则
        elif confluence_gz == '3':
            if total_count == 0: return -1
            agree_ratio = (agree_count / total_count) * 100
            if agree_ratio >= confluence_percent:
                return 1
            return -1
        
        return 0
    
    # ==================== 辅助方法：节点连接判断 ====================
    
    def is_to_node(self, from_node_id: str, to_node_id: str) -> bool:
        """
        判断两节点是否连接（递归判断）

        Args:
            from_node_id: 起始节点ID
            to_node_id: 目标节点ID

        Returns:
            True表示连接，False表示不连接
        """
        scheme_content = self.config.scheme_content
        if isinstance(scheme_content, str):
            scheme_content = json.loads(scheme_content)

        lines = scheme_content.get('lines', [])
        for line in lines:
            if line.get('from') == from_node_id:
                if line.get('to') == to_node_id:
                    return True
                else:
                    to_node = self.nodes_map.get(line.get('to'))
                    if to_node and to_node.get('type') != 'endround':
                        if self.is_to_node(line.get('to'), to_node_id):
                            return True
        return False

    # ==================== 核心方法6: 连线IOC触发（参考力软_TriggerMethod） ====================

    def get_lines_from_node(self, from_node_id: str, to_node_id: str = None) -> List[Dict[str, Any]]:
        """
        获取从某节点出发的连线

        Args:
            from_node_id: 起始节点ID
            to_node_id: 目标节点ID（可选，用于精确匹配）

        Returns:
            连线配置列表
        """
        scheme_content = self.config.scheme_content
        if isinstance(scheme_content, str):
            scheme_content = json.loads(scheme_content)

        lines = scheme_content.get('lines', [])
        result = []

        for line in lines:
            if line.get('from') == from_node_id:
                if to_node_id is None or line.get('to') == to_node_id:
                    result.append(line)

        return result

    def trigger_line_method(self, line: Dict[str, Any], task_id: str,
                           node_name: str, code: str) -> bool:
        """
        触发连线绑定的方法（参考力软 _TriggerMethod）

        Args:
            line: 连线配置
            task_id: 任务ID
            node_name: 节点名称
            code: 操作码（agree/disagree/create等）

        Returns:
            执行是否成功
        """
        operation_type = line.get('operationType', '')

        if not operation_type:
            return True

        # 只处理 IOC 类型（sql 和 interface 类型暂不实现）
        if operation_type == 'ioc':
            ioc_name = line.get('iocName', '')
            if not ioc_name:
                return True

            return self._execute_ioc_method(ioc_name, task_id, node_name, code)

        elif operation_type == 'sql':
            # SQL类型：执行配置的SQL语句
            # 暂不实现，预留接口
            print(f"[WorkflowEngine] 连线SQL执行暂未实现: {line.get('strSql', '')}")
            return True

        elif operation_type == 'interface':
            # 接口类型：调用外部HTTP接口
            # 暂不实现，预留接口
            print(f"[WorkflowEngine] 连线接口调用暂未实现: {line.get('strInterface', '')}")
            return True

        return True

    def trigger_line_method_before(self, line: Dict[str, Any], task_id: str,
                                   node_name: str, code: str) -> bool:
        """
        触发连线流转前绑定的方法（参考力软 _TriggerMethodBefore）

        使用 iocNameB / strSqlB / strInterfaceB 配置
        """
        operation_type = line.get('operationType', '')

        if not operation_type:
            return True

        if operation_type == 'ioc':
            ioc_name_b = line.get('iocNameB', '')
            if not ioc_name_b:
                return True
            return self._execute_ioc_method(ioc_name_b, task_id, node_name, code)

        return True

    def trigger_line_method_revoke(self, line: Dict[str, Any], task_id: str,
                                   node_name: str) -> bool:
        """
        触发连线撤回时绑定的方法（参考力软 _TriggerMethodR）

        使用 iocNameR / strSqlR / strInterfaceR 配置
        """
        operation_type = line.get('operationType', '')

        if not operation_type:
            return True

        if operation_type == 'ioc':
            ioc_name_r = line.get('iocNameR', '')
            if not ioc_name_r:
                return True
            return self._execute_ioc_method(ioc_name_r, task_id, node_name, 'RevokeAudit')

        return True

    def _execute_ioc_method(self, ioc_name: str, task_id: str,
                           node_name: str, code: str) -> bool:
        """
        执行IOC方法

        Args:
            ioc_name: IOC方法名称
            task_id: 任务ID
            node_name: 节点名称
            code: 操作码

        Returns:
            执行是否成功
        """
        try:
            from dvadmin_twodev.node_workflow.ioc import ioc_registry, WfMethodParameter

            if not ioc_registry.is_registered(ioc_name):
                print(f"[WorkflowEngine] IOC方法未注册: {ioc_name}")
                return True  # 未注册不阻断流程

            # 构造参数（参考力软 WfMethodParameter）
            params = WfMethodParameter(
                process_id=self.config.process_id,
                task_id=task_id,
                node_id=None,
                node_name=node_name,
                user_id=self.config.current_user.get('id') if self.config.current_user else None,
                user_name=self.config.current_user.get('name') if self.config.current_user else None,
                company_id=self.config.current_user.get('company_id') if self.config.current_user else None,
                dept_id=self.config.current_user.get('dept_id') if self.config.current_user else None,
                form_data=self.config.form_data or {},
                scheme_code=getattr(self.config, 'scheme_code', None),
                code=code,
                extra={}
            )

            # 调用IOC方法的execute方法
            result = ioc_registry.execute_method(ioc_name, params)
            print(f"[WorkflowEngine] IOC方法 {ioc_name} 执行完成, 结果: {result}")
            return result

        except ImportError as e:
            print(f"[WorkflowEngine] IOC模块导入失败: {e}")
            return True
        except Exception as e:
            print(f"[WorkflowEngine] IOC方法 {ioc_name} 执行失败: {e}")
            return True  # 执行失败不阻断流程
