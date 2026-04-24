from flask import Blueprint, request, jsonify, current_app
from ..models.db import Datasource, SystemSetting
from ..services.query_service import fetch_records

query_bp = Blueprint('query', __name__)


@query_bp.route('/query', methods=['POST'])
def query():
    try:
        ds_id = request.args.get('datasource_id', type=int)
        data = request.get_json() or {}
        if not ds_id:
            active = Datasource.query.filter_by(is_active=True).first()
            if not active:
                return jsonify({'success': True, 'data': [], 'total': 0})
            ds_id = active.id
        ds = Datasource.query.get(ds_id)
        if not ds:
            return jsonify({'success': False, 'message': '数据源不存在'}), 404
        filters = {
            'keyword': data.get('产品名', ''),
            'power': data.get('功率(KVA/KW)', ''),
            'engine_model': data.get('柴油发动机型号', ''),
            'generator_model': data.get('发电机型号', '')
        }
        filters = {k: v for k, v in filters.items() if v}
        records = fetch_records(ds, filters)
        return jsonify({'success': True, 'data': records, 'total': len(records)})
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'}), 500


@query_bp.route('/datasources', methods=['GET'])
def get_datasources():
    sources = Datasource.query.filter_by(is_active=True).all()
    token = current_app.config.get('ACCESS_TOKEN', '')
    result = []
    for s in sources:
        result.append({
            'id': s.id,
            'name': s.name,
            'db_type': s.db_type,
            'token': token
        })
    if not result:
        return jsonify({'success': True, 'data': [], 'total': 0, 'token': token})
    return jsonify({'success': True, 'data': result, 'total': len(result), 'token': token})


@query_bp.route('/suggest', methods=['GET'])
def suggest():
    datasource_id = request.args.get('datasource_id', type=int)
    keyword = request.args.get('keyword', '').strip()
    if not datasource_id or not keyword:
        return jsonify({'success': True, 'data': []})
    ds = Datasource.query.get(datasource_id)
    if not ds:
        return jsonify({'success': False, 'message': '数据源不存在'}), 404
    try:
        from sqlalchemy import create_engine, text
        from ..crypto_utils import decrypt_password
        password = decrypt_password(ds.db_password)
        if ds.db_type == 'mysql':
            url = f'mysql+pymysql://{ds.db_username}:{password}@{ds.host}:{ds.port}/{ds.database_name}'
        else:
            url = f'postgresql://{ds.db_username}:{password}@{ds.host}:{ds.port}/{ds.database_name}'
        engine = create_engine(url)
        with engine.connect() as conn:
            query = f"SELECT DISTINCT `产品名` FROM {ds.table_name} WHERE `产品名` LIKE :kw LIMIT 10"
            result = conn.execute(text(query), {'kw': f'%{keyword}%'})
            suggestions = [row[0] for row in result.fetchall() if row[0]]
        return jsonify({'success': True, 'data': suggestions})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
