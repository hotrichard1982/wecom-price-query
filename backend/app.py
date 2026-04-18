import os
from flask import Flask, jsonify
from flask_cors import CORS
from .routes.query import query_bp
from .utils.config import config

app = Flask(__name__)

# 配置CORS，支持环境变量配置允许的来源
cors_origins = os.getenv('CORS_ORIGINS')
if cors_origins:
    origins = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    CORS(app, origins=origins, supports_credentials=True)
else:
    CORS(app)

app.register_blueprint(query_bp, url_prefix='/api')

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
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
