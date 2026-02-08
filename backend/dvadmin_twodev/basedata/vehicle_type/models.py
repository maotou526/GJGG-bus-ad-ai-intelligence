from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX


class VehicleTypeModel(BaseDataModel):
    """
    车型字典
    继承自 BaseDataModel，自动获得通用审计与软删除字段
    """

    company_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="公司编码",
        help_text="公司编码",
    )

    company_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="公司名称",
        help_text="公司名称",
    )

    vehicle_model_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="车型编号",
        help_text="车型编号",
    )

    vehicle_model_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="车型",
        help_text="车型",
    )

    rated_passenger_capacity = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="额定载客量",
        help_text="额定载客量（人）",
    )

    is_purchased_model = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="是否已购车型",
        help_text="是否已购车型：1=是，0=否",
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "vehicle_type"
        verbose_name = "车型字典"
        verbose_name_plural = verbose_name
        ordering = ["vehicle_model_name"]
