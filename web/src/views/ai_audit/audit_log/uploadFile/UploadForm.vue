<!--
 * @Description: AI审核 - 上传表单组件（用于抽屉）
 * @Version: 1.0
 * @Date: 2026-02-04
-->
<template>
	<div class="upload-form-container">
		<el-form ref="formRef" :model="formData" :rules="rules" label-width="100px" label-position="right"
				size="default">

			<el-form-item label="审核类型" prop="audit_type">
				<el-select v-model="formData.audit_type" placeholder="请选择审核类型" style="width: 100%;">
					<el-option label="画面内容审核" :value="1">
						<el-icon>
							<Picture />
						</el-icon>
						<span style="margin-left: 8px;">画面内容审核</span>
					</el-option>
					<el-option label="证明文件审核" :value="2">
						<el-icon>
							<Document />
						</el-icon>
						<span style="margin-left: 8px;">证明文件审核</span>
					</el-option>
					<el-option label="综合审核" :value="3">
						<el-icon>
							<Files />
						</el-icon>
						<span style="margin-left: 8px;">综合审核</span>
					</el-option>
				</el-select>
			</el-form-item>

			<el-form-item label="选择文件" required>
				<div class="upload-container">
					<!-- 文件上传组件（已选文件时隐藏） -->
					<el-upload v-if="!fileInfo.file" ref="uploadRef" :auto-upload="false" :show-file-list="false"
							:on-change="handleFileChange" :before-upload="beforeUpload" :limit="1"
							accept="image/*,video/*" drag>
						<div class="upload-dragger">
							<el-icon class="upload-icon" :size="60">
								<UploadFilled />
							</el-icon>
							<div class="upload-text">
								点击或拖拽文件到此区域上传
							</div>
							<div class="upload-hint">
								支持图片、视频格式，单个文件大小不超过 50MB
							</div>
						</div>
					</el-upload>

					<!-- 文件预览 -->
					<div v-if="fileInfo.file" class="file-preview">
						<el-card shadow="hover">
							<div class="preview-content">
								<!-- 图片预览 -->
								<div v-if="fileInfo.type === 'image'" class="image-preview">
									<el-image :src="fileInfo.preview" :preview-src-list="[fileInfo.preview]"
											fit="contain" style="max-width: 100%; max-height: 200px; cursor: pointer;">
										<template #error>
											<div class="image-error">
												<el-icon>
													<PictureFilled />
												</el-icon>
												<span>加载失败</span>
											</div>
										</template>
									</el-image>
								</div>

								<!-- 视频预览 -->
								<div v-else-if="fileInfo.type === 'video'" class="video-preview">
									<video :src="fileInfo.preview" controls
											style="max-width: 100%; max-height: 200px;"></video>
								</div>

								<!-- 文件信息 -->
								<div class="file-info">
									<el-descriptions :column="2" size="small" border>
										<el-descriptions-item label="文件名">
											{{ fileInfo.name }}
										</el-descriptions-item>
										<el-descriptions-item label="文件大小">
											{{ formatFileSize(fileInfo.size) }}
										</el-descriptions-item>
										<el-descriptions-item label="文件类型">
											{{ fileInfo.file.type }}
										</el-descriptions-item>
										<el-descriptions-item label="上传时间">
											{{ fileInfo.uploadTime }}
										</el-descriptions-item>
									</el-descriptions>

									<div style="margin-top: 12px; text-align: right;">
										<el-button type="danger" size="small" @click="handleRemoveFile">
											<el-icon>
												<Delete />
											</el-icon>
											移除文件
										</el-button>
									</div>
								</div>
							</div>
						</el-card>
					</div>
				</div>
			</el-form-item>

			<el-form-item label="备注" prop="description">
				<el-input v-model="formData.description" type="textarea" :rows="5" resize="none"
						placeholder="请输入备注说明（选填）" maxlength="500" show-word-limit />
			</el-form-item>

		</el-form>

		<!-- 操作按钮（独立于表单外） -->
		<div class="form-actions">
			<el-button type="primary" size="large" :loading="submitLoading" @click="handleSubmit">
				<el-icon v-if="!submitLoading">
					<Check />
				</el-icon>
				{{ submitLoading ? '审核中...' : '提交审核' }}
			</el-button>
			<el-button size="large" @click="handleReset">
				<el-icon>
					<Refresh />
				</el-icon>
				重置
			</el-button>
			<el-button size="large" @click="handleCancel">
				<el-icon>
					<Close />
				</el-icon>
				取消
			</el-button>
		</div>

		<!-- 审核结果对话框 -->
		<el-dialog v-model="resultDialogVisible" title="审核结果" width="700px" :close-on-click-modal="false">
			<div v-if="auditResult" class="audit-result">
				<el-result :icon="getResultIcon(auditResult.ai_conclusion)"
						:title="getResultTitle(auditResult.ai_conclusion)">
					<template #sub-title>
						<div class="result-subtitle">
							<p>审核编号：<el-tag type="info">{{ auditResult.audit_no }}</el-tag></p>
						</div>
					</template>

					<template #extra>
						<el-descriptions :column="2" border size="small">
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
								<el-progress :percentage="auditResult.confidence_score || 0"
										:color="getProgressColor(auditResult.confidence_score)" />
							</el-descriptions-item>
							<el-descriptions-item label="需人工复核">
								<el-tag :type="auditResult.need_manual_review ? 'warning' : 'success'">
									{{ auditResult.need_manual_review ? '是' : '否' }}
								</el-tag>
							</el-descriptions-item>
						</el-descriptions>

						<!-- AI审核总结 -->
						<div v-if="auditResult.summary" style="margin-top: 16px;">
							<el-alert title="AI审核总结" type="info" :closable="false" style="margin-bottom: 12px;" />
							<el-card shadow="never" style="background-color: #f5f7fa;">
								<div style="line-height: 1.8; color: #606266; white-space: pre-wrap;">
									{{ auditResult.summary }}
								</div>
							</el-card>
						</div>

						<!-- 违规内容 -->
						<div v-if="auditResult.violation_content && auditResult.violation_content.length > 0"
								style="margin-top: 16px;">
							<el-alert title="检测到以下问题" type="warning" :closable="false" style="margin-bottom: 12px;" />
							<el-table :data="auditResult.violation_content" border stripe size="small" max-height="200">
								<el-table-column prop="category" label="类别" width="100" />
								<el-table-column prop="description" label="描述" />
								<el-table-column prop="severity" label="严重程度" width="80">
									<template #default="{ row }">
										<el-tag :type="getSeverityType(row.severity)" size="small">
											{{ row.severity }}
										</el-tag>
									</template>
								</el-table-column>
							</el-table>
						</div>
					</template>
				</el-result>
			</div>

			<template #footer>
				<el-button type="primary" @click="handleViewAndClose">完成</el-button>
			</template>
		</el-dialog>
	</div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive } from 'vue';
import { ElMessage, ElMessageBox, FormInstance, FormRules, UploadFile } from 'element-plus';
import {
	UploadFilled, InfoFilled, Folder, EditPen, Check, Refresh, Close,
	Picture, Document, Files, Delete, PictureFilled
} from '@element-plus/icons-vue';
import * as api from './api';

export default defineComponent({
	name: 'UploadForm',
	components: {
		UploadFilled, InfoFilled, Folder, EditPen, Check, Refresh, Close,
		Picture, Document, Files, Delete, PictureFilled
	},
	emits: ['success', 'cancel'],
	setup(props, { emit }) {
		const formRef = ref<FormInstance>();
		const uploadRef = ref();

		// 表单数据
		const formData = reactive({
			audit_source: 2, // 固定为独立审核
			audit_type: 1,
			description: '',
		});

		// 文件信息
		const fileInfo = reactive({
			file: null as File | null,
			name: '',
			size: 0,
			type: '',
			preview: '',
			uploadTime: '',
		});

		// 验证规则
		const rules = reactive<FormRules>({
			audit_type: [
				{ required: true, message: '请选择审核类型', trigger: 'change' }
			],
		});

		const submitLoading = ref(false);
		const resultDialogVisible = ref(false);
		const auditResult = ref<any>(null);

		const handleFileChange = (uploadFile: UploadFile) => {
			const file = uploadFile.raw;
			if (!file) return;

			fileInfo.file = file;
			fileInfo.name = file.name;
			fileInfo.size = file.size;
			fileInfo.type = file.type.startsWith('image/') ? 'image' : 'video';
			fileInfo.uploadTime = new Date().toLocaleString('zh-CN');

			// 使用 createObjectURL 替代 readAsDataURL，避免读取整个文件转base64，预览更快
			if (fileInfo.preview) {
				URL.revokeObjectURL(fileInfo.preview);
			}
			fileInfo.preview = URL.createObjectURL(file);

			ElMessage.success('文件选择成功');
		};

		const beforeUpload = (file: File) => {
			const isImage = file.type.startsWith('image/');
			const isVideo = file.type.startsWith('video/');
			const isLt50M = file.size / 1024 / 1024 < 50;

			if (!isImage && !isVideo) {
				ElMessage.error('只能上传图片或视频文件！');
				return false;
			}
			if (!isLt50M) {
				ElMessage.error('文件大小不能超过 50MB！');
				return false;
			}
			return true;
		};

		const handleRemoveFile = () => {
			// 释放 ObjectURL 避免内存泄漏
			if (fileInfo.preview) {
				URL.revokeObjectURL(fileInfo.preview);
			}
			fileInfo.file = null;
			fileInfo.name = '';
			fileInfo.size = 0;
			fileInfo.type = '';
			fileInfo.preview = '';
			fileInfo.uploadTime = '';
			ElMessage.success('文件已移除');
		};

		const handleSubmit = async () => {
			if (!formRef.value) return;

			// 先验证文件
			if (!fileInfo.file) {
				ElMessage.warning('请选择要审核的文件');
				return;
			}

			// 再验证表单
			try {
				await formRef.value.validate();
			} catch (error) {
				console.log('表单验证失败：', error);
				ElMessage.warning('请完善表单信息');
				return;
			}

			ElMessageBox.confirm('确定要提交审核吗？', '确认提交', {
				confirmButtonText: '确定',
				cancelButtonText: '取消',
				type: 'info',
			}).then(() => {
				submitAudit();
			}).catch(() => { });
		};

		const submitAudit = async () => {
			submitLoading.value = true;

			try {
				const formDataToSubmit = new FormData();
				formDataToSubmit.append('file', fileInfo.file!);
				formDataToSubmit.append('audit_source', String(formData.audit_source));
				formDataToSubmit.append('audit_type', String(formData.audit_type));

				if (formData.description) {
					formDataToSubmit.append('description', formData.description);
				}

				console.log('提交的数据：', {
					audit_source: formData.audit_source,
					audit_type: formData.audit_type,
					description: formData.description,
					file: {
						name: fileInfo.name,
						size: fileInfo.size,
						type: fileInfo.type,
					}
				});

				const response = await api.UploadAndAudit(formDataToSubmit);
				auditResult.value = response.data;

				ElMessage.success(response.msg || '审核完成！');
				resultDialogVisible.value = true;

			} catch (error: any) {
				ElMessage.error('审核失败：' + (error.msg || error.message || '未知错误'));
				console.error('审核失败：', error);
			} finally {
				submitLoading.value = false;
			}
		};

		const handleReset = () => {
			formRef.value?.resetFields();
			handleRemoveFile();
			ElMessage.success('表单已重置');
		};

		const handleCancel = () => {
			emit('cancel');
		};

		const handleViewAndClose = () => {
			resultDialogVisible.value = false;
			emit('success', auditResult.value);
		};

		const formatFileSize = (bytes: number) => {
			if (bytes === 0) return '0 B';
			const k = 1024;
			const sizes = ['B', 'KB', 'MB', 'GB'];
			const i = Math.floor(Math.log(bytes) / Math.log(k));
			return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
		};

		const getResultIcon = (conclusion: number) => {
			const map: any = { 1: 'success', 2: 'warning', 3: 'error', 4: 'info' };
			return map[conclusion] || 'info';
		};

		const getResultTitle = (conclusion: number) => {
			const map: any = { 1: '审核通过', 2: '疑似违规', 3: '明确违规', 4: '审核失败' };
			return map[conclusion] || '未知';
		};

		const getConclusionType = (value: number) => {
			const map: any = { 1: 'success', 2: 'warning', 3: 'danger', 4: 'info' };
			return map[value] || 'info';
		};

		const getConclusionText = (value: number) => {
			const map: any = { 1: '通过', 2: '疑似违规', 3: '明确违规', 4: '审核失败' };
			return map[value] || '未知';
		};

		const getRiskType = (value: number) => {
			const map: any = { 1: 'success', 2: 'primary', 3: 'warning', 4: 'danger' };
			return map[value] || 'info';
		};

		const getRiskText = (value: number) => {
			const map: any = { 1: '无风险', 2: '低风险', 3: '中风险', 4: '高风险' };
			return map[value] || '未知';
		};

		const getSeverityType = (severity: string) => {
			const map: any = { '低': 'success', '中': 'warning', '高': 'danger' };
			return map[severity] || 'info';
		};

		const getProgressColor = (percentage: number) => {
			if (percentage >= 80) return '#67c23a';
			if (percentage >= 60) return '#e6a23c';
			return '#f56c6c';
		};

		return {
			formRef,
			uploadRef,
			formData,
			fileInfo,
			rules,
			submitLoading,
			resultDialogVisible,
			auditResult,
			handleFileChange,
			beforeUpload,
			handleRemoveFile,
			handleSubmit,
			handleReset,
			handleCancel,
			handleViewAndClose,
			formatFileSize,
			getResultIcon,
			getResultTitle,
			getConclusionType,
			getConclusionText,
			getRiskType,
			getRiskText,
			getSeverityType,
			getProgressColor,
		};
	}
});
</script>

<style scoped lang="scss">
.upload-form-container {
	padding: 16px;
	height: 100%;
	overflow-y: auto;

	.upload-container {
		width: 100%;

		.upload-dragger {
			padding: 36px 20px;
			text-align: center;

			.upload-icon {
				color: #409eff;
				margin-bottom: 14px;
				filter: drop-shadow(0 2px 6px rgba(64, 158, 255, 0.3));
			}

			.upload-text {
				font-size: 15px;
				font-weight: 500;
				color: #303133;
				margin-bottom: 8px;
			}

			.upload-hint {
				font-size: 12px;
				color: #a8abb2;
				letter-spacing: 0.3px;
			}
		}

		.file-preview {
			margin-top: 16px;
			animation: fadeSlideIn 0.3s ease-out;

			.preview-content {

				.image-preview,
				.video-preview {
					text-align: center;
					margin-bottom: 16px;
					padding: 16px;
					background: linear-gradient(135deg, #f5f7fa 0%, #eef1f6 100%);
					border-radius: 8px;
					border: 1px solid #e8ecf1;
				}

				.image-error {
					display: flex;
					flex-direction: column;
					align-items: center;
					justify-content: center;
					padding: 30px;
					color: #c0c4cc;

					.el-icon {
						font-size: 48px;
						margin-bottom: 8px;
					}
				}

				.file-info {
					margin-top: 14px;
				}
			}
		}
	}

	.form-actions {
		display: flex;
		justify-content: center;
		gap: 14px;
		margin-top: 28px;
		padding-top: 20px;
	}

	.audit-result {
		.result-subtitle {
			margin-top: 8px;
			line-height: 1.8;
			color: #606266;

			p {
				margin: 4px 0;
			}
		}
	}
}

@keyframes fadeSlideIn {
	from {
		opacity: 0;
		transform: translateY(8px);
	}

	to {
		opacity: 1;
		transform: translateY(0);
	}
}

:deep(.el-divider__text) {
	display: flex;
	align-items: center;
	font-weight: 600;
	font-size: 14px;
	color: #303133;

	.el-icon {
		color: #409eff;
	}
}

:deep(.el-upload) {
	width: 100%;
}

:deep(.el-upload-dragger) {
	width: 100%;
	border: 2px dashed #dcdfe6;
	border-radius: 8px;
	background-color: #fafbfc;
	transition: all 0.3s ease;

	&:hover {
		border-color: #409eff;
		background-color: #ecf5ff;
		box-shadow: 0 0 12px rgba(64, 158, 255, 0.12);
	}
}

:deep(.file-preview .el-card) {
	border-radius: 8px;
	border: 1px solid #e4e7ed;
	transition: box-shadow 0.3s ease;

	&:hover {
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
	}
}

:deep(.el-descriptions) {
	.el-descriptions__label {
		font-weight: 500;
		color: #606266;
	}
}
</style>
