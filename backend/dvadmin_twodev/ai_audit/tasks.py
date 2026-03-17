"""
AI审核Celery异步任务
Description: 将AI审核提交为Celery异步任务，避免大数据量时接口超时
Version: 1.0
Date: 2026-03-17
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name='ai_audit.task_ai_audit_file',
    max_retries=3,
    default_retry_delay=30,
    soft_time_limit=120,
    time_limit=180,
)
def task_ai_audit_file(
    self,
    file_id: str = None,
    file_path: str = None,
    file_name: str = None,
    audit_type: int = 1,
    material_id: str = None,
    order_id: str = None,
    audit_source: int = 2,
    description: str = None,
):
    """
    异步执行AI文件审核

    Args:
        file_id: 附件ID（关联 dvadmin_system_file_list 表）
        file_path: 文件路径（本地路径或URL）
        file_name: 文件名称
        audit_type: 审核类型（1:画面内容 2:证明文件 3:综合）
        material_id: 关联材料ID
        order_id: 上刊订单ID
        audit_source: 审核来源（1:关联订单 2:独立审核）
        description: 备注说明

    Returns:
        dict: 审核结果
    """
    logger.info(f"[AI审核异步] 开始处理任务: file_name={file_name}, task_id={self.request.id}")

    try:
        from .services import AIAuditService

        audit_service = AIAuditService()
        audit_result = audit_service.audit_file(
            file_id=file_id,
            file_path=file_path,
            file_name=file_name,
            file_object=None,  # 异步模式只能使用file_path，无法传递内存中的file_object
            audit_type=audit_type,
            material_id=material_id,
            order_id=order_id,
            audit_source=audit_source,
            description=description,
        )

        logger.info(
            f"[AI审核异步] 任务完成: audit_no={audit_result.get('audit_no')}, "
            f"conclusion={audit_result.get('ai_conclusion')}"
        )

        return audit_result

    except Exception as exc:
        logger.error(f"[AI审核异步] 任务失败: {str(exc)}, 重试次数={self.request.retries}")
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)
        # 超过最大重试次数，记录失败结果
        try:
            from .services import AIAuditService
            service = AIAuditService()
            error_result = service._create_error_result(
                file_id, file_path, file_name, audit_type, material_id, order_id,
                audit_source, timezone.now(), description,
                f"异步任务失败（已重试{self.max_retries}次）: {str(exc)}"
            )
            return error_result
        except Exception:
            logger.exception("[AI审核异步] 创建错误记录也失败了")
            return {'error': str(exc), 'ai_conclusion': 4}


@shared_task(
    bind=True,
    name='ai_audit.task_ai_audit_batch',
    max_retries=1,
    soft_time_limit=600,
    time_limit=720,
)
def task_ai_audit_batch(
    self,
    file_list: list,
    audit_type: int = 1,
    order_id: str = None,
    audit_source: int = 1,
    description: str = None,
):
    """
    批量异步审核多个文件

    Args:
        file_list: 文件列表，每项包含 {file_id, file_path, file_name, material_id}
        audit_type: 审核类型
        order_id: 上刊订单ID
        audit_source: 审核来源
        description: 备注说明

    Returns:
        dict: 批量审核结果汇总
    """
    logger.info(f"[AI审核批量] 开始处理 {len(file_list)} 个文件, task_id={self.request.id}")

    results = []
    success_count = 0
    fail_count = 0

    from .services import AIAuditService
    audit_service = AIAuditService()

    for idx, file_info in enumerate(file_list):
        logger.info(f"[AI审核批量] 处理第 {idx + 1}/{len(file_list)} 个文件: {file_info.get('file_name')}")

        try:
            result = audit_service.audit_file(
                file_id=file_info.get('file_id'),
                file_path=file_info.get('file_path'),
                file_name=file_info.get('file_name'),
                audit_type=audit_type,
                material_id=file_info.get('material_id'),
                order_id=order_id,
                audit_source=audit_source,
                description=description,
            )
            results.append(result)
            if result.get('ai_conclusion') != 4:
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            logger.error(f"[AI审核批量] 文件审核失败: {file_info.get('file_name')}, 错误: {str(e)}")
            fail_count += 1
            results.append({
                'file_name': file_info.get('file_name'),
                'error': str(e),
                'ai_conclusion': 4,
            })

    logger.info(f"[AI审核批量] 全部完成: 成功={success_count}, 失败={fail_count}")

    return {
        'total': len(file_list),
        'success_count': success_count,
        'fail_count': fail_count,
        'results': results,
    }
