import multiprocessing
import os
import sys
import socket

root_path = os.getcwd()
sys.path.append(root_path)
import uvicorn
from application.settings import LOGGING


def get_local_ip():
    """获取本机IP地址"""
    try:
        # 创建一个UDP socket来获取本机IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 不需要真正连接，只是用来获取本机IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "无法获取IP"


if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    # 获取本机IP
    local_ip = get_local_ip()
    port = 8000
    
    print("=" * 60)
    print("🚀 Django服务器启动信息")
    print("=" * 60)
    print(f"📍 本地访问地址:   http://127.0.0.1:{port}/")
    print(f"🌐 局域网访问地址: http://{local_ip}:{port}/")
    print(f"📚 API文档地址:    http://{local_ip}:{port}/api/swagger/")
    print("=" * 60)
    print()
    
    workers = 4
    if os.sys.platform.startswith('win'):
        # Windows操作系统
        workers = None
    
    uvicorn.run(
        "application.asgi:application", 
        reload=False, 
        host="0.0.0.0", 
        port=port, 
        workers=workers,
        log_config=LOGGING
    )

