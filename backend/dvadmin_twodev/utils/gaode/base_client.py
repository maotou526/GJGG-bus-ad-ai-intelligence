'''
Description: 高德地图API基础客户端
Version: 1.0
Date: 2025-01-23
'''
import os
import re
import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _get_amap_api_key():
    """
    获取高德API密钥，避免循环导入问题
    优先从环境变量获取，其次直接解析配置文件（不触发Django加载）
    """
    # 优先从环境变量获取
    api_key = os.environ.get('AMAP_API_KEY')
    if api_key:
        return api_key
    
    # 直接解析配置文件获取 AMAP_API_KEY（避免import触发Django加载）
    try:
        # 查找 conf/env.py 文件
        current_file = Path(__file__).resolve()
        # 向上查找 backend 目录
        backend_dir = current_file.parent
        while backend_dir.name != 'backend' and backend_dir.parent != backend_dir:
            backend_dir = backend_dir.parent
            if (backend_dir / 'manage.py').exists():
                break
        
        env_file = backend_dir / 'conf' / 'env.py'
        if env_file.exists():
            content = env_file.read_text(encoding='utf-8')
            # 使用正则表达式提取 AMAP_API_KEY
            match = re.search(r'AMAP_API_KEY\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except Exception as e:
        logger.warning(f"读取配置文件获取AMAP_API_KEY失败: {e}")
    
    return None


class GaodeBaseClient:
    """
    高德地图API基础客户端
    提供统一的HTTP请求处理和错误处理
    
    官方文档：https://lbs.amap.com/api/webservice/summary
    """
    
    BASE_URL = 'https://restapi.amap.com'
    DEFAULT_TIMEOUT = 30  # 默认超时时间（秒）
    
    def __init__(self, api_key=None, timeout=None):
        """
        初始化高德地图基础客户端
        
        Args:
            api_key (str, optional): 高德API密钥，不传则使用配置文件中的密钥
            timeout (int, optional): 请求超时时间（秒），默认30秒
        """
        # 延迟获取API密钥，避免循环导入
        self.api_key = api_key or _get_amap_api_key()
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        
        if not self.api_key:
            raise ValueError("缺少高德地图API密钥，请在配置文件中设置 AMAP_API_KEY 或设置环境变量")
    
    def _request(self, endpoint, params=None, method='GET'):
        """
        统一的HTTP请求方法
        
        Args:
            endpoint (str): API端点路径（如：/v3/config/district）
            params (dict, optional): 请求参数
            method (str, optional): 请求方法，默认GET
            
        Returns:
            dict: API返回的JSON数据
            
        Raises:
            requests.Timeout: 请求超时
            requests.RequestException: 网络请求失败
            Exception: API返回错误状态
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # 添加API密钥到参数
        if params is None:
            params = {}
        params['key'] = self.api_key
        
        try:
            logger.debug(f"[高德API] 请求: {method} {url}, 参数: {params}")
            
            if method.upper() == 'GET':
                response = requests.get(url, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, data=params, timeout=self.timeout)
            else:
                raise ValueError(f"不支持的请求方法: {method}")
            
            # 解析JSON响应
            data = response.json()
            
            # 检查API返回状态
            # 高德API约定：status='1' 表示成功
            if data.get('status') != '1':
                error_info = data.get('info', '未知错误')
                error_code = data.get('infocode', '')
                logger.error(f"[高德API] 请求失败: {error_info} (错误码: {error_code})")
                raise Exception(f"高德地图API错误: {error_info}")
            
            logger.debug(f"[高德API] 请求成功")
            return data
            
        except requests.Timeout:
            logger.error(f"[高德API] 请求超时 (超时时间: {self.timeout}秒)")
            raise
        except requests.RequestException as e:
            logger.error(f"[高德API] 网络请求失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"[高德API] 请求处理失败: {str(e)}")
            raise

