'''
Description: Celery 启动命令说明
Version: 1.0
Author: AI Assistant
Date: 2025-11-19 16:30:00
LastEditors: AI Assistant
LastEditTime: 2025-11-19 16:30:00
'''

# Celery 启动命令

以下命令需在 `backend` 目录下执行，并确保已经激活虚拟环境。

## 启动 Worker（任务执行进程）

```powershell
celery -A application worker -l info -P solo
```

## 启动 Beat（定时调度进程）

```powershell
celery -A application beat -l info
```

> 提示：请在两个独立的终端中分别运行上述命令，并保持终端处于运行状态，以确保定时任务可以正常调度与执行。

