import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class Config:
    """配置类"""
    # 企业微信配置
    CORPID = os.getenv('corpid')
    CORPSECRET = os.getenv('corpsecret')
    
    # 智能表格配置
    DOCID = os.getenv('docid')
    SHEET_ID = os.getenv('sheet_id')
    
    # API配置
    ACCESS_TOKEN_URL = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    SMARTSHEET_API_URL = 'https://qyapi.weixin.qq.com/cgi-bin/wedoc/smartsheet/get_records'
    
    @classmethod
    def validate(cls):
        """验证必要配置是否存在"""
        required_fields = {
            'CORPID': cls.CORPID,
            'CORPSECRET': cls.CORPSECRET,
            'DOCID': cls.DOCID,
            'SHEET_ID': cls.SHEET_ID
        }
        missing = [name for name, value in required_fields.items() if not value]
        if missing:
            raise ValueError(f'缺少必要配置: {", ".join(missing)}。请在.env文件中配置这些参数。')
        return True


# 创建并验证配置实例
config = Config()
config.validate()
