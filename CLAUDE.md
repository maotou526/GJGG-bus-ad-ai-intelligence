# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指导。

## 项目概述

Django-Vue3-Admin 全栈单体仓库，用于公交广告管理系统（公交广告智擎）。基于 [django-vue3-admin](https://gitee.com/huge-dream/django-vue3-admin) 开发，采用 RBAC 权限系统。

## 技术栈

- **后端:** Python 3.11+, Django 4.2, DRF, SimpleJWT, Celery, Channels
- **前端:** Vue 3, TypeScript, Vite, Pinia, Element Plus, FastCRUD
- **数据库:** MySQL 8.0+（生产环境），SQLite（开发环境）
- **缓存/队列:** Redis

## 常用命令

### 后端（在项目根目录执行）

```bash
# 激活虚拟环境（Windows PowerShell）
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r backend/requirements.txt

# 数据库迁移
python backend/manage.py makemigrations
python backend/manage.py migrate

# 初始化系统数据（首次安装时执行）
python backend/manage.py init
python backend/manage.py init_area

# 运行开发服务器
python backend/manage.py runserver 0.0.0.0:8000

# 使用 uvicorn 运行（类生产环境）
uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 8

# Celery 工作进程（Windows 需使用 solo 模式）
celery -A application worker -l info -P solo --workdir backend

# 运行测试
python backend/manage.py test
```

### 前端（在 `web/` 目录执行）

```bash
pnpm install --no-frozen-lockfile
pnpm dev              # 开发服务器
pnpm build            # 生产环境构建
pnpm build:dev        # 开发环境构建
pnpm lint-fix         # 代码检查和修复
```

### Docker

```bash
docker compose up -d --build
docker exec dvadmin3-django python manage.py migrate
docker exec dvadmin3-django python manage.py init
```

## 架构

### 后端结构

```
backend/
├── application/          # Django 项目配置（settings, urls, celery, asgi）
├── conf/                 # 环境配置文件（env.py, env_prod.py）
├── dvadmin/
│   ├── system/          # 核心 RBAC 系统（用户、角色、部门、菜单、权限）
│   ├── utils/           # 基类（viewset.py, serializers.py, filters.py）
│   └── database/        # 多数据库支持
├── dvadmin_twodev/      # 业务模块
│   ├── basedata/        # 线路、车辆、公司、区域
│   ├── osm/             # OpenStreetMap 集成
│   ├── line_overlap/    # 线路分析
│   └── node_workflow/   # 工作流引擎
└── dvadmin_extensions/  # 数据权限、分表扩展
```

### 前端结构

```
web/src/
├── api/                 # 按业务领域划分的 API 客户端模块
├── views/               # 页面组件（system/, basedata/, osm/）
├── stores/              # Pinia 状态管理
├── router/              # Vue Router（backEnd.ts 系统路由，frontEnd.ts 业务路由）
├── components/          # 可复用组件
├── utils/service.ts     # HTTP 请求封装
└── settings.ts          # FastCRUD 配置
```

### 关键模式

- **ViewSets:** 所有 API 视图继承自 `dvadmin/utils/viewset.py` 中的 `CustomModelViewSet`
- **Serializers:** 继承自 `dvadmin/utils/serializers.py` 中的 `CustomModelSerializer`
- **CRUD 页面:** 使用 FastCRUD 模式，配合 `commonCrud.ts` 辅助函数
- **状态管理:** Pinia stores 位于 `stores/modules/`，按功能模块划分
- **权限控制:** 列级权限通过 `MenuField`，按钮级权限通过 `MenuButton`

## 配置管理

环境由 `DJANGO_ENV` 控制：
- 未设置 → 加载 `backend/conf/env.py`（开发环境）
- `DJANGO_ENV=production` → 加载 `backend/conf/env_prod.py`

环境配置文件中的关键设置：DATABASE, REDIS, DEBUG, ALLOWED_HOSTS, CORS_ORIGIN_WHITELIST

## API 访问

- Swagger 文档: `http://localhost:8000/swagger/`（仅 DEBUG=True 时可用）
- Redoc 文档: `http://localhost:8000/redoc/`
- 默认登录账号: `superadmin` / `admin123456`

## 开发规范

来自 `.cursorrules`：

- **提交信息:** 使用约定式提交（`feat:`, `fix:`, `chore:`, `docs:`）
- **分支命名:** `feature/<scope>-<desc>` 或 `fix/<scope>-<desc>`
- **模型字段:** 所有字段必须包含 `db_comment` 属性
- **数据库迁移:** 禁止手动编辑迁移文件，始终使用 `makemigrations`
- **模式变更:** 使用带默认值的迁移，避免破坏性变更
