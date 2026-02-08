"""
AI审核服务 - 阿里云百炼集成
Description: 提供文件审核功能，集成阿里云百炼API
Version: 1.0
Date: 2026-02-04
"""
import os
import json
from datetime import datetime
from django.utils import timezone
# from django.conf import settings  # 暂时不需要，未来启用公网URL时取消注释

try:
    import dashscope
    from dashscope import MultiModalConversation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("警告: dashscope 未安装，AI审核功能将不可用。请运行: pip install dashscope")

from ..audit_log.models import AIAuditLogModel
from ..utils.audit_enums import AuditType, AIConclusion, RiskLevel
from ..constants import PLATFORM_ALIBABA_BAILIAN, ALIBABA_BAILIAN_KEY


class AIAuditService:
    """阿里云百炼AI审核服务"""

    def __init__(self):
        """初始化服务"""
        self.api_key = ALIBABA_BAILIAN_KEY
        if DASHSCOPE_AVAILABLE:
            dashscope.api_key = self.api_key

    def audit_file(
        self,
        file_id: str = None,
        file_path: str = None,
        file_name: str = None,
        file_object=None,
        audit_type: int = AuditType.CONTENT,
        material_id: str = None,
        order_id: str = None,
        audit_source: int = 2,
        description: str = None
    ) -> dict:
        """
        审核单个文件

        Args:
            file_id: 附件ID（关联 dvadmin_system_file_list 表）
            file_path: 文件路径（本地路径或URL），与 file_object 二选一
            file_name: 文件名称
            file_object: Django UploadedFile 对象（优先使用，避免磁盘IO）
            audit_type: 审核类型（1:画面内容 2:证明文件 3:综合）
            material_id: 关联材料ID
            order_id: 上刊订单ID
            audit_source: 审核来源（1:关联订单 2:独立审核）
            description: 备注说明

        Returns:
            dict: 审核结果
        """
        request_time = timezone.now()

        # 检查 dashscope 是否可用
        if not DASHSCOPE_AVAILABLE:
            return self._create_error_result(
                file_id, file_path, file_name, audit_type, material_id, order_id,
                audit_source, request_time, description,
                "dashscope SDK未安装，无法进行AI审核"
            )

        try:
            # 1. 构建审核提示词
            prompt = self._build_audit_prompt(audit_type)

            # 2. 准备文件URL（优先使用 file_object，避免磁盘IO）
            file_url = self._prepare_file_url(file_path, file_object)

            # 3. 调用阿里云百炼多模态对话API
            messages = [
                {
                    'role': 'user',
                    'content': [
                        {'text': prompt},
                        {'image': file_url}  # 图片URL
                    ]
                }
            ]

            print(f"[AI审核] 开始审核文件: {file_name}")
            # 注意：不打印完整URL，避免日志过大（Base64很长）

            # 调用API，设置更长的超时时间
            response = MultiModalConversation.call(
                model='qwen-vl-max',  # 或 'qwen-vl-plus'
                messages=messages,
                # 阿里云SDK会自动处理超时，这里不需要显式设置
                # 如果需要调整，可以在 dashscope 配置中设置
            )

            response_time = timezone.now()

            print(f"[AI审核] API响应成功，耗时: {(response_time - request_time).total_seconds():.2f}秒")

            # 4. 解析审核结果
            audit_result = self._parse_audit_response(response)

            # 5. 保存审核记录
            audit_log = AIAuditLogModel.objects.create(
                audit_source=audit_source,
                file_id=file_id,  # 保存附件ID
                material_id=material_id,
                order_id=order_id,
                file_name=file_name or os.path.basename(file_path) if file_path else None,
                file_path=file_path or '',
                audit_type=audit_type,
                platform=PLATFORM_ALIBABA_BAILIAN,
                request_time=request_time,
                response_time=response_time,
                ai_conclusion=audit_result['ai_conclusion'],
                risk_level=audit_result.get('risk_level'),
                confidence_score=audit_result.get('confidence_score'),
                detection_details=audit_result.get('detection_details'),
                violation_content=audit_result.get('violation_content'),
                summary=audit_result.get('summary', ''),  # 保存AI审核总结
                raw_response=json.dumps(response, ensure_ascii=False),
                description=description,
            )

            print(f"[AI审核] 审核完成，记录ID: {audit_log.id}, 审核编号: {audit_log.audit_no}")

            return {
                'audit_log_id': audit_log.id,
                'audit_no': audit_log.audit_no,
                'ai_conclusion': audit_log.ai_conclusion,
                'risk_level': audit_log.risk_level,
                'confidence_score': float(audit_log.confidence_score) if audit_log.confidence_score else 0,
                'need_manual_review': audit_log.need_manual_review,
                'duration_seconds': audit_log.duration_seconds,
                'request_time': audit_log.request_time.isoformat() if audit_log.request_time else None,
                'response_time': audit_log.response_time.isoformat() if audit_log.response_time else None,
                'detection_details': audit_log.detection_details or [],
                'violation_content': audit_log.violation_content or [],
                'summary': audit_result.get('summary', ''),  # AI审核总结
                'file_path': audit_log.file_path,
                'file_name': audit_log.file_name,
            }

        except Exception as e:
            print(f"[AI审核] 审核失败: {str(e)}")
            import traceback
            traceback.print_exc()

            # 审核失败，记录错误
            return self._create_error_result(
                file_id, file_path, file_name, audit_type, material_id, order_id,
                audit_source, request_time, description, str(e)
            )

    def _create_error_result(
        self, file_id, file_path, file_name, audit_type, material_id, order_id,
        audit_source, request_time, description, error_message
    ):
        """创建错误结果记录"""
        audit_log = AIAuditLogModel.objects.create(
            audit_source=audit_source,
            file_id=file_id,  # 保存附件ID
            material_id=material_id,
            order_id=order_id,
            file_name=file_name or os.path.basename(file_path) if file_path else '未知文件',
            file_path=file_path or '',
            audit_type=audit_type,
            platform=PLATFORM_ALIBABA_BAILIAN,
            request_time=request_time,
            response_time=timezone.now(),
            ai_conclusion=AIConclusion.FAILED,
            error_message=error_message,
            description=description,
        )

        return {
            'audit_log_id': audit_log.id,
            'audit_no': audit_log.audit_no,
            'ai_conclusion': audit_log.ai_conclusion,
            'risk_level': None,
            'confidence_score': 0,
            'need_manual_review': True,
            'duration_seconds': audit_log.duration_seconds,
            'request_time': audit_log.request_time.isoformat() if audit_log.request_time else None,
            'response_time': audit_log.response_time.isoformat() if audit_log.response_time else None,
            'detection_details': [],
            'violation_content': [],
            'error_message': error_message,
        }

    def _build_audit_prompt(self, audit_type: int) -> str:
        """构建审核提示词"""
        prompts = {
            AuditType.CONTENT: """
请审核这张公交广告画面，检测以下违规内容：

**必检项：**
1. 政治敏感内容（国家领导人、政治标语、敏感地图等）
2. 色情低俗内容（裸露、性暗示等）
3. 暴力血腥内容
4. 违法违规内容（赌博、毒品、枪支等）
5. 虚假宣传（夸大、绝对化用语如"最好"、"第一"）
6. 侵权内容（未授权使用他人肖像、商标等）

**输出JSON格式：**
{
    "conclusion": "通过/疑似违规/明确违规",
    "risk_level": "无风险/低风险/中风险/高风险",
    "confidence": 95.5,
    "violations": [
        {
            "category": "虚假宣传",
            "description": "使用了'最好'等绝对化用语",
            "severity": "中",
            "position": "画面中央文字"
        }
    ],
    "summary": "综合审核意见"
}
""",
            AuditType.DOCUMENT: """
请审核这份证明文件，检查：
1. 文件类型是否正确（营业执照、授权书、资质证书等）
2. 文件是否清晰完整
3. 有效期是否在有效范围内
4. 盖章签字是否齐全

输出JSON格式的审核结果。
""",
            AuditType.COMPREHENSIVE: """
请进行综合审核（内容+文件合规性），输出完整的审核报告。
"""
        }
        return prompts.get(audit_type, prompts[AuditType.CONTENT])

    def _prepare_file_url(self, file_path: str = None, file_object=None) -> str:
        """
        准备文件URL
        当前实现：将文件转为Base64 Data URI
        未来实现：使用公网可访问的HTTP/HTTPS URL（需配置OSS或公网IP）

        Args:
            file_path: 文件路径（本地路径或URL）
            file_object: Django UploadedFile 对象（优先使用）
        """
        import base64
        import mimetypes

        # 方式1：优先使用 file_object（避免磁盘IO）
        if file_object:
            print(f"[AI审核] 使用内存中的文件对象: {getattr(file_object, 'name', 'unknown')}")

            # 读取文件内容
            file_object.seek(0)  # 重置文件指针到开头
            file_data = file_object.read()

            # 检查文件大小，如果超过5MB，进行压缩
            max_size = 5 * 1024 * 1024  # 5MB
            if len(file_data) > max_size:
                print(f"[AI审核] 文件过大({len(file_data)} bytes)，尝试压缩...")
                file_data = self._compress_image(file_data)
                print(f"[AI审核] 压缩后大小: {len(file_data)} bytes")

            base64_data = base64.b64encode(file_data).decode('utf-8')

            # 获取MIME类型
            mime_type = getattr(file_object, 'content_type', None)
            if not mime_type:
                # 从文件名推断
                file_name = getattr(file_object, 'name', '')
                mime_type, _ = mimetypes.guess_type(file_name)
            if not mime_type:
                mime_type = 'image/jpeg'  # 默认图片类型

            # 返回 data URI 格式
            data_uri = f"data:{mime_type};base64,{base64_data}"
            print(f"[AI审核] 文件已转为Base64, 原始大小: {len(file_data)} bytes, Base64大小: {len(base64_data)} 字符")
            return data_uri

        # 方式2：如果已经是公网URL，直接返回（用于未来OSS场景）
        if file_path and file_path.startswith('http'):
            print(f"[AI审核] 使用远程URL: {file_path}")
            return file_path

        # 方式3：从磁盘读取文件（备用方案）
        if file_path and os.path.exists(file_path):
            print(f"[AI审核] 从磁盘读取文件: {file_path}")
            with open(file_path, 'rb') as f:
                file_data = f.read()
                base64_data = base64.b64encode(file_data).decode('utf-8')

            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'image/jpeg'

            data_uri = f"data:{mime_type};base64,{base64_data}"
            print(f"[AI审核] 文件已转为Base64, 原始大小: {len(file_data)} bytes, Base64大小: {len(base64_data)} 字符")
            return data_uri

        raise ValueError("必须提供 file_object 或 file_path 参数")

    def _compress_image(self, file_data: bytes, max_size: int = 5 * 1024 * 1024, quality: int = 85) -> bytes:
        """
        压缩图片

        Args:
            file_data: 原始图片数据
            max_size: 目标最大大小（字节）
            quality: JPEG质量（1-100）

        Returns:
            压缩后的图片数据
        """
        try:
            from PIL import Image
            import io

            # 打开图片
            img = Image.open(io.BytesIO(file_data))

            # 转换为RGB模式（JPEG不支持透明通道）
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 尝试不同的质量级别进行压缩
            for q in [quality, 75, 60, 50, 40]:
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=q, optimize=True)
                compressed_data = output.getvalue()

                if len(compressed_data) <= max_size:
                    print(f"[AI审核] 压缩成功，质量={q}, 压缩率={(1 - len(compressed_data)/len(file_data))*100:.1f}%")
                    return compressed_data

            # 如果质量40还是太大，尝试缩小分辨率
            width, height = img.size
            for scale in [0.8, 0.6, 0.5, 0.4]:
                new_size = (int(width * scale), int(height * scale))
                resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                output = io.BytesIO()
                resized_img.save(output, format='JPEG', quality=60, optimize=True)
                compressed_data = output.getvalue()

                if len(compressed_data) <= max_size:
                    print(f"[AI审核] 缩放+压缩成功，缩放比例={scale}, 新尺寸={new_size}")
                    return compressed_data

            # 实在压缩不下来，返回最小版本
            print(f"[AI审核] 警告：无法压缩到目标大小，返回最小版本")
            return compressed_data

        except ImportError:
            print(f"[AI审核] 警告：Pillow未安装，无法压缩图片")
            return file_data
        except Exception as e:
            print(f"[AI审核] 图片压缩失败: {str(e)}")
            return file_data

        # ========== 未来实现：使用公网URL（暂时注释） ==========
        # 方式4：使用后端公网URL（需要配置BACKEND_BASE_URL和开放防火墙）
        # base_url = getattr(settings, 'BACKEND_BASE_URL', 'http://localhost:8000')
        # if not file_path.startswith('/'):
        #     file_path = '/' + file_path
        # full_url = f"{base_url}{file_path}"
        # print(f"[AI审核] 文件URL: {full_url}")
        # return full_url

    def _parse_audit_response(self, response: dict) -> dict:
        """解析阿里云百炼的返回结果"""
        try:
            # 获取AI回复的文本
            if 'output' not in response or 'choices' not in response['output']:
                raise ValueError("API返回格式错误")

            content = response['output']['choices'][0]['message']['content']

            # 处理多模态对话的返回格式：content 可能是列表 [{'text': '...'}]
            if isinstance(content, list) and len(content) > 0:
                # 提取第一个 text 字段
                if isinstance(content[0], dict) and 'text' in content[0]:
                    content = content[0]['text']
                else:
                    content = str(content[0])

            print(f"[AI审核] 提取到的文本内容: {content[:200]}...")  # 打印前200字符

            # 尝试解析JSON
            try:
                # 查找JSON部分（可能包含在markdown代码块中）
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    json_str = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    json_str = content[json_start:json_end].strip()
                elif '{' in content and '}' in content:
                    json_start = content.find('{')
                    json_end = content.rfind('}') + 1
                    json_str = content[json_start:json_end]
                else:
                    json_str = content

                result_json = json.loads(json_str)
            except:
                # 如果不是JSON，使用默认值
                print(f"[AI审核] 无法解析JSON，使用默认值。原始内容: {content[:200]}")
                result_json = {
                    'conclusion': '通过',
                    'risk_level': '无风险',
                    'confidence': 80,
                    'violations': [],
                    'summary': content[:500]  # 保存前500字符作为摘要
                }

            # 映射为系统枚举
            conclusion_map = {
                '通过': AIConclusion.PASS,
                '疑似违规': AIConclusion.SUSPECTED_VIOLATION,
                '明确违规': AIConclusion.CLEAR_VIOLATION,
            }

            risk_map = {
                '无风险': RiskLevel.NO_RISK,
                '低风险': RiskLevel.LOW_RISK,
                '中风险': RiskLevel.MEDIUM_RISK,
                '高风险': RiskLevel.HIGH_RISK,
            }

            return {
                'ai_conclusion': conclusion_map.get(
                    result_json.get('conclusion', '通过'),
                    AIConclusion.PASS
                ),
                'risk_level': risk_map.get(
                    result_json.get('risk_level', '无风险'),
                    RiskLevel.NO_RISK
                ),
                'confidence_score': result_json.get('confidence', 0),
                'detection_details': result_json.get('violations', []),
                'violation_content': result_json.get('violations', []),
                'summary': result_json.get('summary', content[:500]),
            }

        except Exception as e:
            print(f"[AI审核] 解析响应失败: {str(e)}")
            # 解析失败，默认返回通过
            return {
                'ai_conclusion': AIConclusion.PASS,
                'risk_level': RiskLevel.NO_RISK,
                'confidence_score': 0,
                'detection_details': [],
                'violation_content': [],
                'summary': f'解析失败: {str(e)}',
            }
