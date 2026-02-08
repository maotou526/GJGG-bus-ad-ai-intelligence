# Docker 镜像构建与部署指南

本文档说明如何构建、推送和运行太仓线网管理后台的 Docker 镜像。

---

## 目录

- [快速开始](#快速开始)
- [镜像构建](#镜像构建)
- [镜像推送](#镜像推送)
- [本地运行](#本地运行)
- [常用命令](#常用命令)

---

## 快速开始

### 前置要求

- Docker 和 Docker Compose 已安装
- 已配置 `backend/conf/env.py` 数据库连接信息

### 一键启动

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

---

## 镜像构建

### 使用 docker-compose 构建（推荐）

在项目根目录执行：

```bash
# 停止旧容器（可选）
docker-compose down

# 构建所有镜像
docker-compose build

# 或者构建并启动
docker-compose up -d --build
```

构建完成后，本地应拥有以下镜像：
- `taicang-dvadmin3-web:1.0` - 前端服务
- `taicang-dvadmin3-django:1.0` - 后端服务
- `taicang-dvadmin3-celery:1.0` - 异步任务服务

### 单独构建（不推荐）

如果需要单独构建某个服务：

```bash
# 构建前端
docker build -f ./docker_env/web/Dockerfile -t taicang-dvadmin3-web:1.0 .

# 构建后端
docker build -f ./docker_env/django/Dockerfile -t taicang-dvadmin3-django:1.0 .

# 构建 Celery
docker build -f ./docker_env/celery/Dockerfile -t taicang-dvadmin3-celery:1.0 .
```

---

## 镜像推送

### 推送到 Harbor

详细的推送步骤请参考：[镜像构建与推送.md](./镜像构建与推送.md)
60.204.199.11:8880
www.wys8fb8.top:8443
简要步骤：

```bash
# 1. 登录 Harbor
docker login 60.204.199.11:8880 -u <Harbor用户名>

# 2. 标记并推送镜像
# web
docker tag taicang-dvadmin3-web:1.0 60.204.199.11:8880/tai_cang_od/taicang-dvadmin3-web:1.0
docker push 60.204.199.11:8880/tai_cang_od/taicang-dvadmin3-web:1.0

# Django
docker tag taicang-dvadmin3-django:1.0 60.204.199.11:8880/tai_cang_od/taicang-dvadmin3-django:1.0
docker push 60.204.199.11:8880/tai_cang_od/taicang-dvadmin3-django:1.0

# 删除本地镜像
docker rmi www.wys8fb8.top:8443/tai_cang_od/taicang-dvadmin3-django:1.1

# 重新拉取
docker pull www.wys8fb8.top:8443/tai_cang_od/taicang-dvadmin3-django:1.1

# 某些 Docker 版本支持
docker pull --no-cache www.wys8fb8.top:8443/tai_cang_od/taicang-dvadmin3-django:1.1
```

---

## 本地运行

### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 初始化数据库（首次运行）

```bash
# 进入 Django 容器
docker exec -it taicang-dvadmin3-django bash

# 执行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 初始化系统数据（如果需要）
python manage.py init -y

# 退出容器
exit
```

### 访问地址

- **前端地址**：http://localhost:8080
- **后端地址**：http://localhost:8000
- **Swagger 文档**：http://localhost:8000/（仅在 DEBUG=True 时可用）

> 注意：在服务器上部署时，请将 `localhost` 替换为实际的服务 IP 地址

### 默认账号

- 用户名：`superadmin`
- 密码：`admin123456`

> ⚠️ 生产环境请及时修改默认密码！

---

## 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart taicang-dvadmin3-django

# 查看日志
docker-compose logs -f

# 查看单个服务日志
docker-compose logs -f taicang-dvadmin3-django

# 实时查看日志
docker logs -f taicang-dvadmin3-django

# 或者查看最近100行
docker logs --tail 100 taicang-dvadmin3-django
```

### 容器操作

```bash
# 进入 Django 容器
docker exec -it taicang-dvadmin3-django bash

# 进入 Web 容器
docker exec -it taicang-dvadmin3-web sh

# 查看容器状态
docker ps | grep taicang

# 查看容器资源使用
docker stats taicang-dvadmin3-django
```

### Django 管理命令

```bash
# 执行 Django 命令
docker exec -it taicang-dvadmin3-django python manage.py <command>

# 示例：创建迁移
docker exec -it taicang-dvadmin3-django python manage.py makemigrations

# 示例：应用迁移
docker exec -it taicang-dvadmin3-django python manage.py migrate

# 示例：创建超级用户
docker exec -it taicang-dvadmin3-django python manage.py createsuperuser

# 示例：检查配置
docker exec -it taicang-dvadmin3-django python manage.py check

# 复制文件到容器
docker cp /home/bak/bus_datasys.sql taicang-dvadmin3-django:/tmp/bus_datasys.sql

# 复制 exec_sql_bst.py 文件到容器
docker cp /home/bak/exec_sql_bst.py taicang-dvadmin3-django:/backend/exec_sql_bst.py

# nohup后台执行 SQL 文件
docker exec taicang-dvadmin3-django bash -c "nohup python /backend/exec_sql_bst.py --file /tmp/bus_datasys.sql --schema bus_datasys --verbose > /tmp/sql_exec.log 2>&1 &"

# 监控日志，配合nohup使用
docker exec taicang-dvadmin3-django bash -c "tail -f /tmp/sql_exec.log"

# 在容器内部删除文件
docker exec taicang-dvadmin3-django rm -f /tmp/2.sql

# 执行 SQL（使用生产环境配置）
docker exec taicang-dvadmin3-django bash -c "cd /backend && python exec_sql.py --file /tmp/1.sql --host 2.35.131.124 --port 5432 --dbname shznjtgjxlyh --user shznjtgjxlyh --password 'shznjtgjxlyh@5611' --schema transit_data_hub_dev"

# 在容器内执行sql文件
docker exec taicang-dvadmin3-django bash -c "cd /backend && python exec_sql_bst.py --file /tmp/bus_datasys.sql"

# 在容器内执行sql文件，如果不需要跳过错误，用批量提交（性能更好）
docker exec taicang-dvadmin3-django bash -c "cd /backend && python exec_sql_bst.py --file /tmp/ddl_datas.sql --verbose --batch-size 10000"

# 在容器内执行sql文件，如果需要跳过错误，用 autocommit（每条单独提交）
docker exec taicang-dvadmin3-django bash -c "cd /backend && python exec_sql_bst.py --file /tmp/ddl_datas.sql --verbose --continue-on-error"

# 查询线路数量sql语句
docker exec taicang-dvadmin3-django bash -c 'cd /backend && python exec_sql.py --sql "SELECT COUNT(1) FROM tx_bus_routes"'

# 创建 bus_datasys 模式
docker exec taicang-dvadmin3-django bash -c 'cd /backend && python exec_sql.py --sql "CREATE SCHEMA \"bus_datasys\""'

# 清空 bus_datasys schema 并重新创建
docker exec taicang-dvadmin3-django bash -c "cd /backend && python exec_sql.py --sql \"DROP SCHEMA IF EXISTS bus_datasys CASCADE; CREATE SCHEMA bus_datasys;\" --host 2.35.131.124 --port 5432 --dbname shznjtgjxlyh --user shznjtgjxlyh --password 'shznjtgjxlyh@5611'"

# 查询 bus_datasys schema 下所有数据量大于 0 的表和记录数：
docker exec taicang-dvadmin3-django bash -c 'cd /backend && python -c "
import psycopg2
conn = psycopg2.connect(host=\"2.35.131.124\", port=5432, dbname=\"shznjtgjxlyh\", user=\"shznjtgjxlyh\", password=\"shznjtgjxlyh@5611\")
cur = conn.cursor()
cur.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema = '\''bus_datasys'\'' ORDER BY table_name;\")
tables = cur.fetchall()
print(\"表名 | 记录数\")
print(\"=\" * 60)
total_tables = 0
total_rows = 0
for (table_name,) in tables:
    try:
        cur.execute(f\"SELECT COUNT(*) FROM bus_datasys.\\\"{table_name}\\\";\")
        count = cur.fetchone()[0]
        if count > 0:
            print(f\"{table_name:<50} | {count:>15,}\")
            total_tables += 1
            total_rows += count
    except Exception as e:
        pass
print(\"=\" * 60)
print(f\"总计: {total_tables} 个表有数据，共 {total_rows:,} 条记录\")
conn.close()
"'

# 使用新端口39028重新运行容器
docker run -d \
  --name taicang-dvadmin3-web \
  -p 39028:8080 \
  -e BACKEND_HOST=2.35.106.11 \
  -e BACKEND_PORT=8000 \
  www.wys8fb8.top:8443/tai_cang_od/taicang-dvadmin3-web:1.2
  
# 后端启动命令
docker run -d \
  --name taicang-dvadmin3-django \
  -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  -e DJANGO_ENV=production \
  -e REDIS_HOST=2.35.106.11 \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD='tcGj@Bs2025!' \
  -v /opt/taicang/backend/media:/backend/media \
  -v /opt/taicang/logs:/var/log \
  www.wys8fb8.top:8443/tai_cang_od/taicang-dvadmin3-django:1.2
```

### 数据库操作

```bash
# 进入数据库命令行（默认数据库）
docker exec -it taicang-dvadmin3-django python manage.py dbshell

# 进入达梦数据库命令行（如果已配置）
docker exec -it taicang-dvadmin3-django python manage.py dbshell --database=dm
```

---

## 环境配置

### 数据库配置

编辑 `backend/conf/env.py` 配置数据库连接信息：

```python
# 默认数据库（Vastbase）
DATABASE_ENGINE = "dvadmin.database.vastbase"
DATABASE_NAME = 'vastbase'
DATABASE_HOST = '10.60.9.69'
DATABASE_PORT = 5432
DATABASE_USER = "tpcc"
DATABASE_PASSWORD = 'your_password'
```

### 功能开关

在 `backend/conf/env.py` 中配置：

```python
# 调试模式（影响 Swagger 是否启用）
DEBUG = True  # 开发环境
# DEBUG = False  # 生产环境

# 其他功能开关
ENABLE_LOGIN_ANALYSIS_LOG = True
LOGIN_NO_CAPTCHA_AUTH = True
```

### 环境变量（可选）

也可以通过 `docker-compose.yml` 中的环境变量传递配置，详见项目根目录的配置说明。

---

## 故障排查

### 查看服务日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看最近 100 行日志
docker-compose logs --tail=100

# 实时查看日志
docker-compose logs -f taicang-dvadmin3-django
```

### 常见问题

1. **容器无法启动**
   - 检查端口是否被占用：`netstat -an | grep 8000`
   - 查看容器日志：`docker-compose logs taicang-dvadmin3-django`

2. **数据库连接失败**
   - 检查 `backend/conf/env.py` 中的数据库配置
   - 确认数据库服务可访问

3. **Swagger 无法访问**
   - 检查 `DEBUG` 是否为 `True`
   - 查看 `backend/application/urls.py` 中的 Swagger 配置

4. **镜像构建失败**
   - 检查网络连接（需要下载依赖）
   - 查看构建日志：`docker-compose build --no-cache`

---

## 注意事项

1. **数据持久化**：`backend/media` 目录已挂载，上传的文件会持久化保存
2. **日志文件**：日志保存在 `logs/log/` 目录
3. **代码热更新**：`backend` 目录已挂载，修改代码后重启容器即可生效
4. **生产环境**：建议设置 `DEBUG=False` 并修改默认密码
5. **镜像版本**：当前使用 `1.0` 标签，升级时请更新版本号

---

## 相关文档

- [镜像构建与推送.md](./镜像构建与推送.md) - Harbor 镜像推送详细说明
- 项目根目录 `README.md` - 项目整体说明
