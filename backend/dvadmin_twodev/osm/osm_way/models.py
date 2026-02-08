from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class OsmWayModel(BaseDataModel):
    """
    OSM道路数据模型
    存储OpenStreetMap道路信息，包括名称、标签和轨迹
    """
    
    # OSM道路ID
    osm_way_id = models.CharField(
        max_length=50,
        verbose_name="OSM道路ID",
        help_text="OpenStreetMap道路唯一标识",
        db_comment="OSM道路ID"
    )
    
    # 路名名称
    name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="路名名称",
        help_text="道路名称",
        db_comment="路名名称"
    )
    
    # 标签JSON
    tag_json = models.TextField(
        null=True,
        blank=True,
        verbose_name="标签JSON",
        help_text="道路标签数据（JSON格式）",
        db_comment="标签JSON"
    )
    
    # 轨迹坐标串
    str_track = models.TextField(
        null=True,
        blank=True,
        verbose_name="轨迹坐标串",
        help_text="道路轨迹坐标串",
        db_comment="轨迹坐标串"
    )

    class Meta:
        db_table = 'osm_way'
        verbose_name = "OSM道路"
        verbose_name_plural = "OSM道路"
        ordering = ['-create_datetime']

    def __str__(self):
        return f"OSM道路-{self.name or self.osm_way_id}"

    @property
    def name_display(self):
        """
        获取道路名称显示
        """
        return self.name if self.name else f"Way-{self.osm_way_id}"

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

    def get_highway_type(self):
        """
        获取道路类型（从标签中提取highway字段）
        """
        tags = self.get_tags()
        if tags and isinstance(tags, dict):
            return tags.get('highway', None)
        return None
