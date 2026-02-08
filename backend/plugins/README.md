# dvadmin-flow
1. 插件安装
~~~
1. 把后端插件放到 dvadmin/plugins/ 目录下
2. 把前端插件放到 src/views/plugins/ 目录下
~~~
2. 添加setting.py配置
~~~
from dvadmin3_flow.settings import *            # 审批流组件
~~~
3. 迁移数据库
~~~
python manage.py makemigrations
python manage.py migrate
python manage.py init
~~~
4. 给需要配置审批流的model做继承(演示环境配置的角色管理)
~~~
from dvadmin3_flow.base_model import FlowBaseModel
class Role(CoreModel,FlowBaseModel):
    name = models.CharField(max_length=64, verbose_name="角色名称", help_text="角色名称")
    key = models.CharField(max_length=64, unique=True, verbose_name="权限字符", help_text="权限字符")
    sort = models.IntegerField(default=1, verbose_name="角色顺序", help_text="角色顺序")
    status = models.BooleanField(default=True, verbose_name="角色状态", help_text="角色状态")

    class Meta:
        db_table = table_prefix + "system_role"
        verbose_name = "角色表"
        verbose_name_plural = verbose_name
        ordering = ("sort",)
~~~
5. 配置审批流
~~~
在审批流中配置审批流，并关联到对应的model上，如下图
~~~

# 页面效果图


![输入链接说明](https://bbs.django-vue-admin.com/uploads/20250321/97fbbf29673edfd66a1edd49237791bb.png)

![输入链接说明](https://bbs.django-vue-admin.com/uploads/20250321/c43aa51278cbc478287c718d22397479.png)


![输入链接说明](https://bbs.django-vue-admin.com/uploads/20250321/9732a5cca9c1166d1a65c35e313ab90d.png)


![输入链接说明](https://bbs.django-vue-admin.com/uploads/20250321/3ca9dd0801ce76d21435abcc8a3d505a.png)

![输入链接说明](https://bbs.django-vue-admin.com/uploads/20250321/a87a8d2329ef66880af5b0f16c5ff823.png)