import os
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from models import db
from routes.auth import auth_bp
from routes.orders import orders_bp
from routes.admin import admin_bp


def create_app(config_class=Config):    # 创建后端服务
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化数据库
    db.init_app(app)

    # 打开 CORS 允许前端跨域请求
    CORS(app, supports_credentials=True)

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    @app.route('/')
    def index():
        return jsonify(success=True, message='Canteen backend is running.')
    
    # 全局错误处理器
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(success=False, error=str(e.description)), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(success=False, error='未授权'), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(success=False, error='禁止访问'), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(success=False, error='资源不存在'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(success=False, error='服务器内部错误'), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)