





'''
Description: 
Version: 1.0
Autor: 王晨
Date: 2025-10-27 13:35:15
LastEditors: 王晨
LastEditTime: 2025-10-27 15:19:16
'''

"""
数据库路由器
用于控制不同模型使用不同的数据库

功能说明：
1. 自动路由数据库的读写操作
2. 支持按app配置数据库
3. 支持按模型属性配置数据库
4. 控制跨数据库关联和迁移

使用方式：
方式1：在路由器中配置app使用的数据库
    在 app_db_map 中添加配置，如：
    'dvadmin_twodev.od.od_details': 'dm'

方式2：在模型的Meta类中指定数据库
    class MyModel(CoreModel):
        class Meta:
            db_label = 'dm'  # 指定使用dm数据库

方式3：在查询时手动指定（不推荐）
    MyModel.objects.using('dm').all()
"""
import logging

logger = logging.getLogger(__name__)


class DatabaseRouter:
    """
    多数据库路由器

    根据模型和app标签自动选择正确的数据库进行读写操作
    """

    # 配置哪些app使用哪个数据库
    # 格式：'app_label': 'database_alias'
    app_db_map = {
        # 注意：这里的 key 是 app_label，不是完整的应用路径
        # app_label 是 apps.py 中 name 的最后一部分
        # 例如：'dvadmin_twodev.basedata.park' 的 app_label 是 'park'
        
        # Park 模块路由到达梦数据库
        # 'park': 'dm',
        
        # 示例：其他模块配置
        # 'od_details': 'dm',
        # 'od_device': 'dm',
        # 'poi': 'dm',
        # 'hot_poi': 'dm',
        # 'osm_node': 'dm',
        # 'osm_way': 'dm',
        # 'osm_nodeway_rel': 'dm',
    }

    def db_for_read(self, model, **hints):
        """
        决定从哪个数据库读取数据

        Args:
            model: Django模型类
            **hints: 额外的提示信息

        Returns:
            str: 数据库别名，如 'default', 'dm' 等
        """
        # 优先级1：如果模型有指定 db_label，使用指定的数据库
        if hasattr(model._meta, "db_label"):
            db_label = model._meta.db_label
            logger.debug(
                f"模型 {model.__name__} 通过 db_label 路由到数据库: {db_label}"
            )
            return db_label

        # 优先级2：根据app名称选择数据库
        app_label = model._meta.app_label
        if app_label in self.app_db_map:
            db_name = self.app_db_map[app_label]
            logger.debug(
                f"模型 {model.__name__} (app: {app_label}) 路由到数据库: {db_name}"
            )
            return db_name

        # 优先级3：默认使用 default 数据库
        return "default"

    def db_for_write(self, model, **hints):
        """
        决定向哪个数据库写入数据

        Args:
            model: Django模型类
            **hints: 额外的提示信息

        Returns:
            str: 数据库别名，如 'default', 'dm' 等
        """
        # 写操作使用与读操作相同的逻辑
        if hasattr(model._meta, "db_label"):
            db_label = model._meta.db_label
            logger.debug(f"模型 {model.__name__} 写入操作路由到数据库: {db_label}")
            return db_label

        app_label = model._meta.app_label
        if app_label in self.app_db_map:
            db_name = self.app_db_map[app_label]
            logger.debug(
                f"模型 {model.__name__} (app: {app_label}) 写入操作路由到数据库: {db_name}"
            )
            return db_name

        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        是否允许两个对象之间的关联

        Args:
            obj1: 第一个对象
            obj2: 第二个对象
            **hints: 额外的提示信息

        Returns:
            bool: True表示允许关联，False表示不允许，None表示没有意见
        """
        # 获取两个对象使用的数据库
        db1 = self.db_for_read(obj1.__class__)
        db2 = self.db_for_read(obj2.__class__)

        # 如果两个对象在同一个数据库，允许关联
        if db1 and db2:
            if db1 == db2:
                return True
            else:
                # 允许跨数据库的软关联（db_constraint=False）
                # 主要用于 creator、modifier 等审计字段
                # 这些字段在 CoreModel 中设置了 db_constraint=False
                from dvadmin.system.models import Users
                
                # 如果其中一个是 Users 模型，允许关联（审计字段需要）
                if obj1.__class__ == Users or obj2.__class__ == Users:
                    return True
                
                # 其他情况不允许跨数据库关联
                logger.warning(
                    f"模型 {obj1.__class__.__name__} (db: {db1}) 和 "
                    f"{obj2.__class__.__name__} (db: {db2}) 在不同数据库，不允许关联"
                )
                return False

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        控制迁移在哪个数据库执行

        Args:
            db: 目标数据库别名
            app_label: 应用标签
            model_name: 模型名称（可选）
            **hints: 额外的提示信息

        Returns:
            bool: True表示允许迁移，False表示不允许，None表示没有意见
        """
        # 如果app在映射中，只在指定数据库迁移
        if app_label in self.app_db_map:
            target_db = self.app_db_map[app_label]
            allow = db == target_db
            if model_name:
                logger.debug(
                    f"模型 {model_name} (app: {app_label}) 在数据库 {db} 的迁移: "
                    f"{'允许' if allow else '拒绝'} (目标数据库: {target_db})"
                )
            return allow

        # system、auth等核心应用只在default数据库迁移
        core_apps = [
            "system",  # 系统核心应用
            "auth",  # Django认证
            "contenttypes",  # Django内容类型
            "sessions",  # Django会话
            "admin",  # Django管理后台
            "captcha",  # 验证码
            "django_comment_migrate",  # 注释迁移
        ]

        if app_label in core_apps:
            allow = db == "default"
            logger.debug(
                f"核心应用 {app_label} 在数据库 {db} 的迁移: "
                f"{'允许' if allow else '拒绝'}"
            )
            return allow

        # 其他情况，默认在default数据库迁移
        # 返回None让Django自己决定
        if db == "default":
            return True

        return None