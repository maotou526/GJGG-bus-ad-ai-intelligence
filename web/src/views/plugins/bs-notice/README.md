# 消息通知系统前端组件

## 目录结构

```
bs-notice/
├── api/                          # API 接口定义
│   └── index.ts                  # 消息通知相关 API
├── components/                   # 组件目录
│   ├── UnreadNoticeBadge/        # 未读消息徽章组件（用于顶部导航栏）
│   │   └── index.vue
│   ├── NoticeList/               # 消息列表组件（可复用）
│   │   └── index.vue
│   └── NoticeDetail/             # 消息详情组件
│       └── index.vue
├── list/                         # 消息列表页面
│   ├── index.vue                 # 主页面
│   ├── crud.tsx                  # CRUD 配置（使用 fast-crud）
│   └── types.ts                  # TypeScript 类型定义
└── README.md                     # 本文档
```

## 使用说明

### 1. 消息列表页面

**路径**: `/plugins/bs-notice`

**功能**:
- 查看所有消息（全部/未读/已读/待办）
- 筛选消息类型和优先级
- 批量操作（标记已读、删除）
- 单个操作（标记已读、处理、忽略、跳转业务）

**路由配置**:
```typescript
{
  path: '/plugins/bs-notice',
  name: 'BsNotice',
  component: () => import('/@/views/plugins/bs-notice/list/index.vue'),
  meta: {
    title: '消息中心',
    icon: 'Bell',
  },
}
```

### 2. 未读消息徽章组件

**组件路径**: `components/UnreadNoticeBadge/index.vue`

**使用场景**: 顶部导航栏右侧，显示未读消息数量

**使用方法**:
```vue
<template>
  <UnreadNoticeBadge />
</template>

<script setup>
import UnreadNoticeBadge from '/@/views/plugins/bs-notice/components/UnreadNoticeBadge/index.vue';
</script>
```

**功能**:
- 显示未读消息数量（红色徽章）
- 点击后弹出未读消息列表
- 支持快速操作（标记已读、跳转详情）
- 自动刷新（每30秒）

### 3. 消息详情组件

**组件路径**: `components/NoticeDetail/index.vue`

**使用方法**:
```vue
<template>
  <NoticeDetail v-model="visible" :notice-id="noticeId" @refresh="handleRefresh" />
</template>

<script setup>
import { ref } from 'vue';
import NoticeDetail from '/@/views/plugins/bs-notice/components/NoticeDetail/index.vue';

const visible = ref(false);
const noticeId = ref('');

const handleRefresh = () => {
  // 刷新消息列表
};
</script>
```

**Props**:
- `modelValue`: Boolean - 控制对话框显示/隐藏
- `noticeId`: String - 消息ID

**Events**:
- `refresh`: 消息状态更新后触发

### 4. 消息列表组件（可复用）

**组件路径**: `components/NoticeList/index.vue`

**使用方法**:
```vue
<template>
  <NoticeList
    :notice-list="notices"
    :loading="loading"
    :total="total"
    :page="page"
    :page-size="pageSize"
    show-pagination
    @item-click="handleItemClick"
    @mark-read="handleMarkRead"
    @jump="handleJump"
    @page-change="handlePageChange"
    @size-change="handleSizeChange"
  />
</template>

<script setup>
import { ref } from 'vue';
import NoticeList from '/@/views/plugins/bs-notice/components/NoticeList/index.vue';
import { NoticeItem } from '/@/views/plugins/bs-notice/list/types';

const notices = ref<NoticeItem[]>([]);
const loading = ref(false);
const total = ref(0);
const page = ref(1);
const pageSize = ref(20);

const handleItemClick = (item: NoticeItem) => {
  // 处理点击事件
};

const handleMarkRead = (item: NoticeItem) => {
  // 处理标记已读
};

const handleJump = (item: NoticeItem) => {
  // 处理跳转
};

const handlePageChange = (pageNum: number) => {
  page.value = pageNum;
  // 重新加载数据
};

const handleSizeChange = (size: number) => {
  pageSize.value = size;
  // 重新加载数据
};
</script>
```

**Props**:
- `noticeList`: NoticeItem[] - 消息列表
- `loading`: Boolean - 加载状态
- `title`: String - 标题（默认：'消息列表'）
- `showHeader`: Boolean - 显示头部（默认：true）
- `showContent`: Boolean - 显示内容（默认：true）
- `showActions`: Boolean - 显示操作按钮（默认：true）
- `showPagination`: Boolean - 显示分页（默认：false）
- `total`: Number - 总数
- `page`: Number - 当前页
- `pageSize`: Number - 每页数量
- `emptyText`: String - 空数据提示（默认：'暂无消息'）

**Events**:
- `item-click`: 点击消息项
- `mark-read`: 标记已读
- `jump`: 跳转业务页面
- `page-change`: 页码变化
- `size-change`: 每页数量变化

## API 接口

所有 API 接口定义在 `api/index.ts` 中：

- `getUnreadCount()` - 获取未读消息数量
- `getMyNotices(params)` - 获取用户消息列表
- `markAsRead(id)` - 标记消息为已读
- `markAsHandled(id)` - 标记消息为已处理
- `markAsIgnored(id)` - 标记消息为已忽略
- `deleteNotice(id)` - 删除消息
- `batchMarkRead(ids)` - 批量标记已读
- `batchDelete(ids)` - 批量删除
- `getNoticeDetail(id)` - 获取消息详情

## 类型定义

所有类型定义在 `list/types.ts` 中：

- `NoticeItem` - 消息项类型
- `PageQuery` - 分页查询参数
- `MsgType` - 消息类型枚举
- `Priority` - 优先级枚举
- `ReadStatus` - 阅读状态枚举
- `HandleStatus` - 处理状态枚举

## 样式定制

所有组件都使用了 scoped 样式，可以通过以下方式定制：

1. 使用 CSS 变量覆盖默认颜色
2. 使用深度选择器覆盖组件内部样式
3. 通过 props 传递自定义类名

## 注意事项

1. **权限控制**: 所有接口都需要用户登录
2. **数据安全**: 只显示当前用户的消息
3. **性能优化**: 
   - 列表使用分页加载
   - 未读数量使用防抖刷新
   - 图片和富文本内容懒加载
4. **错误处理**: API 调用失败时显示友好提示
5. **加载状态**: 列表加载时显示 loading 动画

## 后续扩展

1. **消息推送**: 集成 WebSocket 实现实时消息推送
2. **消息模板**: 前端消息模板预览和编辑
3. **消息统计**: 消息阅读率、处理率等统计图表
4. **消息设置**: 用户个性化消息设置
5. **移动端适配**: 响应式设计，支持移动端访问

