'''
Description: 分表管理视图集
Version: 1.0
Author: 王晨
Date: 2025-11-26
LastEditors: 王晨
LastEditTime: 2025-11-26
'''
from datetime import date, datetime
from django.apps import apps
from django.db import connection
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from .serializers import (
    ShardTableInfoSerializer,
    ModelShardingConfigSerializer,
    CreateShardTableSerializer,
    DropShardTableSerializer,
)
from .sharding import ShardingTableManager, ShardingConfig


class TableShardingViewSet(ViewSet):
    """分表管理视图集"""
    
    def _get_model_by_name(self, model_name: str):
        """
        根据模型名称获取模型类
        
        Args:
            model_name: 模型完整路径，如 'dvadmin_twodev.od.od_details.models.OdDetailsModel'
            
        Returns:
            Django模型类
        """
        try:
            # 解析模型路径
            parts = model_name.split('.')
            if len(parts) < 2:
                raise ValueError("模型名称格式错误，应为：app_label.models.ModelName 或 完整路径")
            
            # 尝试两种格式
            # 格式1: app_label.models.ModelName
            if len(parts) == 3 and parts[1] == 'models':
                app_label = parts[0]
                model_class_name = parts[2]
                model = apps.get_model(app_label, model_class_name)
            # 格式2: 完整路径 dvadmin_twodev.od.od_details.models.OdDetailsModel
            elif len(parts) >= 3:
                # 找到 models 的位置
                models_index = None
                for i, part in enumerate(parts):
                    if part == 'models':
                        models_index = i
                        break
                
                if models_index:
                    app_label = '.'.join(parts[:models_index])
                    model_class_name = parts[models_index + 1]
                    model = apps.get_model(app_label, model_class_name)
                else:
                    # 如果没有 models，尝试最后两部分
                    app_label = '.'.join(parts[:-1])
                    model_class_name = parts[-1]
                    model = apps.get_model(app_label, model_class_name)
            else:
                raise ValueError("无法解析模型路径")
            
            return model
        except Exception as e:
            raise ValueError(f"获取模型失败: {str(e)}")
    
    def _get_sharding_config(self, model):
        """获取模型的分表配置"""
        sharding_config = getattr(model, 'sharding_config', None)
        if not sharding_config:
            raise ValueError(f"模型 {model.__name__} 未配置分表（缺少 sharding_config 属性）")
        return ShardingConfig(model, sharding_config)
    
    @action(detail=False, methods=['get'], url_path='list-models')
    def list_models(self, request):
        """
        列出所有配置了分表的模型
        
        返回所有在代码中配置了 sharding_config 的模型信息
        """
        try:
            models_info = []
            
            # 遍历所有已注册的应用
            for app_config in apps.get_app_configs():
                try:
                    # 获取应用下的所有模型
                    for model in app_config.get_models():
                        # 检查是否有分表配置
                        if hasattr(model, 'sharding_config') and model.sharding_config:
                            config = ShardingConfig(model, model.sharding_config)
                            models_info.append({
                                'model_name': f"{model.__module__}.{model.__name__}",
                                'app_label': model._meta.app_label,
                                'base_table': config.get_base_table(),
                                'date_field': config.get_date_field(),
                                'shard_type': config.config['shard_type'],
                                'auto_create': config.config.get('auto_create_table', True),
                            })
                except Exception as e:
                    # 某些应用可能无法获取模型，忽略
                    continue
            
            serializer = ModelShardingConfigSerializer(models_info, many=True)
            return SuccessResponse(data=serializer.data, msg="获取成功")
        except Exception as e:
            return ErrorResponse(msg=f"获取失败: {str(e)}")
    
    @action(detail=False, methods=['get'], url_path='list-shard-tables')
    def list_shard_tables(self, request):
        """
        列出指定模型的所有分表
        
        请求参数:
            - model_name: 模型名称（完整路径），必填
        """
        model_name = request.query_params.get('model_name')
        if not model_name:
            return ErrorResponse(msg="请提供 model_name 参数")
        
        try:
            model = self._get_model_by_name(model_name)
            config = self._get_sharding_config(model)
            manager = ShardingTableManager(config)
            
            tables = manager.list_shard_tables()
            
            # 获取每个表的统计信息
            table_info = []
            for table_name in tables:
                info = manager.get_table_info(table_name)
                table_info.append(info)
            
            serializer = ShardTableInfoSerializer(table_info, many=True)
            return SuccessResponse(data=serializer.data, msg="获取成功")
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"获取失败: {str(e)}")
    
    @action(detail=False, methods=['post'], url_path='create-shard-table')
    def create_shard_table(self, request):
        """
        创建分表
        
        请求参数:
            - model_name: 模型名称（完整路径），必填
            - date: 日期（格式：YYYY-MM-DD），可选，默认当前日期
            - months_ahead: 提前创建的月数（用于批量创建），可选
        """
        serializer = CreateShardTableSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=f"参数错误: {serializer.errors}")
        
        model_name = serializer.validated_data['model_name']
        date_value = serializer.validated_data.get('date')
        months_ahead = serializer.validated_data.get('months_ahead', 0)
        
        try:
            model = self._get_model_by_name(model_name)
            config = self._get_sharding_config(model)
            manager = ShardingTableManager(config)
            
            if months_ahead > 0:
                # 批量创建未来几个月的分表
                results = manager.create_future_tables(months_ahead)
                return SuccessResponse(data=results, msg=f"成功创建 {len(results)} 个分表")
            else:
                # 创建单个分表
                if not date_value:
                    date_value = date.today()
                
                result = manager.create_shard_table(date_value)
                return SuccessResponse(msg=result)
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"创建失败: {str(e)}")
    
    @action(detail=False, methods=['post'], url_path='drop-shard-table')
    def drop_shard_table(self, request):
        """
        删除分表（谨慎使用）
        
        请求参数:
            - model_name: 模型名称（完整路径），必填
            - date: 日期（格式：YYYY-MM-DD），必填
        """
        serializer = DropShardTableSerializer(data=request.data)
        if not serializer.is_valid():
            return ErrorResponse(msg=f"参数错误: {serializer.errors}")
        
        model_name = serializer.validated_data['model_name']
        date_value = serializer.validated_data['date']
        
        try:
            model = self._get_model_by_name(model_name)
            config = self._get_sharding_config(model)
            manager = ShardingTableManager(config)
            
            result = manager.drop_shard_table(date_value)
            return SuccessResponse(msg=result)
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"删除失败: {str(e)}")
    
    @action(detail=False, methods=['get'], url_path='table-info')
    def get_table_info(self, request):
        """
        获取指定分表的详细信息
        
        请求参数:
            - model_name: 模型名称（完整路径），必填
            - date: 日期（格式：YYYY-MM-DD），必填
        """
        model_name = request.query_params.get('model_name')
        date_str = request.query_params.get('date')
        
        if not model_name or not date_str:
            return ErrorResponse(msg="请提供 model_name 和 date 参数")
        
        try:
            date_value = datetime.strptime(date_str, '%Y-%m-%d').date()
            model = self._get_model_by_name(model_name)
            config = self._get_sharding_config(model)
            manager = ShardingTableManager(config)
            
            table_name = config.get_table_name(date_value)
            info = manager.get_table_info(table_name)
            
            serializer = ShardTableInfoSerializer(info)
            return SuccessResponse(data=serializer.data, msg="获取成功")
        except ValueError as e:
            return ErrorResponse(msg=str(e))
        except Exception as e:
            return ErrorResponse(msg=f"获取失败: {str(e)}")
