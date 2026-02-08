# -*- coding: utf-8 -*-
from dvadmin3_flow.decorator import flow_work

from dvadmin.system.models import Users

@flow_work(name="获取结束节点的动态函数",type="end")
def end_function(data,node):
    print("data",data)
    print("结束节点",node)
    return True
@flow_work(name="获取发起人的上级主管",type="approval")
def get_user_superior(data,node):
    print("data",data)
    start_user = data.start_user
    print("发起人",start_user)
    if start_user.name == "A1-1":
        next_user = Users.objects.filter(name="A1").first()
        return [next_user.id]
    if start_user.name == "A10-1":
        next_user = Users.objects.filter(name="A10").first()
        return [next_user.id]
    return [1]