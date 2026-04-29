import os

# backend文件夹的绝对路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bjtu-canteen-secret-key-2026')

    # SQLite数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'canteen.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭修改追踪功能

    # APScheduler
    SCHEDULER_API_ENABLED = False   # 关闭自带的管理接口（自带的会通过浏览器管理）
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'    # 定时任务按上海时区计算

    # 预测任务触发的天数间隔
    PREDICTION_INTERVAL_DAYS = 3