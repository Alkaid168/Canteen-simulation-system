import os
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from models import db


def create_app(config_class=Config):    # 创建后端服务
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化数据库
    db.init_app(app)

    # 打开 CORS 允许前端跨域请求
    CORS(app, supports_credentials=True)

    @app.route('/')
    def index():
        return jsonify(success=True, message='Canteen backend is running.')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)