#!/bin/sh

# 设置默认值
BACKEND_HOST=${BACKEND_HOST:-dvadmin3-django}
BACKEND_PORT=${BACKEND_PORT:-8000}

# 使用 envsubst 替换模板中的变量
envsubst '${BACKEND_HOST} ${BACKEND_PORT}' < /etc/nginx/templates/my.conf.template > /etc/nginx/conf.d/default.conf

# 启动 nginx
exec nginx -g 'daemon off;'

