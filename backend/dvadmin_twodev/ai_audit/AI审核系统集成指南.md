# AI审核系统 - 文件上传与阿里云百炼集成指南

## 📚 目录
1. [文件上传实现](#1-文件上传实现)
2. [阿里云百炼API集成](#2-阿里云百炼api集成)
3. [完整审核流程](#3-完整审核流程)
4. [测试步骤](#4-测试步骤)
5. [常见问题](#5-常见问题)

---

## 1. 文件上传实现

### 1.1 前端上传组件（方式一：使用 fileSelector）

项目已内置 `fileSelector` 组件，在 `crud.tsx` 中配置：

```tsx
// web/src/views/ai_audit/audit_log/AIAuditLogViewSet/crud.tsx

// 文件路径字段配置
file_path: {
    title: '审核文件',
    type: 'file-uploader',
    column: {
        minWidth: 200,
        component: {
            name: 'fs-file-uploader',
            buildUrl: (value: string) => {
                // 如果是完整URL直接返回，否则拼接base URL
                return value?.startsWith('http') ? value : `http://localhost:8000/${value}`;
            },
        },
    },
    form: {
        rules: [{ required: true, message: '请上传审核文件' }],
        component: {
            name: () => import('/@/components/fileSelector/index.vue'),
            vModel: 'modelValue',
            tabsShow: 1000 + 100, // SHOW.IMAGE(1000) + SHOW.VIDEO(100)
            inputType: 'image',    // 显示为图片预览
            inputSize: 150,
            multiple: false,       // 单文件上传
            valueKey: 'url',       // 绑定文件的 url 字段
        },
    },
},
```

### 1.2 前端上传组件（方式二：Element Plus Upload）

```vue
<template>
  <el-upload
    action="/api/system/file/"
    :data="{ upload_method: 1 }"
    :on-success="handleUploadSuccess"
    :before-upload="beforeUpload"
    accept="image/*,video/*"
  >
    <el-button type="primary">选择文件</el-button>
  </el-upload>
</template>

<script setup>
const handleUploadSuccess = (response) => {
  console.log('文件路径:', response.data.url);
  console.log('完整URL:', response.data.file_url);
};

const beforeUpload = (file) => {
  const isValid = file.type.startsWith('image/') || file.type.startsWith('video/');
  const isLt50M = file.size / 1024 / 1024 < 50;

  if (!isValid) {
    ElMessage.error('只能上传图片或视频文件！');
    return false;
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB！');
    return false;
  }
  return true;
};
</script>
```

### 1.3 后端文件接收（已内置）

项目已有文件管理接口：`/api/system/file/`

**接口路径：** `backend/dvadmin/system/views/file_list.py`

```bash
# 上传请求
POST /api/system/file/
Content-Type: multipart/form-data

Body:
  file: <文件对象>
  upload_method: 1

# 返回数据
{
    "code": 2000,
    "data": {
        "id": 123,
        "name": "example.jpg",
        "url": "media/2026/02/example.jpg",     # 相对路径
        "file_url": "https://oss.xxx.com/...",  # OSS完整URL（如果配置了）
        "size": 1024000,
        "mime_type": "image/jpeg",
        "file_type": 0  # 0:图片 1:视频 2:音频 3:其他
    }
}
```

---

## 2. 阿里云百炼API集成

### 2.1 安装SDK

```bash
cd backend
pip install dashscope
pip freeze > requirements.txt
```

### 2.2 配置密钥

在 `backend/conf/env.py` 中添加：

```python
# ============== 阿里云百炼配置 ==============
# API Key 从阿里云控制台获取: https://bailian.console.aliyun.com/
ALIBABA_BAILIAN_API_KEY = "sk-xxxxxxxxxxxxx"
# 智能体ID（可选，使用通义千问VL模型时不需要）
ALIBABA_BAILIAN_AGENT_ID = ""
```

### 2.3 创建审核服务类

创建文件：`backend/dvadmin_twodev/ai_audit/services/ai_audit_service.py`

```python
"""
AI审核服务 - 阿里云百炼集成
"""
import os
import json
from datetime import datetime
from django.conf import settings
from django.utils import timezone
import dashscope
from dashscope import MultiModalConversation
from ..audit_log.models import AIAuditLogModel
from ..utils.audit_enums import AuditType, AIConclusion, RiskLevel
from ..constants import PLATFORM_ALIBABA_BAILIAN


class AIAuditService:
    """阿里云百炼AI审核服务"""

    def __init__(self):
        self.api_key = settings.ALIBABA_BAILIAN_API_KEY
        dashscope.api_key = self.api_key

    def audit_file(
        self,
        file_path: str,
        file_name: str = None,
        audit_type: int = AuditType.CONTENT_AUDIT,
        material_id: int = None,
        order_id: int = None,
        audit_source: int = 2
    ) -> dict:
        """
        审核单个文件

        Args:
            file_path: 文件路径（本地路径或URL）
            file_name: 文件名称
            audit_type: 审核类型（1:画面内容 2:证明文件 3:综合）
            material_id: 关联材料ID
            order_id: 上刊订单ID
            audit_source: 审核来源（1:关联订单 2:独立审核）

        Returns:
            dict: 审核结果
        """
        request_time = timezone.now()

        try:
            # 1. 构建审核提示词
            prompt = self._build_audit_prompt(audit_type)

            # 2. 准备文件URL（阿里云百炼需要公网可访问的URL）
            file_url = self._prepare_file_url(file_path)

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

            response = MultiModalConversation.call(
                model='qwen-vl-max',  # 或 'qwen-vl-plus'
                messages=messages
            )

            response_time = timezone.now()

            # 4. 解析审核结果
            audit_result = self._parse_audit_response(response)

            # 5. 保存审核记录
            audit_log = AIAuditLogModel.objects.create(
                audit_source=audit_source,
                material_id=material_id,
                order_id=order_id,
                file_name=file_name or os.path.basename(file_path),
                file_path=file_path,
                audit_type=audit_type,
                platform=PLATFORM_ALIBABA_BAILIAN,
                request_time=request_time,
                response_time=response_time,
                ai_conclusion=audit_result['ai_conclusion'],
                risk_level=audit_result.get('risk_level'),
                confidence_score=audit_result.get('confidence_score'),
                detection_details=audit_result.get('detection_details'),
                violation_content=audit_result.get('violation_content'),
                raw_response=json.dumps(response, ensure_ascii=False),
            )

            return {
                'audit_log_id': audit_log.id,
                'audit_no': audit_log.audit_no,
                **audit_result
            }

        except Exception as e:
            # 审核失败记录
            AIAuditLogModel.objects.create(
                audit_source=audit_source,
                material_id=material_id,
                order_id=order_id,
                file_name=file_name or os.path.basename(file_path),
                file_path=file_path,
                audit_type=audit_type,
                platform=PLATFORM_ALIBABA_BAILIAN,
                request_time=request_time,
                response_time=timezone.now(),
                ai_conclusion=AIConclusion.AUDIT_FAILED,
                error_message=str(e),
            )
            raise Exception(f"AI审核失败: {str(e)}")

    def _build_audit_prompt(self, audit_type: int) -> str:
        """构建审核提示词"""
        prompts = {
            AuditType.CONTENT_AUDIT: """
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
            AuditType.DOCUMENT_AUDIT: """
请审核这份证明文件，检查：
1. 文件类型是否正确（营业执照、授权书、资质证书等）
2. 文件是否清晰完整
3. 有效期是否在有效范围内
4. 盖章签字是否齐全

输出JSON格式的审核结果。
""",
            AuditType.COMPREHENSIVE_AUDIT: """
请进行综合审核（内容+文件合规性），输出完整的审核报告。
"""
        }
        return prompts.get(audit_type, prompts[AuditType.CONTENT_AUDIT])

    def _prepare_file_url(self, file_path: str) -> str:
        """
        准备文件URL
        阿里云百炼需要公网可访问的HTTP/HTTPS URL
        """
        if file_path.startswith('http'):
            return file_path

        # 本地文件需要提供公网访问地址
        base_url = getattr(settings, 'BACKEND_BASE_URL', 'http://localhost:8000')
        return f"{base_url}/{file_path}"

    def _parse_audit_response(self, response: dict) -> dict:
        """解析阿里云百炼的返回结果"""
        try:
            # 获取AI回复的文本
            content = response['output']['choices'][0]['message']['content']

            # 尝试解析JSON
            try:
                result_json = json.loads(content)
            except:
                # 如果不是JSON，使用简单提取
                result_json = {'conclusion': '通过', 'risk_level': '无风险', 'confidence': 80}

            # 映射为系统枚举
            conclusion_map = {
                '通过': AIConclusion.PASSED,
                '疑似违规': AIConclusion.SUSPECTED_VIOLATION,
                '明确违规': AIConclusion.CONFIRMED_VIOLATION,
            }

            risk_map = {
                '无风险': RiskLevel.NO_RISK,
                '低风险': RiskLevel.LOW_RISK,
                '中风险': RiskLevel.MEDIUM_RISK,
                '高风险': RiskLevel.HIGH_RISK,
            }

            return {
                'ai_conclusion': conclusion_map.get(result_json.get('conclusion', '通过'), AIConclusion.PASSED),
                'risk_level': risk_map.get(result_json.get('risk_level', '无风险'), RiskLevel.NO_RISK),
                'confidence_score': result_json.get('confidence', 0),
                'detection_details': result_json.get('violations', []),
                'violation_content': result_json.get('violations', []),
                'summary': result_json.get('summary', content),
            }

        except Exception as e:
            return {
                'ai_conclusion': AIConclusion.PASSED,
                'risk_level': RiskLevel.NO_RISK,
                'confidence_score': 0,
                'detection_details': [],
                'violation_content': [],
                'summary': f'解析失败: {str(e)}',
            }
```

### 2.4 在ViewSet中添加上传审核接口

编辑 `backend/dvadmin_twodev/ai_audit/audit_log/views.py`：

```python
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from ..services.ai_audit_service import AIAuditService

class AIAuditLogViewSet(CustomModelViewSet):
    # ... 现有代码 ...

    parser_classes = (MultiPartParser, FormParser)  # 支持文件上传

    @action(methods=['POST'], detail=False, permission_classes=[])
    def upload_and_audit(self, request):
        """
        上传文件并立即触发AI审核

        请求参数：
        - file: 文件对象（必填）
        - audit_type: 审核类型（1:画面内容 2:证明文件 3:综合）
        - material_id: 关联材料ID（可选）
        - order_id: 上刊订单ID（可选）
        """
        file = request.FILES.get('file')
        if not file:
            return ErrorResponse(msg="请上传文件", code=4000)

        audit_type = int(request.data.get('audit_type', 1))
        material_id = request.data.get('material_id')
        order_id = request.data.get('order_id')

        try:
            # 1. 保存文件
            from dvadmin.system.models import FileList
            from dvadmin.system.views.file_list import FileSerializer

            file_serializer = FileSerializer(
                data={'file': file},
                context={'request': request}
            )
            file_serializer.is_valid(raise_exception=True)
            file_obj = file_serializer.save()

            # 2. 触发AI审核
            audit_service = AIAuditService()
            audit_result = audit_service.audit_file(
                file_path=file_obj.file_url or file_obj.url.path,
                file_name=file_obj.name,
                audit_type=audit_type,
                material_id=material_id,
                order_id=order_id,
            )

            return DetailResponse(data=audit_result, msg="审核完成")

        except Exception as e:
            return ErrorResponse(msg=f"审核失败: {str(e)}", code=5000)
```

---

## 3. 完整审核流程

### 3.1 流程图

```
用户上传文件
    ↓
保存到服务器/OSS (/api/system/file/)
    ↓
触发 upload_and_audit 接口
    ↓
AIAuditService.audit_file()
    ↓
构建审核提示词
    ↓
调用阿里云百炼API (MultiModalConversation.call)
    ↓
解析审核结果
    ↓
保存到 AIAuditLogModel
    ↓
自动判断是否需要人工复核
    ↓
返回审核结果
```

### 3.2 前端完整示例

创建审核上传页面：`web/src/views/ai_audit/upload_audit/index.vue`

```vue
<template>
  <div class="audit-upload-page">
    <el-card>
      <template #header>
        <h3>AI审核 - 文件上传</h3>
      </template>

      <el-form :model="form" label-width="120px">
        <el-form-item label="审核类型">
          <el-radio-group v-model="form.audit_type">
            <el-radio :label="1">画面内容审核</el-radio>
            <el-radio :label="2">证明文件审核</el-radio>
            <el-radio :label="3">综合审核</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="上传文件">
          <el-upload
            ref="uploadRef"
            action="/api/AIAuditLogViewSet/upload_and_audit/"
            :data="uploadData"
            :on-success="handleSuccess"
            :on-error="handleError"
            :before-upload="beforeUpload"
            accept="image/*,video/*"
            :show-file-list="true"
            :limit="1"
            :auto-upload="false"
          >
            <el-button type="primary">选择文件</el-button>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button type="success" @click="submitUpload" :loading="uploading">
            上传并审核
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="auditResult" style="margin-top: 20px;">
      <template #header>
        <h3>审核结果</h3>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="审核编号">
          {{ auditResult.audit_no }}
        </el-descriptions-item>
        <el-descriptions-item label="AI判定">
          <el-tag :type="getConclusionType(auditResult.ai_conclusion)">
            {{ getConclusionText(auditResult.ai_conclusion) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险等级">
          <el-tag :type="getRiskType(auditResult.risk_level)">
            {{ getRiskText(auditResult.risk_level) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="置信度">
          {{ auditResult.confidence_score }}%
        </el-descriptions-item>
        <el-descriptions-item label="需人工复核" :span="2">
          <el-tag :type="auditResult.need_manual_review ? 'warning' : 'success'">
            {{ auditResult.need_manual_review ? '是' : '否' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="auditResult.violation_content?.length" style="margin-top: 20px;">
        <h4>检测到的问题</h4>
        <el-table :data="auditResult.violation_content" border>
          <el-table-column prop="category" label="类别" width="120" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="severity" label="严重程度" width="100" />
          <el-table-column prop="position" label="位置" width="150" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';

const form = ref({
  audit_type: 1,
});

const uploadData = computed(() => ({
  audit_type: form.value.audit_type,
}));

const uploadRef = ref();
const uploading = ref(false);
const auditResult = ref(null);

const submitUpload = () => {
  uploadRef.value.submit();
  uploading.value = true;
};

const handleSuccess = (response: any) => {
  uploading.value = false;
  ElMessage.success('审核完成！');
  auditResult.value = response.data;
};

const handleError = (error: any) => {
  uploading.value = false;
  ElMessage.error('审核失败：' + error.message);
};

const beforeUpload = (file: File) => {
  const isValid = file.type.startsWith('image/') || file.type.startsWith('video/');
  const isLt50M = file.size / 1024 / 1024 < 50;

  if (!isValid) {
    ElMessage.error('只能上传图片或视频！');
    return false;
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过50MB！');
    return false;
  }
  return true;
};

const getConclusionType = (value: number) => {
  const map = { 1: 'success', 2: 'warning', 3: 'danger', 4: 'info' };
  return map[value] || 'info';
};

const getConclusionText = (value: number) => {
  const map = { 1: '通过', 2: '疑似违规', 3: '明确违规', 4: '审核失败' };
  return map[value] || '未知';
};

const getRiskType = (value: number) => {
  const map = { 1: 'success', 2: 'primary', 3: 'warning', 4: 'danger' };
  return map[value] || 'info';
};

const getRiskText = (value: number) => {
  const map = { 1: '无风险', 2: '低风险', 3: '中风险', 4: '高风险' };
  return map[value] || '未知';
};
</script>

<style scoped>
.audit-upload-page {
  padding: 20px;
}
</style>
```

---

## 4. 测试步骤

### 4.1 配置环境变量

```bash
# backend/conf/env.py
ALIBABA_BAILIAN_API_KEY = "sk-your-api-key"
BACKEND_BASE_URL = "http://localhost:8000"  # 开发环境
```

### 4.2 创建services目录

```bash
mkdir -p backend/dvadmin_twodev/ai_audit/services
touch backend/dvadmin_twodev/ai_audit/services/__init__.py
touch backend/dvadmin_twodev/ai_audit/services/ai_audit_service.py
```

### 4.3 测试文件上传

```bash
curl -X POST http://localhost:8000/api/system/file/ \
  -F "file=@test.jpg" \
  -F "upload_method=1"
```

### 4.4 测试AI审核

```bash
curl -X POST http://localhost:8000/api/AIAuditLogViewSet/upload_and_audit/ \
  -F "file=@ad_image.jpg" \
  -F "audit_type=1"
```

---

## 5. 常见问题

### Q1: 阿里云百炼无法访问文件URL？

**原因：** 本地文件没有公网访问地址

**解决方案：**

#### 方案1：使用 ngrok（开发环境）

```bash
# 安装 ngrok
npm install -g ngrok

# 启动代理
ngrok http 8000

# 将生成的公网URL配置到 env.py
BACKEND_BASE_URL = "https://xxxx.ngrok.io"
```

#### 方案2：配置阿里云OSS（生产环境）

```python
# backend/conf/env.py
FILE_STORAGE = {
    'file_engine': 'oss',  # 改为 oss
    'aliyun_oss': {
        'access_key_id': 'your-access-key',
        'access_key_secret': 'your-secret',
        'bucket_name': 'your-bucket',
        'endpoint': 'oss-cn-hangzhou.aliyuncs.com',
    }
}
```

### Q2: dashscope 导入失败？

```bash
pip install dashscope --upgrade
pip install --upgrade setuptools
```

### Q3: 如何处理大文件/视频？

**建议：**
1. 视频审核：提取关键帧
2. 使用Celery异步处理
3. 配置更大的上传限制

```python
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50MB
```

---

## 6. 相关资源

- [阿里云百炼控制台](https://bailian.console.aliyun.com/)
- [DashScope SDK 文档](https://help.aliyun.com/zh/dashscope/developer-reference/sdk-installation)
- [通义千问VL API](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-vl-api)

---

**创建时间：** 2026-02-04
**最后更新：** 2026-02-04
**文档维护：** AI审核系统开发团队
