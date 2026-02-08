# -*- coding: utf-8 -*-

"""
系统常量定义
包含系统级别的常量配置

@author: 王晨
@Created on: 2025-10-17 11:20:53
@Remark: 系统常量定义，包含系统配置、状态码、通用设置等
"""

# ================================================= #
# ******************** 系统信息 ******************** #
# ================================================= #

# 系统标题
SYSTEM_TITLE = "太仓线网"

# 系统版本
SYSTEM_VERSION = "1.0.0"

# 系统描述
SYSTEM_DESCRIPTION = "太仓线网管理系统"

# 系统作者
SYSTEM_AUTHOR = "王晨"

# ================================================= #
# ******************** 状态码 ******************** #
# ================================================= #

# 通用状态码
STATUS_SUCCESS = 200
STATUS_CREATED = 201
STATUS_NO_CONTENT = 204
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_FORBIDDEN = 403
STATUS_NOT_FOUND = 404
STATUS_INTERNAL_ERROR = 500

# 业务状态码
STATUS_DATA_NOT_FOUND = 1001
STATUS_DATA_EXISTS = 1002
STATUS_DATA_INVALID = 1003
STATUS_OPERATION_FAILED = 1004

# ================================================= #
# ******************** 状态选择 ******************** #
# ================================================= #

# 通用状态选择
STATUS_CHOICES = [
    (True, '启用'),
    (False, '禁用'),
]

# 审核状态选择
AUDIT_STATUS_CHOICES = [
    ('pending', '待审核'),
    ('approved', '已通过'),
    ('rejected', '已拒绝'),
]

# 删除状态选择
DELETE_STATUS_CHOICES = [
    (False, '正常'),
    (True, '已删除'),
]

# ================================================= #
# ******************** 文件配置 ******************** #
# ================================================= #

# 文件上传限制
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5MB

# 允许的文件类型
ALLOWED_IMAGE_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
ALLOWED_DOCUMENT_TYPES = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
ALLOWED_VIDEO_TYPES = ['mp4', 'avi', 'mov', 'wmv', 'flv']

# 文件存储路径
UPLOAD_ROOT = 'uploads/'
IMAGE_UPLOAD_PATH = 'uploads/images/'
DOCUMENT_UPLOAD_PATH = 'uploads/documents/'
VIDEO_UPLOAD_PATH = 'uploads/videos/'

# ================================================= #
# ******************** 分页配置 ******************** #
# ================================================= #

# 默认分页大小
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# 分页大小选择
PAGE_SIZE_CHOICES = [
    (10, '10条/页'),
    (20, '20条/页'),
    (50, '50条/页'),
    (100, '100条/页'),
]

# ================================================= #
# ******************** 缓存配置 ******************** #
# ================================================= #

# 缓存过期时间（秒）
CACHE_TIMEOUT_SHORT = 300      # 5分钟
CACHE_TIMEOUT_MEDIUM = 1800    # 30分钟
CACHE_TIMEOUT_LONG = 3600      # 1小时
CACHE_TIMEOUT_DAY = 86400      # 1天

# 缓存键前缀
CACHE_PREFIX_SYSTEM = 'system:'
CACHE_PREFIX_USER = 'user:'
CACHE_PREFIX_DATA = 'data:'

# ================================================= #
# ******************** 日志配置 ******************** #
# ================================================= #

# 日志级别
LOG_LEVEL_DEBUG = 'DEBUG'
LOG_LEVEL_INFO = 'INFO'
LOG_LEVEL_WARNING = 'WARNING'
LOG_LEVEL_ERROR = 'ERROR'
LOG_LEVEL_CRITICAL = 'CRITICAL'

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ================================================= #
# ******************** 时间配置 ******************** #
# ================================================= #

# 时间格式
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'

# 时区
DEFAULT_TIMEZONE = 'Asia/Shanghai'

# ================================================= #
# ******************** 验证配置 ******************** #
# ================================================= #

# 密码强度要求
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 32

# 用户名规则
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 20

# 手机号验证
PHONE_REGEX = r'^1[3-9]\d{9}$'

# 邮箱验证
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# ================================================= #
# ******************** 导出配置 ******************** #
# ================================================= #

# 导出文件限制
EXPORT_MAX_ROWS = 10000
EXPORT_FILE_TYPES = ['xlsx', 'csv', 'json']

# 导出文件路径
EXPORT_PATH = 'exports/'
