from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class OsmNodeWayRelModel(BaseDataModel):
    """
    OSM道路节点关联数据模型
    存储道路与节点的关联关系，包括排序信息
    """
    
    # OSM道路ID
    osm_way_id = models.CharField(
        max_length=50,
        verbose_name="OSM道路ID",
        help_text="OpenStreetMap道路唯一标识",
        db_comment="OSM道路ID"
    )
    
    # OSM节点ID
    osm_node_id = models.CharField(
        max_length=50,
        verbose_name="OSM节点ID",
        help_text="OpenStreetMap节点唯一标识",
        db_comment="OSM节点ID"
    )
    
    # 排序序号
    sort = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="排序序号",
        help_text="节点在道路中的排序序号",
        db_comment="排序序号"
    )

    class Meta:
        db_table = 'osm_nodeway_rel'
        verbose_name = "OSM道路节点关联"
        verbose_name_plural = "OSM道路节点关联"
        ordering = ['osm_way_id', 'sort']

    def __str__(self):
        return f"关联-Way:{self.osm_way_id}-Node:{self.osm_node_id}-Sort:{self.sort}"

    @property
    def relation_display(self):
        """
        获取关联关系显示
        """
        return f"Way({self.osm_way_id}) -> Node({self.osm_node_id})"
