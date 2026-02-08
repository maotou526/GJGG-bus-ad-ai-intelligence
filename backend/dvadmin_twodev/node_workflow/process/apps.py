from django.apps import AppConfig
import logging
import importlib

logger = logging.getLogger(__name__)


class ProcessConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "dvadmin_twodev.node_workflow.process"

    def ready(self):
        """
        应用启动时自动扫描并加载所有模块的IOC方法

        自动扫描所有已安装应用的 ioc.py 文件并导入，触发IOC方法注册
        各业务模块只需创建 ioc.py 文件，无需修改 apps.py
        """
        self._auto_discover_ioc_modules()

    def _auto_discover_ioc_modules(self):
        """
        自动发现并加载所有模块的IOC方法

        扫描 INSTALLED_APPS 中的所有应用，尝试导入其 ioc 模块
        """
        from django.apps import apps
        from dvadmin_twodev.node_workflow.ioc import ioc_registry

        loaded_modules = []

        for app_config in apps.get_app_configs():
            module_name = f"{app_config.name}.ioc"
            try:
                importlib.import_module(module_name)
                loaded_modules.append(app_config.name)
            except ImportError:
                # 该应用没有 ioc.py，跳过
                pass
            except Exception as e:
                logger.warning(f"加载 {module_name} 时出错: {e}")

        registered_methods = ioc_registry.list_all()

        if loaded_modules:
            logger.info(f"已从以下模块加载IOC: {loaded_modules}")

        if registered_methods:
            logger.info(f"已注册的IOC方法: {registered_methods}")
        else:
            logger.info("未发现已注册的IOC方法")
