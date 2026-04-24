import os
import hashlib
from datetime import timedelta
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from .models.db import db
from .routes.query import query_bp
from .routes.admin import admin_bp
from .utils.config import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__,
            static_folder=os.path.join(BASE_DIR, 'frontend'),
            static_url_path='',
            template_folder=os.path.join(BASE_DIR, 'frontend'))

app.config['SECRET_KEY'] = hashlib.sha256(os.urandom(32)).hexdigest()
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=4)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'data', 'data.db').replace('\\', '/')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
db.init_app(app)

with app.app_context():
    from .models.db import User, SystemSetting
    db.create_all()
    admin_exists = User.query.filter_by(is_admin=True).first()
    app.config['NEED_INIT'] = not admin_exists
    setting = SystemSetting.query.filter_by(key='app.access_token').first()
    if setting:
        app.config['ACCESS_TOKEN'] = setting.value
    else:
        default_token = os.getenv('token', '') or hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        db.session.add(SystemSetting(key='app.access_token', value=default_token, description='访问令牌'))
        db.session.add(SystemSetting(key='app.version', value='v260425', description='系统版本'))
        db.session.commit()
        app.config['ACCESS_TOKEN'] = default_token

cors_origins = os.getenv('CORS_ORIGINS')
if cors_origins:
    origins = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    CORS(app, origins=origins, supports_credentials=True)
else:
    CORS(app)

@app.before_request
def validate_access_token():
    if request.path.startswith('/admin/') or request.path.startswith('/api/admin/') or request.path == '/init':
        return None
    if request.path != '/' and not request.path.startswith('/api/'):
        return None
    token = request.args.get('token') or request.headers.get('X-Access-Token')
    access_token = app.config.get('ACCESS_TOKEN', '')
    if access_token and token != access_token:
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': '访问被拒绝：无效的访问Token'}), 403
        else:
            return send_from_directory(os.path.join(BASE_DIR, 'frontend'), '403.html'), 403
    return None

app.register_blueprint(query_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/admin/')
@app.route('/admin/<path:page>')
def admin_page(page='login.html'):
    return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'admin'), page if page else 'login.html')

@app.route('/init')
def init_page():
    return send_from_directory(os.path.join(BASE_DIR, 'frontend', 'admin'), 'login.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': '请求的资源不存在'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'message': '请求方法不允许'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': '服务器内部错误'}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_RUN_PORT', 5000))
    print(f"\n{'='*50}")
    print(f"🚀 商品价格查询系统 v260425")
    print(f"{'='*50}")
    if app.config.get('NEED_INIT'):
        print(f"📝 首次运行！请访问 /init 完成初始化")
        print(f"📱 地址: http://127.0.0.1:{port}/init")
    else:
        print(f"📱 地址: http://127.0.0.1:{port}")
    print(f"🔑 访问Token: {app.config.get('ACCESS_TOKEN', '')}")
    print()
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
