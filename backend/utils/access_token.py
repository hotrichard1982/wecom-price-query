import time
import threading
import requests
from .config import config


class AccessTokenManager:
    """access_token管理器（线程安全）"""
    def __init__(self):
        self.access_token = None
        self.expire_time = 0
        self._lock = threading.Lock()
        self.timeout = 10  # 请求超时时间（秒）
        self.max_retries = 3  # 最大重试次数
    
    def get_access_token(self):
        """获取access_token（线程安全）"""
        current_time = time.time()
        
        # 检查access_token是否有效（提前100秒刷新）
        with self._lock:
            if self.access_token and current_time < self.expire_time - 100:
                return self.access_token
        
        # 重新获取access_token
        return self._refresh_token()
    
    def _refresh_token(self):
        """刷新access_token，支持重试"""
        params = {
            'corpid': config.CORPID,
            'corpsecret': config.CORPSECRET
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    config.ACCESS_TOKEN_URL,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get('errcode') == 0:
                    access_token = result.get('access_token')
                    expire_time = time.time() + 7200
                    
                    with self._lock:
                        self.access_token = access_token
                        self.expire_time = expire_time
                    
                    return access_token
                else:
                    raise Exception(f'获取access_token失败: {result.get("errmsg")}')
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    # 指数退避重试
                    time.sleep(1 * (attempt + 1))
                else:
                    raise Exception(f'获取access_token失败: {str(e)}')


# 创建access_token管理器实例
token_manager = AccessTokenManager()
