from flask import Blueprint, request, jsonify
from ..utils.api_client import api_client

# 创建蓝图
query_bp = Blueprint('query', __name__)

# 允许的查询字段白名单
ALLOWED_FILTER_FIELDS = {
    '产品名': 'OPERATOR_CONTAINS',
    '功率(KVA/KW)': 'OPERATOR_IS',
    '柴油发动机型号': 'OPERATOR_IS',
    '发电机型号': 'OPERATOR_IS'
}

# 必须排除的敏感字段
SENSITIVE_FIELDS = ['成本', '上浮指数', '报价']

# 最大查询参数长度
MAX_PARAM_LENGTH = 100


@query_bp.route('/query', methods=['POST'])
def query():
    """查询商品价格"""
    try:
        # 获取查询参数
        data = request.get_json()
        if data is None:
            data = {}
        
        # 验证输入参数
        for field_name in data:
            if field_name in ALLOWED_FILTER_FIELDS:
                value = data[field_name]
                if value and not isinstance(value, str):
                    return jsonify({
                        'success': False,
                        'message': f'{field_name}参数类型错误'
                    }), 400
                if value and len(str(value).strip()) > MAX_PARAM_LENGTH:
                    return jsonify({
                        'success': False,
                        'message': f'{field_name}长度不能超过{MAX_PARAM_LENGTH}字符'
                    }), 400
        
        # 构建过滤条件
        filter_spec = {
            "conditions": []
        }
        
        # 添加查询条件
        for field_name, operator in ALLOWED_FILTER_FIELDS.items():
            if data.get(field_name):
                filter_spec['conditions'].append({
                    "field_name": field_name,
                    "operator": operator,
                    "value": str(data.get(field_name)).strip()
                })
        
        # 调用API获取记录
        result = api_client.get_records(filter_spec if filter_spec['conditions'] else None)
        
        # 处理返回数据
        records = result.get('records', [])
        
        # 格式化数据
        formatted_records = []
        for record in records:
            values = record.get('values', {})
            formatted_record = {}
            
            # 计算报价
            quote = values.get('报价')
            
            # 如果报价不存在，计算报价
            if quote is None:
                # 获取成本和上浮指数
                cost = values.get('成本')
                float_index = values.get('上浮指数')
                
                if cost is not None and float_index is not None:
                    quote = cost + (cost * float_index / 100)
                    formatted_record['报价'] = round(quote, 2)
                else:
                    # 如果成本或上浮指数不存在，设置报价为0
                    formatted_record['报价'] = 0
            else:
                # 如果报价存在，直接使用
                formatted_record['报价'] = quote
            
            # 遍历所有字段，排除敏感字段
            for field_name, field_value in values.items():
                # 跳过成本、上浮指数和报价（报价已经处理）
                if field_name in SENSITIVE_FIELDS:
                    continue
                
                # 处理不同类型的字段值
                if isinstance(field_value, dict):
                    # 处理对象类型（如产品ID）
                    formatted_record[field_name] = field_value.get('text')
                elif isinstance(field_value, list):
                    # 处理数组类型（如产品名、功率等）
                    if field_value and isinstance(field_value[0], dict):
                        # 处理产品图片
                        if field_name == '产品图片' and field_value[0].get('image_url'):
                            formatted_record[field_name] = field_value[0].get('image_url')
                        else:
                            formatted_record[field_name] = field_value[0].get('text')
                    else:
                        formatted_record[field_name] = field_value
                else:
                    # 处理基本类型（如数字、字符串）
                    formatted_record[field_name] = field_value
            
            formatted_records.append(formatted_record)
        
        return jsonify({
            'success': True,
            'data': formatted_records,
            'total': len(formatted_records)
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': '查询失败，请稍后重试'
        }), 500
