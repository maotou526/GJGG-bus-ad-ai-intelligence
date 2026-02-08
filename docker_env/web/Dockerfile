# 构建阶段
FROM node:22.14.0-alpine AS builder

# 安装 pnpm
RUN npm install -g pnpm@10.6.2

WORKDIR /web

# 复制 package.json 和 pnpm-lock.yaml
COPY ./web/package.json ./web/pnpm-lock.yaml* ./

# 安装依赖（如果锁文件不同步，会自动更新）
RUN pnpm install --registry=https://registry.npmmirror.com

# 复制源代码（排除 node_modules，由 .dockerignore 处理）
COPY ./web/ .

# 构建生产版本
RUN pnpm build

# 运行阶段
FROM nginx:alpine

# 安装 envsubst（gettext 包提供）
RUN apk add --no-cache gettext

# 创建模板目录
RUN mkdir -p /etc/nginx/templates

# 复制 nginx 配置模板
COPY ./docker_env/nginx/my.conf.template /etc/nginx/templates/my.conf.template

# 复制启动脚本
COPY ./docker_env/web/nginx-entrypoint.sh /docker-entrypoint.d/nginx-entrypoint.sh
RUN chmod +x /docker-entrypoint.d/nginx-entrypoint.sh

# 从构建阶段复制构建产物
COPY --from=builder /web/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 8080

# 使用自定义启动脚本
CMD ["/docker-entrypoint.d/nginx-entrypoint.sh"]
