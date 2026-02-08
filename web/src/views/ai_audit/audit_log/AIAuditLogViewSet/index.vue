<template>
	<div class="module-container">
		<div class="module-header">
			<h2>审查执行</h2>
			<div class="ai-helper">
				<i class="ri-shield-check-line"></i> AI 画面合规性预审中
			</div>
		</div>

		<el-tabs v-model="activeTab" @tab-change="handleTabChange">
			<el-tab-pane label="待审核画面" name="review">
				<div v-loading="reviewLoading" class="review-grid">
					<div v-if="reviewList.length === 0" class="empty-state">
						暂无待审核记录
					</div>
					<el-card v-for="item in reviewList" :key="item.id" :body-style="{ padding: '0px' }">
						<div class="image-placeholder" @click="openReport(item.id)">
							<el-image v-if="item.file_path" :src="item.file_path" fit="contain"
									style="width: 100%; height: 100%">
								<template #error>
									<div class="placeholder-icon"><i class="ri-image-off-line"></i></div>
									<div class="placeholder-text">图片加载失败</div>
								</template>
							</el-image>
							<div v-else>
								<div class="placeholder-icon"><i class="ri-image-2-line"></i></div>
								<div class="placeholder-text">点击查看详情</div>
							</div>
						</div>
						<div style="padding: 14px">
							<span class="file-name" :title="item.file_name">{{ item.file_name || '未命名文件' }}</span>
							<div class="bottom">
								<div class="ai-check-result" :class="getResultClass(item.ai_conclusion)">
									<i :class="getResultIcon(item.ai_conclusion)"></i>
									{{ getResultText(item.ai_conclusion) }}
								</div>
								<el-button type="primary" link @click="openReport(item.id)">人工复核</el-button>
							</div>
						</div>
					</el-card>
				</div>
				<div class="pagination-container">
					<el-pagination v-model:current-page="reviewPage.page" v-model:page-size="reviewPage.limit"
							:total="reviewPage.total" layout="prev, pager, next" @current-change="fetchReviewList" />
				</div>
			</el-tab-pane>
			<el-tab-pane label="上刊任务" name="install">
				<div v-loading="installLoading">
					<div v-if="installList.length === 0" class="empty-state">
						暂无上刊任务记录
					</div>
					<el-timeline>
						<el-timeline-item v-for="item in installList" :key="item.id"
								:timestamp="formatDate(item.create_datetime)" placement="top">
							<el-card>
								<h4>{{ item.file_name || '未命名任务' }}</h4>
								<p>执行人员: {{ item.creator_name || '系统用户' }}</p>
								<p>状态: {{ getResultText(item.ai_conclusion) }}</p>
								<el-progress :percentage="getConfidence(item.confidence_score)"
										:status="getProgressStatus(item.ai_conclusion)" />
							</el-card>
						</el-timeline-item>
					</el-timeline>
					<div class="pagination-container">
						<el-pagination v-model:current-page="installPage.page" v-model:page-size="installPage.limit"
								:total="installPage.total" layout="prev, pager, next"
								@current-change="fetchInstallList" />
					</div>
				</div>
			</el-tab-pane>
		</el-tabs>

		<!-- AI Report Modal -->
		<el-dialog v-model="dialogVisible" title="AI 合规性检测报告" width="900px" top="5vh">
			<div v-loading="reportLoading" class="report-layout">
				<!-- Left: Image Preview with AI Annotation -->
				<div class="report-image-section">
					<div class="annotated-image">
						<el-image v-if="currentReport.file_path" :src="currentReport.file_path" fit="contain"
								class="report-img" />
						<div v-else class="image-mock">
							<i class="ri-image-2-line"></i>
							<span>广告画面预览</span>
						</div>
						<!-- AI Bounding Box Overlay (Mock for now, can be real if coordinates exist) -->
						<div v-if="currentReport.ai_conclusion === 2 || currentReport.ai_conclusion === 3"
								class="bounding-box sensitive">
							<span class="box-label">风险点</span>
						</div>
						<div v-if="currentReport.ai_conclusion === 1" class="bounding-box safe">
							<span class="box-label">合规</span>
						</div>
					</div>
					<div class="image-meta">
						<span>文件: {{ currentReport.file_name }}</span>
						<span>耗时: {{ currentReport.duration_seconds }}s</span>
						<span>类型: {{ getAuditType(currentReport.audit_type) }}</span>
					</div>
				</div>

				<!-- Right: Analysis Details -->
				<div class="report-content">
					<div class="report-score">
						<el-progress type="dashboard" :percentage="getConfidence(currentReport.confidence_score)"
								:color="scoreColor" />
						<div class="score-label">置信度</div>
					</div>
					<div class="report-details">
						<h4>检测项详情:</h4>
						<el-collapse v-model="activeNames">
							<el-collapse-item title="AI 判定结果" name="1">
								<div v-if="currentReport.ai_conclusion === 2 || currentReport.ai_conclusion === 3"
										class="risk-item">
									<i class="ri-alert-fill"></i> {{ getResultText(currentReport.ai_conclusion) }}
									<div v-if="currentReport.violation_content" class="violation-json">
										{{ currentReport.violation_content }}
									</div>
								</div>
								<div v-else class="pass-item"><i class="ri-check-double-line"></i>
									{{ getResultText(currentReport.ai_conclusion) }}
								</div>
								<div class="audit-summary" v-if="currentReport.summary">
									{{ currentReport.summary }}
								</div>
							</el-collapse-item>
							<el-collapse-item title="检测项详情" name="2">
								<div v-if="currentReport.detection_details">
									<pre
											class="json-content">{{ JSON.stringify(currentReport.detection_details, null, 2) }}
									</pre>
								</div>
								<div v-else class="pass-item">无详细检测数据</div>
							</el-collapse-item>
						</el-collapse>
					</div>
				</div>
			</div>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="dialogVisible = false">关闭</el-button>
					<el-button v-if="currentReport.need_manual_review" type="primary" @click="handleManualReview">
						人工确认
					</el-button>
				</span>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { GetList, GetObj, UpdateObj } from './api'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const activeTab = ref('review')
const dialogVisible = ref(false)
const activeNames = ref(['1', '2'])
const currentReport = ref<any>({})
const reportLoading = ref(false)

// Review List
const reviewList = ref<any[]>([])
const reviewLoading = ref(false)
const reviewPage = ref({
	page: 1,
	limit: 12,
	total: 0
})

// Install List
const installList = ref<any[]>([])
const installLoading = ref(false)
const installPage = ref({
	page: 1,
	limit: 10,
	total: 0
})

// Fetch Review List (Default pending or all)
const fetchReviewList = async () => {
	reviewLoading.value = true
	try {
		const res = await GetList({
			page: reviewPage.value.page,
			limit: reviewPage.value.limit,
			ordering: '-create_datetime',
			// search: { need_manual_review: true } // Optional: filter only needed
		})
		if (res.data) {
			reviewList.value = res.data
			reviewPage.value.total = res.total || 0
		}
	} catch (e) {
		console.error(e)
	} finally {
		reviewLoading.value = false
	}
}

// Fetch Install List (Audit Source = 1)
const fetchInstallList = async () => {
	installLoading.value = true
	try {
		const res = await GetList({
			page: installPage.value.page,
			limit: installPage.value.limit,
			audit_source: 1, // Order associated
			ordering: '-create_datetime'
		})
		if (res.data) {
			installList.value = res.data
			installPage.value.total = res.total || 0
		}
	} catch (e) {
		console.error(e)
	} finally {
		installLoading.value = false
	}
}

const handleTabChange = (val: string) => {
	if (val === 'review') {
		fetchReviewList()
	} else {
		fetchInstallList()
	}
}

const openReport = async (id: string | number) => {
	dialogVisible.value = true
	reportLoading.value = true
	try {
		const res = await GetObj(id)
		currentReport.value = res.data || {}
	} catch (e) {
		ElMessage.error('获取详情失败')
	} finally {
		reportLoading.value = false
	}
}

const handleManualReview = async () => {
	// Determine new status (e.g. manually passed)
	// This logic depends on business requirement. For now, assume manual pass.
	try {
		await UpdateObj({
			id: currentReport.value.id,
			need_manual_review: false,
			ai_conclusion: 1, // Manual Pass
			description: '人工复核通过'
		})
		ElMessage.success('已人工确认通过')
		dialogVisible.value = false
		fetchReviewList()
	} catch (e) {
		ElMessage.error('操作失败')
	}
}

// Computeds
const scoreColor = computed(() => {
	const score = getConfidence(currentReport.value.confidence_score)
	return score < 80 ? '#f56c6c' : '#67c23a'
})

// Helpers
const getResultClass = (status: number) => {
	// 1: Pass, 2: Suspect, 3: Violation, 4: Fail
	switch (status) {
		case 1: return 'success'
		case 2: return 'warning'
		case 3: return 'danger'
		default: return 'info'
	}
}

const getResultIcon = (status: number) => {
	switch (status) {
		case 1: return 'ri-checkbox-circle-line'
		case 2: return 'ri-error-warning-line'
		case 3: return 'ri-close-circle-line'
		default: return 'ri-question-line'
	}
}

const getResultText = (status: number) => {
	switch (status) {
		case 1: return 'AI 通过'
		case 2: return '疑似违规'
		case 3: return '明确违规'
		case 4: return '审核失败'
		default: return '未知状态'
	}
}

const getProgressStatus = (status: number) => {
	switch (status) {
		case 1: return 'success'
		case 2: return 'warning'
		case 3: return 'exception'
		default: return ''
	}
}

const getConfidence = (score: string | number) => {
	return score ? Number(score) : 0
}

const formatDate = (date: string) => {
	return dayjs(date).format('YYYY/MM/DD HH:mm')
}

const getAuditType = (type: number) => {
	const types: Record<number, string> = {
		1: '画面内容',
		2: '证明文件',
		3: '综合审核'
	}
	return types[type] || '未知'
}

onMounted(() => {
	fetchReviewList()
})
</script>

<style scoped>
.module-container {
	padding: 20px;
	background: #fff;
	border-radius: 8px;
	min-height: calc(100vh - 120px);
}

.module-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 5px;
	padding-bottom: 5px;
	border-bottom: 1px solid #eee;
}

.module-header h2 {
	margin: 0;
	font-size: 18px;
}

.ai-helper {
	color: var(--el-color-primary);
	background: var(--el-color-primary-light-9);
	padding: 2px 10px;
	border-radius: 15px;
	font-size: 12px;
}

.review-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
	gap: 20px;
}

.image-placeholder {
	height: 180px;
	background: #f0f2f5;
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	color: #999;
	cursor: pointer;
	transition: background 0.3s;
	overflow: hidden;
}

.image-placeholder:hover {
	background: #e6e8eb;
}

.placeholder-icon {
	font-size: 32px;
	margin-bottom: 8px;
}

.file-name {
	display: block;
	width: 100%;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.bottom {
	margin-top: 13px;
	line-height: 12px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.ai-check-result {
	font-size: 12px;
	display: flex;
	align-items: center;
	gap: 4px;
}

.ai-check-result.warning {
	color: #e6a23c;
}

.ai-check-result.success {
	color: #67c23a;
}

.ai-check-result.danger {
	color: #f56c6c;
}

.ai-check-result.info {
	color: #909399;
}

/* Modal Styles */
.report-content {
	display: flex;
	gap: 30px;
}

.report-score {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 20px;
	background: #f9f9f9;
	border-radius: 8px;
	height: fit-content;
}

.score-label {
	margin-top: 10px;
	font-weight: bold;
	color: #666;
}

.report-details {
	flex: 1;
}

.risk-item {
	color: #f56c6c;
	display: flex;
	align-items: center;
	gap: 5px;
	flex-wrap: wrap;
}

.pass-item {
	color: #67c23a;
	display: flex;
	align-items: center;
	gap: 5px;
}

.image-meta {
	margin-top: 10px;
	display: flex;
	flex-direction: column;
	gap: 4px;
	font-size: 12px;
	color: #666;
}

.report-img {
	width: 100%;
	max-height: 300px;
}

.audit-summary {
	margin-top: 8px;
	font-size: 13px;
	color: #666;
	background: #f4f4f5;
	padding: 8px;
	border-radius: 4px;
}

.json-content {
	background: #f4f4f5;
	padding: 10px;
	font-size: 12px;
	overflow-x: auto;
}

.pagination-container {
	margin-top: 20px;
	display: flex;
	justify-content: flex-end;
}

.empty-state {
	grid-column: 1 / -1;
	text-align: center;
	padding: 40px;
	color: #909399;
}

.violation-json {
	width: 100%;
	font-size: 12px;
	background: #fef0f0;
	padding: 5px;
	border-radius: 4px;
	margin-top: 4px;
}
</style>
