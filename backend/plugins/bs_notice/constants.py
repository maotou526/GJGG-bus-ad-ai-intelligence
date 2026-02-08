"""
Description: 消息模板常量
Version: 1.0
Autor: AI Assistant
Date: 2026-02-05
LastEditors: 
LastEditTime: 2026-02-05
"""


class NoticeTemplate:
    """
    消息模板常量
    命名规范：{模块}_{动作}，如 BOOKING_APPROVED
    """
    
    # ==================== 预订管理 ====================
    
    # 预订单提交待审批（通知审批人）
    BOOKING_SUBMITTED = {
        "msg_type": 4,  # 待办
        "priority": 2,
        "title": "{order_no} 预订单待您审批",
        "content": "{submitter_name} 提交的预订单 {order_no}（客户：{customer_name}）待您审批，请及时处理。",
        "jump_url": "/booking/detail?id={order_id}",
    }
    
    # 预订单审批通过（通知创建人）
    BOOKING_APPROVED = {
        "msg_type": 2,  # 业务消息
        "priority": 2,
        "title": "{order_no} 预订单审批通过",
        "content": "您的预订单 {order_no} 已通过审批，客户：{customer_name}，请及时安排上刊。",
        "jump_url": "/booking/detail?id={order_id}",
    }
    
    # 预订单审批驳回（通知创建人）
    BOOKING_REJECTED = {
        "msg_type": 2,
        "priority": 2,
        "title": "{order_no} 预订单审批驳回",
        "content": "您的预订单 {order_no} 审批未通过，驳回原因：{reject_reason}。",
        "jump_url": "/booking/detail?id={order_id}",
    }
    
    # 资源冲突告警（通知媒体部）
    RESOURCE_CONFLICT = {
        "msg_type": 3,  # 告警
        "priority": 1,
        "title": "【资源冲突】{vehicle_no} - {media_type}",
        "content": "车辆 {vehicle_no} 的 {media_type} 资源位在 {date_range} 期间存在预订冲突，请核实处理。",
        "jump_url": "/booking/detail?id={order_id}",
    }
    
    # ==================== 上刊管理 ====================
    
    # 上刊工单自动生成（通知施工人员）
    ON_AIR_CREATED = {
        "msg_type": 4,
        "priority": 1,
        "title": "上刊工单 {order_no} 已生成",
        "content": "预订单 {booking_no} 的上刊工单已自动生成，共 {vehicle_count} 辆车，计划上刊日期：{start_date}，请及时处理。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # 上刊工单分配（通知施工团队）
    ON_AIR_ASSIGNED = {
        "msg_type": 4,
        "priority": 1,
        "title": "上刊工单 {order_no} 已分配",
        "content": "您有新的上刊任务 {order_no}，共 {vehicle_count} 辆车，请及时处理。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # 上刊审批待处理（通知审批人）
    ON_AIR_PENDING_APPROVAL = {
        "msg_type": 4,
        "priority": 2,
        "title": "上刊工单 {order_no} 待审批",
        "content": "上刊工单 {order_no} 的材料已提交，请进行审核。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # 上刊审批通过（通知提交人）
    ON_AIR_APPROVED = {
        "msg_type": 2,
        "priority": 2,
        "title": "上刊工单 {order_no} 审批通过",
        "content": "上刊工单 {order_no} 已通过审批，可以开始施工。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # 上刊审批驳回（通知提交人）
    ON_AIR_REJECTED = {
        "msg_type": 2,
        "priority": 2,
        "title": "上刊工单 {order_no} 审批驳回",
        "content": "上刊工单 {order_no} 审批未通过，驳回原因：{reject_reason}。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # 上刊施工完成待验收（通知验收人员）
    ON_AIR_PENDING_ACCEPTANCE = {
        "msg_type": 4,
        "priority": 2,
        "title": "上刊工单 {order_no} 待验收",
        "content": "施工人员已完成上刊工单 {order_no}，完成 {completed_count}/{total_count} 辆车，请及时验收。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # 上刊施工完成（通知订单创建人）
    ON_AIR_COMPLETED = {
        "msg_type": 2,
        "priority": 2,
        "title": "上刊工单 {order_no} 已完成",
        "content": "上刊工单 {order_no} 施工已全部完成，共 {vehicle_count} 辆车。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # 错车/换车异常告警（通知媒体部）
    ON_AIR_VEHICLE_MISMATCH = {
        "msg_type": 3,
        "priority": 1,
        "title": "【上刊异常】工单 {order_no} 车辆不一致",
        "content": "上刊工单 {order_no} 施工人员上报的车辆（{actual_vehicle}）与预订车辆（{plan_vehicle}）不一致，请审核处理。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # 到期未下刊告警（通知相关人员）
    ON_AIR_EXPIRED_ALERT = {
        "msg_type": 3,
        "priority": 1,
        "title": "【告警】订单 {order_no} 到期未下刊",
        "content": "预订单 {order_no} 已于 {expire_date} 到期，但车辆 {vehicle_no} 的广告仍未下刊，请立即处理。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # ==================== AI审核 ====================
    
    # AI审核完成待复核（通知审核员）
    AI_AUDIT_PENDING_REVIEW = {
        "msg_type": 4,
        "priority": 2,
        "title": "AI审核完成 - {order_no}",
        "content": "上刊订单 {order_no} 的广告画面AI审核已完成，风险等级：{risk_level}，请及时复核。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # AI审核高风险告警（通知媒体部）
    AI_AUDIT_HIGH_RISK = {
        "msg_type": 3,
        "priority": 1,
        "title": "【高风险】{order_no} AI审核发现违规",
        "content": "上刊订单 {order_no} 的广告画面AI审核发现高风险内容：{violation_summary}，请重点关注。",
        "jump_url": "/on-air/detail?id={order_id}",
    }
    
    # ==================== 下刊管理 ====================
    
    # 下刊工单自动生成（通知施工人员）
    OFF_AIR_CREATED = {
        "msg_type": 4,
        "priority": 2,
        "title": "下刊工单 {order_no} 已生成",
        "content": "预订单 {booking_no} 即将于 {end_date} 到期，下刊工单已自动生成，共 {vehicle_count} 辆车，请及时安排下刊。",
        "jump_url": "/off-air/detail?id={order_id}",
    }
    
    # 下刊到期提醒（通知相关人员）
    OFF_AIR_REMIND = {
        "msg_type": 2,
        "priority": 2,
        "title": "{order_no} 下刊日期临近",
        "content": "预订单 {order_no}（客户：{customer_name}）将于 {end_date} 到期下刊，请提前安排。",
        "jump_url": "/off-air/detail?id={order_id}",
    }
    
    # 下刊施工完成待验收（通知验收人员）
    OFF_AIR_PENDING_ACCEPTANCE = {
        "msg_type": 4,
        "priority": 2,
        "title": "下刊工单 {order_no} 待验收",
        "content": "施工人员已完成下刊工单 {order_no}，完成 {completed_count}/{total_count} 辆车，请及时验收。",
        "jump_url": "/off-air/detail?id={order_id}",
    }
    
    # 下刊施工完成（通知订单创建人）
    OFF_AIR_COMPLETED = {
        "msg_type": 2,
        "priority": 2,
        "title": "下刊工单 {order_no} 已完成",
        "content": "下刊工单 {order_no} 施工已全部完成，资源已释放。",
        "jump_url": "/off-air/detail?id={order_id}",
    }
    
    # ==================== 调线审核 ====================
    
    # 车辆调线告警（通知媒体部）
    ROUTE_ADJUSTMENT_ALERT = {
        "msg_type": 3,
        "priority": 1,
        "title": "【调线告警】车辆 {vehicle_no} 发生调线",
        "content": "车辆 {vehicle_no} 从 {old_line} 调整到 {new_line}，影响 {affected_count} 个广告位，请及时处理。",
        "jump_url": "/route-adjustment/detail?id={audit_id}",
    }
    
    # 调线审核待处理（通知负责人）
    ROUTE_ADJUSTMENT_PENDING = {
        "msg_type": 4,
        "priority": 1,
        "title": "调线审核 {audit_no} 待处理",
        "content": "车辆 {vehicle_no} 调线审核待您处理，影响 {affected_count} 个广告位，请选择忽略或重做。",
        "jump_url": "/route-adjustment/detail?id={audit_id}",
    }
    
    # 调线处理完成（通知相关人员）
    ROUTE_ADJUSTMENT_COMPLETED = {
        "msg_type": 2,
        "priority": 2,
        "title": "调线审核 {audit_no} 已完成",
        "content": "车辆 {vehicle_no} 的调线审核已处理完成。",
        "jump_url": "/route-adjustment/detail?id={audit_id}",
    }
    
    # ==================== 系统通知 ====================
    
    # 系统维护通知（全局广播）
    SYSTEM_MAINTENANCE = {
        "msg_type": 1,
        "priority": 1,
        "title": "系统维护通知",
        "content": "系统将于 {start_time} 至 {end_time} 进行维护升级，届时将暂停服务，请提前保存数据。",
        "jump_url": None,
    }
    
    # 系统公告（全局广播）
    SYSTEM_ANNOUNCEMENT = {
        "msg_type": 1,
        "priority": 2,
        "title": "{title}",
        "content": "{content}",
        "jump_url": None,
    }
    
    # ==================== 工具方法 ====================
    
    @staticmethod
    def render(tpl: dict, variables: dict) -> dict:
        """
        渲染模板，替换变量
        
        Args:
            tpl: 模板字典
            variables: 变量字典
            
        Returns:
            渲染后的消息字典
        """
        return {
            "msg_type": tpl["msg_type"],
            "priority": tpl.get("priority", 2),
            "title": tpl["title"].format(**variables),
            "content": tpl.get("content", "").format(**variables) if tpl.get("content") else None,
            "jump_url": tpl.get("jump_url", "").format(**variables) if tpl.get("jump_url") else None,
        }

