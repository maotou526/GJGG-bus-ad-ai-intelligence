from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class OsmNodeModel(BaseDataModel):
    """
    OSM节点数据模型
    存储OpenStreetMap节点信息，包括坐标和标签
    """
    
    # OSM节点ID
    osm_node_id = models.CharField(
        max_length=50,
        verbose_name="OSM节点ID",
        help_text="OpenStreetMap节点唯一标识",
        db_comment="OSM节点ID"
    )
    
    # 经度
    str_lon = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="经度",
        help_text="节点经度坐标",
        db_comment="经度"
    )
    
    # 纬度
    str_lat = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name="纬度",
        help_text="节点纬度坐标",
        db_comment="纬度"
    )
    
    # 标签JSON
    tag_json = models.TextField(
        null=True,
        blank=True,
        verbose_name="标签JSON",
        help_text="节点标签数据（JSON格式）",
        db_comment="标签JSON"
    )

    class Meta:
        db_table = 'osm_node'
        verbose_name = "OSM节点"
        verbose_name_plural = "OSM节点"
        ordering = ['-create_datetime']

    def __str__(self):
        return f"OSM节点-{self.osm_node_id}"

    @property
    def coordinate_display(self):
        """
        获取格式化的坐标显示
        """
        if self.str_lon and self.str_lat:
            return f"{self.str_lat}, {self.str_lon}"
        return '-'

    def get_tags(self):
        """
        解析标签JSON
        返回解析后的字典数据
        """
        import json
        if self.tag_json:
            try:
                return json.loads(self.tag_json)
            except json.JSONDecodeError:
                return None
        return None
