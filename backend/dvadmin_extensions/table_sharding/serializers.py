'''
Description: 分表管理序列化器
Version: 1.0
Author: 王晨
Date: 2025-11-26
LastEditors: 王晨
LastEditTime: 2025-11-26
'''
from rest_framework import serializers


class ShardTableInfoSerializer(serializers.Serializer):
    """分表信息序列化器（用于返回分表列表）"""
    table_name = serializers.CharField(help_text="分表名称")
    row_count = serializers.IntegerField(help_text="记录数", required=False, allow_null=True)
    table_size = serializers.CharField(help_text="表大小", required=False, allow_null=True)
    error = serializers.CharField(help_text="错误信息", required=False, allow_null=True)


class ModelShardingConfigSerializer(serializers.Serializer):
    """模型分表配置序列化器"""
    model_name = serializers.CharField(help_text="模型名称（完整路径）")
    app_label = serializers.CharField(help_text="应用标签")
    base_table = serializers.CharField(help_text="基础表名")
    date_field = serializers.CharField(help_text="分表字段")
    shard_type = serializers.CharField(help_text="分表类型（year/month/day）")
    auto_create = serializers.BooleanField(help_text="是否自动创建")


class CreateShardTableSerializer(serializers.Serializer):
    """创建分表请求序列化器"""
    model_name = serializers.CharField(help_text="模型名称（完整路径）", required=True)
    date = serializers.DateField(help_text="日期（格式：YYYY-MM-DD）", required=False)
    months_ahead = serializers.IntegerField(help_text="提前创建的月数（用于批量创建）", required=False, default=0)


class DropShardTableSerializer(serializers.Serializer):
    """删除分表请求序列化器"""
    model_name = serializers.CharField(help_text="模型名称（完整路径）", required=True)
    date = serializers.DateField(help_text="日期（格式：YYYY-MM-DD）", required=True)

