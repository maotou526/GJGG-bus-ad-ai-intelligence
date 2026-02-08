/*
 * @Description: AI审核上传API接口
 * @Version: 1.0
 * @Date: 2026-02-04
 *
 * 数据流说明：
 * 1. 前端收集表单数据和文件
 * 2. 使用 FormData 格式提交到后端
 * 3. 后端保存文件并触发AI审核
 * 4. 返回审核结果
 */
import { request } from '/@/utils/service';

// API前缀
export const apiPrefix = '/api/AIAuditLogViewSet/';

/**
 * 上传文件并触发AI审核
 *
 * @param formData FormData对象，包含以下字段：
 *   - file: File对象（必填）
 *   - audit_source: number 审核来源（1:关联订单 2:独立审核）
 *   - audit_type: number 审核类型（1:画面内容 2:证明文件 3:综合审核）
 *   - material_id?: number 关联材料ID（关联订单审核时必填）
 *   - order_id?: number 上刊订单ID（可选）
 *   - description?: string 备注说明（可选）
 *
 * @returns Promise 审核结果
 *
 * 返回数据结构：
 * {
 *   code: 2000,
 *   msg: "审核完成",
 *   data: {
 *     audit_log_id: 123,           // 审核记录ID
 *     audit_no: "AUD-20260204-0001", // 审核编号
 *     ai_conclusion: 1,            // AI判定（1:通过 2:疑似违规 3:明确违规 4:审核失败）
 *     risk_level: 1,               // 风险等级（1:无风险 2:低风险 3:中风险 4:高风险）
 *     confidence_score: 95.5,      // 置信度（0-100）
 *     need_manual_review: false,   // 是否需要人工复核
 *     duration_seconds: 2,         // 审核耗时（秒）
 *     request_time: "2026-02-04T10:00:00",   // 请求时间
 *     response_time: "2026-02-04T10:00:02",  // 响应时间
 *     detection_details: [...],    // 检测项详情（JSON）
 *     violation_content: [         // 违规内容列表
 *       {
 *         category: "虚假宣传",
 *         description: "使用了'最好'等绝对化用语",
 *         severity: "中",
 *         position: "画面中央文字"
 *       }
 *     ],
 *     file_path: "media/2026/02/xxx.jpg",  // 文件保存路径
 *     file_name: "example.jpg"              // 文件名
 *   }
 * }
 */
export function UploadAndAudit(formData: FormData) {
	return request({
		url: apiPrefix + 'upload_and_audit/',
		method: 'post',
		data: formData,
		headers: {
			'Content-Type': 'multipart/form-data'
		},
		timeout: 60000, // 60秒超时（AI审核可能需要较长时间）
	});
}

/**
 * 仅上传文件（不触发审核）
 *
 * 如果需要先上传文件，再手动触发审核，可以使用此接口
 *
 * @param file File对象
 * @returns Promise 文件信息
 */
export function UploadFileOnly(file: File) {
	const formData = new FormData();
	formData.append('file', file);
	formData.append('upload_method', '1');

	return request({
		url: '/api/system/file/',
		method: 'post',
		data: formData,
		headers: {
			'Content-Type': 'multipart/form-data'
		},
	});
}

/**
 * 手动触发审核（已上传的文件）
 *
 * @param params 审核参数
 *   - file_id: number 文件ID
 *   - file_path: string 文件路径
 *   - audit_source: number 审核来源
 *   - audit_type: number 审核类型
 *   - material_id?: number 关联材料ID
 *   - order_id?: number 上刊订单ID
 *
 * @returns Promise 审核结果
 */
export function TriggerAudit(params: {
	file_id?: number;
	file_path?: string;
	file_name?: string;
	audit_source: number;
	audit_type: number;
	material_id?: number;
	order_id?: number;
}) {
	return request({
		url: apiPrefix + 'trigger_audit/',
		method: 'post',
		data: params,
		timeout: 60000,
	});
}

/**
 * 批量上传并审核
 *
 * @param files File对象数组
 * @param params 公共审核参数
 * @returns Promise 批量审核结果
 */
export function BatchUploadAndAudit(files: File[], params: {
	audit_source: number;
	audit_type: number;
	material_id?: number;
	order_id?: number;
}) {
	const formData = new FormData();

	// 添加文件
	files.forEach((file, index) => {
		formData.append(`files[${index}]`, file);
	});

	// 添加其他参数
	Object.entries(params).forEach(([key, value]) => {
		if (value !== null && value !== undefined) {
			formData.append(key, String(value));
		}
	});

	return request({
		url: apiPrefix + 'batch_upload_and_audit/',
		method: 'post',
		data: formData,
		headers: {
			'Content-Type': 'multipart/form-data'
		},
		timeout: 120000, // 批量审核需要更长时间
	});
}

/**
 * 查询审核结果
 *
 * @param auditLogId 审核记录ID
 * @returns Promise 审核详情
 */
export function GetAuditResult(auditLogId: number) {
	return request({
		url: apiPrefix + auditLogId + '/',
		method: 'get',
	});
}

/**
 * 根据审核编号查询
 *
 * @param auditNo 审核编号
 * @returns Promise 审核详情
 */
export function GetAuditByNo(auditNo: string) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: {
			audit_no: auditNo,
			limit: 1
		}
	});
}
