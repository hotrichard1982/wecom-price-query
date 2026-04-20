import os
import hashlib
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from .routes.query import query_bp
from .utils.config import config

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
            static_folder=os.path.join(BASE_DIR, 'frontend'),
            static_url_path='')

# 配置CORS，支持环境变量配置允许的来源
cors_origins = os.getenv('CORS_ORIGINS')
if cors_origins:
    origins = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    CORS(app, origins=origins, supports_credentials=True)
else:
    CORS(app)

# 生成token（如果.env中没有配置，则自动生成一个）
if not config.ACCESS_TOKEN:
    config.ACCESS_TOKEN = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
    print(f"🔑 自动生成访问Token: {config.ACCESS_TOKEN}")
    print(f"💡 请将此Token添加到.env文件的token字段中")

@app.before_request
def validate_access_token():
    """验证访问token，防止未授权访问"""
    # 静态文件（CSS、JS、图片等）不需要验证
    if request.path != '/' and not request.path.startswith('/api/'):
        return None
    
    # 获取请求中的token（支持URL参数和Header两种方式）
    token = request.args.get('token') or request.headers.get('X-Access-Token')
    
    # 如果配置了token，则必须验证
    if config.ACCESS_TOKEN and token != config.ACCESS_TOKEN:
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'message': '访问被拒绝：无效的访问Token'
            }), 403
        else:
            return send_from_directory(
                os.path.join(BASE_DIR, 'frontend'),
                '403.html'
            ), 403
    
    return None

app.register_blueprint(query_bp, url_prefix='/api')

@app.route('/')
def index():
    """返回前端首页"""
    return send_from_directory(app.static_folder, 'index.html')

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
    print(f"\n🔑 访问Token: {config.ACCESS_TOKEN}")
    print(f"📝 完整访问地址: http://127.0.0.1:5000/?token={config.ACCESS_TOKEN}\n")
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
