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
    fi && \
    if [ ! -f ./conf/env_prod.py ]; then \
        cp ./conf/env.prod.py ./conf/env_prod.py; \
    fi

# 暴露端口
EXPOSE 8000

# 直接启动 uvicorn 服务器（配置从 env.py 或 env.prod.py 读取）
CMD ["uvicorn", "application.asgi:application", "--port", "8000", "--host", "0.0.0.0", "--workers", "4"]