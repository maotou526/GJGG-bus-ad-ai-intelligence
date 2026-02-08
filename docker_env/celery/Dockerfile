FROM python:3.11.2-slim

# 设置工作目录
WORKDIR /backend

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 并安装 Python 依赖
COPY ./backend/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# 复制后端代码
COPY ./backend/ /backend/

# 复制环境配置（如果不存在则从示例创建）
RUN if [ ! -f ./conf/env.py ]; then \
        cp ./conf/env.example.py ./conf/env.py; \
    fi

# 更新环境配置中的 Redis 主机（使用环境变量，在运行时设置）
# 注意：Redis 主机地址通过环境变量 REDIS_HOST 在运行时设置

# 转换行尾符并设置启动脚本权限（如果存在）
RUN if [ -f docker_start.sh ]; then sed -i 's/\r$//' docker_start.sh && chmod +x docker_start.sh; fi

# 直接启动 Celery
# 日志配置使用 Django 的 LOGGING 设置（backend/application/settings.py）
# 日志文件：backend/logs/celery.log（每天自动切换）
CMD ["celery", "-A", "application", "worker", "-B", "--loglevel=info"]