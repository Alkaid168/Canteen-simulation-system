import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash
from app import create_app
from models import db, AdminUser, Window, SeatGroup, Seat, Dish, Student, SystemConfig


def init_db():
    app = create_app()
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("[OK] 数据库表创建完成")

        # 创建管理员账号
        if not AdminUser.query.filter_by(username='admin').first():
            admin = AdminUser(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            print("[OK] 管理员账号创建完成")
        else:
            print("[SKIP] 已存在管理员账号")

        # 创建窗口
        windows_data = [
            {'name': '窗口1', 'window_number': 1},
            {'name': '窗口2', 'window_number': 2},
            {'name': '窗口3', 'window_number': 3},
        ]
        for wd in windows_data:
            if not Window.query.filter_by(window_number=wd['window_number']).first():
                w = Window(
                    name=wd['name'],
                    window_number=wd['window_number'],
                    is_online=True
                )
                db.session.add(w)
                print(f"[OK] {wd['name']}已创建完成")
        
        