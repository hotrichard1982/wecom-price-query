from flask import Blueprint, request, jsonify, session, current_app
from datetime import datetime
from functools import wraps
import bcrypt
import os
import hashlib
from ..models.db import db, User, Datasource, SystemSetting
from ..crypto_utils import encrypt_password, decrypt_password
from ..services.query_service import test_connection

admin_bp = Blueprint('admin', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'message': '未登录'}), 401
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'success': False, 'message': '请输入用户名和密码'}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    user.last_login = datetime.utcnow()
    db.session.commit()
    session['admin_logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username
    session.permanent = True
    return jsonify({'success': True, 'message': '登录成功', 'username': user.username})


@admin_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return jsonify({'success': True, 'message': '已退出'})


@admin_bp.route('/auth/check', methods=['GET'])
def check_auth():
    if session.get('admin_logged_in'):
        return jsonify({'success': True, 'username': session.get('username')})
    return jsonify({'success': False}), 401


@admin_bp.route('/init/setup', methods=['POST'])
def setup():
    if User.query.filter_by(is_admin=True).first():
        return jsonify({'success': False, 'message': '系统已初始化'}), 400
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or len(username) < 2:
        return jsonify({'success': False, 'message': '用户名至少2个字符'}), 400
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': '密码至少6个字符'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': '用户名已存在'}), 400
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(username=username, password_hash=password_hash, display_name=username, is_admin=True)
    db.session.add(user)
    existing_token = SystemSetting.query.filter_by(key='app.access_token').first()
    if not existing_token:
        token = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        db.session.add(SystemSetting(key='app.access_token', value=token, description='访问令牌'))
    db.session.add(SystemSetting(key='app.version', value='v260425', description='系统版本'))
    db.session.commit()
    current_app.config['NEED_INIT'] = False
    session['admin_logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username
    session.permanent = True
    token_val = existing_token.value if existing_token else token
    return jsonify({'success': True, 'message': '初始化成功', 'token': token_val})


@admin_bp.route('/datasources', methods=['GET'])
@login_required
def get_datasources():
    sources = Datasource.query.order_by(Datasource.id.desc()).all()
    result = []
    for s in sources:
        result.append({
            'id': s.id,
            'name': s.name,
            'db_type': s.db_type,
            'host': s.host,
            'port': s.port,
            'database_name': s.database_name,
            'db_username': s.db_username,
            'table_name': s.table_name,
            'description': s.description,
            'is_active': s.is_active,
            'created_at': s.created_at.isoformat() if s.created_at else None
        })
    return jsonify({'success': True, 'data': result})


@admin_bp.route('/datasources', methods=['POST'])
@login_required
def add_datasource():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400
    required = ['name', 'db_type', 'host', 'port', 'database_name', 'db_username', 'db_password', 'table_name']
    for field in required:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
    encrypted_pwd = encrypt_password(data['db_password'])
    ds = Datasource(
        name=data['name'],
        db_type=data['db_type'],
        host=data['host'],
        port=int(data['port']),
        database_name=data['database_name'],
        db_username=data['db_username'],
        db_password=encrypted_pwd,
        table_name=data['table_name'],
        description=data.get('description', '')
    )
    db.session.add(ds)
    db.session.commit()
    return jsonify({'success': True, 'message': '数据源添加成功', 'id': ds.id})


@admin_bp.route('/datasources/<int:id>', methods=['PUT'])
@login_required
def update_datasource(id):
    ds = Datasource.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400
    ds.name = data.get('name', ds.name)
    ds.db_type = data.get('db_type', ds.db_type)
    ds.host = data.get('host', ds.host)
    ds.port = int(data.get('port', ds.port))
    ds.database_name = data.get('database_name', ds.database_name)
    ds.db_username = data.get('db_username', ds.db_username)
    if data.get('db_password'):
        ds.db_password = encrypt_password(data['db_password'])
    ds.table_name = data.get('table_name', ds.table_name)
    ds.description = data.get('description', ds.description)
    ds.is_active = data.get('is_active', ds.is_active)
    db.session.commit()
    return jsonify({'success': True, 'message': '数据源更新成功'})


@admin_bp.route('/datasources/<int:id>', methods=['DELETE'])
@login_required
def delete_datasource(id):
    ds = Datasource.query.get_or_404(id)
    db.session.delete(ds)
    db.session.commit()
    return jsonify({'success': True, 'message': '数据源已删除'})


@admin_bp.route('/datasources/test', methods=['POST'])
@login_required
def test_datasource():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400
    class TempDS:
        pass
    ds = TempDS()
    ds.db_type = data['db_type']
    ds.host = data['host']
    ds.port = int(data.get('port', 3306))
    ds.database_name = data['database_name']
    ds.db_username = data['db_username']
    ds.db_password = data.get('db_password', '')
    success, msg = test_connection(ds)
    return jsonify({'success': success, 'message': msg})


@admin_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    settings = SystemSetting.query.all()
    data = {s.key: s.value for s in settings}
    data['username'] = session.get('username')
    return jsonify({'success': True, 'data': data})


@admin_bp.route('/settings/password', methods=['PUT'])
@login_required
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400
    old_pwd = data.get('old_password', '')
    new_pwd = data.get('new_password', '')
    user = User.query.get(session['user_id'])
    if not bcrypt.checkpw(old_pwd.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({'success': False, 'message': '当前密码错误'}), 400
    if len(new_pwd) < 6:
        return jsonify({'success': False, 'message': '新密码至少6个字符'}), 400
    user.password_hash = bcrypt.hashpw(new_pwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.session.commit()
    return jsonify({'success': True, 'message': '密码修改成功'})


@admin_bp.route('/settings/token', methods=['PUT'])
@login_required
def update_token():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求数据为空'}), 400
    new_token = data.get('token', '')
    if len(new_token) < 6:
        return jsonify({'success': False, 'message': 'Token至少6个字符'}), 400
    setting = SystemSetting.query.filter_by(key='app.access_token').first()
    if setting:
        setting.value = new_token
    else:
        db.session.add(SystemSetting(key='app.access_token', value=new_token, description='访问令牌'))
    db.session.commit()
    current_app.config['ACCESS_TOKEN'] = new_token
    return jsonify({'success': True, 'message': 'Token更新成功'})


@admin_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():
    ds_count = Datasource.query.count()
    active_count = Datasource.query.filter_by(is_active=True).count()
    version = SystemSetting.query.filter_by(key='app.version').first()
    return jsonify({
        'success': True,
        'data': {
            'datasource_count': ds_count,
            'active_count': active_count,
            'version': version.value if version else 'v260425'
        }
    })
