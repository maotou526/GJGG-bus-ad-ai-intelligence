'''
高德地图API统一工具类
官方文档：https://lbs.amap.com/api/webservice/summary
'''
from .base_client import GaodeBaseClient


class GaodeAPI(GaodeBaseClient):
    """高德地图API统一调用"""
    
    def district(self, params):
        """
        行政区划查询
        
        参数：
            params: 请求参数字典
                - keywords: 必需，查询关键字
                - subdistrict: 子级行政区，0-3
                - extensions: 'base' 或 'all'
        
        官方文档：https://lbs.amap.com/api/webservice/guide/api/district
        """
        return self._request('/v3/config/district', params)
    
    def regeo(self, params):
        """
        逆地理编码（经纬度 → 地址）
        
        参数：
            params: 请求参数字典
                - location: 必需，"经度,纬度"
                - extensions: 'base' 或 'all'
                - radius: 搜索半径（米）
                - roadlevel: 0(所有道路) 或 1(仅主干道)
        
        官方文档：https://lbs.amap.com/api/webservice/guide/api/georegeo
        """
        return self._request('/v3/geocode/regeo', params)
    
    def bus_stop(self, params):
        """
        公交站点查询
        
        参数：
            params: 请求参数字典
                - keywords: 必需，站点关键字
                - city: 可选，城市adcode
                - offset: 每页记录数，最大100
        
        官方文档：https://lbs.amap.com/api/webservice/guide/api/search#bus
        """
        return self._request('/v3/bus/stopname', params)
    
    def bus_line_name(self, params):
        """
        公交路线关键字查询
        
        参数：
            params: 请求参数字典
                - keywords: 必需，线路名称关键字
                - city: 必需，城市adcode（如：320000代表江苏省，320585代表太仓市）
                - offset: 可选，每页记录数，默认20，最大100
                - page: 可选，当前页数，默认1
                - extensions: 可选，'base'（基本信息）或'all'（详细信息），默认'base'
                - output: 可选，返回数据格式，'JSON'或'XML'，默认'JSON'
        
        返回：
            dict: 包含公交路线信息的字典
                - status: 返回状态，1表示成功
                - info: 返回状态说明
                - infocode: 返回状态码
                - buslines: 公交路线集合
                    - id: 唯一id
                    - type: 公交类型
                    - name: 线路名称
                    - polyline: 线路的坐标串
                    - citycode: 城市的adcode
                    - start_stop: 始发站
                    - end_stop: 终点站
        
        官方文档：https://lbs.amap.com/api/webservice/guide/api-advanced/bus-inquiry#t6
        
        示例：
            gaode = GaodeAPI()
            result = gaode.bus_line_name({
                'keywords': '101路',
                'city': '320000',  # 江苏省
                'extensions': 'base'
            })
        """
        return self._request('/v3/bus/linename', params)

