<template>
  <el-card shadow="never" class="changelog-panel">
    <template #header>
      <div class="panel-header">
        <span class="panel-title">变更记录</span>
        <el-tag size="small" type="info">共 {{ changes.length }} 条</el-tag>
      </div>
    </template>

    <el-timeline v-if="changes.length > 0">
      <el-timeline-item
        v-for="item in changes"
        :key="item.id"
        :timestamp="item.operation_time"
        :type="getTimelineType(item.action_type)"
        :hollow="true"
        placement="top"
      >
        <div class="change-item">
          <div class="change-header">
            <el-tag size="small" :type="actionTypeTag(item.action_type)">
              {{ actionTypeText(item.action_type) }}
            </el-tag>
            <span class="change-node">{{ changeNodeText(item.change_node) }}</span>
            <span class="change-operator">{{ item.operator_name || '-' }}</span>
          </div>

          <div class="change-body">
            <div class="change-target">
              <span>线路：{{ item.roadline_name || '-' }}</span>
              <span>车辆：{{ item.vehicle_no || '-' }}</span>
              <span>公司：{{ item.roadline_company_name || '-' }}</span>
            </div>

            <div v-if="item.change_reason" class="change-reason">
              {{ item.change_reason }}
            </div>

            <!-- 变更前后对比 -->
            <div v-if="hasDiff(item)" class="change-diff">
              <div v-if="item.before_data" class="diff-item before">
                <span class="diff-label">变更前：</span>
                <span class="diff-value">{{ formatDiffData(item.before_data) }}</span>
              </div>
              <div v-if="item.after_data" class="diff-item after">
                <span class="diff-label">变更后：</span>
                <span class="diff-value">{{ formatDiffData(item.after_data) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-timeline-item>
    </el-timeline>

    <el-empty v-else description="暂无变更记录" :image-size="50" />
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  changes: Record<string, any>[]
}>()

const ACTION_TYPE_MAP: Record<number, { text: string; tag: string; timeline: string }> = {
  1: { text: '新增车位', tag: 'success', timeline: 'success' },
  2: { text: '删除车位', tag: 'danger', timeline: 'danger' },
  3: { text: '修改车位', tag: 'warning', timeline: 'warning' },
}

const NODE_MAP: Record<string, string> = {
  '1': '媒体部初审',
  '2': '营运公司审核',
  '3': '媒体部复审',
}

const actionTypeText = (t: number) => ACTION_TYPE_MAP[t]?.text || '未知操作'
const actionTypeTag = (t: number) => ACTION_TYPE_MAP[t]?.tag || 'info'
const getTimelineType = (t: number) => ACTION_TYPE_MAP[t]?.timeline || 'info'
const changeNodeText = (n: string) => NODE_MAP[n] || n || '-'

const hasDiff = (item: any) => item.before_data || item.after_data

const formatDiffData = (data: string) => {
  if (!data) return '-'
  try {
    const obj = typeof data === 'string' ? JSON.parse(data) : data
    return Object.entries(obj)
      .map(([k, v]) => `${k}: ${v}`)
      .join(', ')
  } catch {
    return data
  }
}
</script>

<style scoped lang="scss">
.changelog-panel {
  margin-bottom: 12px;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.panel-title {
  font-weight: 600;
  font-size: 15px;
}

.change-item {
  font-size: 13px;
}

.change-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.change-node {
  color: var(--el-text-color-secondary);
}

.change-operator {
  color: var(--el-text-color-regular);
  font-weight: 500;
}

.change-target {
  display: flex;
  gap: 16px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.change-reason {
  margin-top: 4px;
  padding: 4px 8px;
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
  font-size: 12px;
}

.change-diff {
  margin-top: 6px;
  font-size: 12px;
}

.diff-item {
  display: flex;
  gap: 4px;
  padding: 2px 0;
}

.diff-label {
  font-weight: 500;
  flex-shrink: 0;
}

.diff-item.before .diff-value {
  color: var(--el-color-danger);
  text-decoration: line-through;
}

.diff-item.after .diff-value {
  color: var(--el-color-success);
}
</style>
