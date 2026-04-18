import requests
from .access_token import token_manager
from .config import config


class APIClient:
    """API客户端"""
    def __init__(self):
        self.token_manager = token_manager
        self.timeout = 30  # 请求超时时间（秒）
        self.max_retries = 2  # 最大重试次数
    
    def get_records(self, filter_spec=None):
        """获取智能表格记录"""
        # 获取access_token
        access_token = self.token_manager.get_access_token()
        
        # 构建请求URL
        url = f"{config.SMARTSHEET_API_URL}?access_token={access_token}"
        
        # 构建请求体
        data = {
            "docid": config.DOCID,
            "sheet_id": config.SHEET_ID
        }
        
        # 添加过滤条件
        if filter_spec:
            data["filter_spec"] = filter_spec
        
        # 发送请求（支持重试）
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    url,
                    json=data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get('errcode') == 0:
                    return result
                else:
                    err_msg = result.get('errmsg', '未知错误')
                    if attempt < self.max_retries:
                        continue
                    raise Exception(f'获取记录失败: {err_msg}')
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    continue
                raise Exception('请求超时，请检查网络连接')
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    continue
                raise


# 创建API客户端实例
api_client = APIClient()
