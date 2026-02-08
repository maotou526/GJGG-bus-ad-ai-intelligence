# scheme/services.py

import json
from django.db import transaction
from typing import Dict, Any, Optional

from dvadmin_twodev.node_workflow.scheme.models import WorkflowSchemeModel
from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel

class WorkflowSchemeService:
    """
    流程模板业务逻辑服务
    """
    
    @staticmethod
    def export_scheme(scheme_code: str) -> Dict[str, Any]:
        """
        导出流程模板
        
        Args:
            scheme_code: 流程模板编码
            
        Returns:
            模板数据字典
        """
        scheme_info = WorkflowSchemeInfoModel.objects.filter(code=scheme_code).first()
        if not scheme_info:
            raise ValueError(f"流程模板不存在: {scheme_code}")
            
        scheme = WorkflowSchemeModel.objects.filter(scheme_info_id=scheme_info.id, type=1).first()
        if not scheme:
            # 尝试获取草稿
            scheme = WorkflowSchemeModel.objects.filter(scheme_info_id=scheme_info.id, type=2).first()
            
        if not scheme:
            raise ValueError(f"找不到可导出的流程内容")
            
        content = scheme.content
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except:
                pass
                
        return {
            'info': {
                'code': scheme_info.code,
                'name': scheme_info.name,
                'category': scheme_info.category,
                'description': scheme_info.description,
                'sort': scheme_info.sort,
            },
            'scheme': {
                'scheme_content': content
            }
        }
    
    @staticmethod
    @transaction.atomic
    def import_scheme(data: Dict[str, Any], user) -> str:
        """
        导入流程模板
        
        Args:
            data: 模板数据
            user: 当前用户
            
        Returns:
            schema_code
        """
        info_data = data.get('info', {})
        scheme_data = data.get('scheme', {})
        
        code = info_data.get('code')
        name = info_data.get('name')
        
        if not code or not name:
            raise ValueError("导入数据格式错误: 缺少code或name")
            
        # 1. 创建或更新SchemeInfo
        info, created = WorkflowSchemeInfoModel.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'category': info_data.get('category', ''),
                'description': info_data.get('description', ''),
                'sort': info_data.get('sort', 0),
                'enabled_mark': 1,
                'creator_id': str(user.id),
                'creator_name': getattr(user, 'name', '') or getattr(user, 'username', '')
            }
        )
        
        # 2. 创建Scheme (类型为草稿/正式? 这里导入后一般设为正式或者草稿)
        # 假设导入为最新正式版
        process_content = scheme_data.get('scheme_content', {})
        if isinstance(process_content, dict):
            process_content = json.dumps(process_content, ensure_ascii=False)
            
        WorkflowSchemeModel.objects.create(
            scheme_info_id=info.id,
            content=process_content,
            type=1, # 正式
            creator_id=str(user.id),
            creator_name=getattr(user, 'name', '') or getattr(user, 'username', '')
        )
        
        return code
