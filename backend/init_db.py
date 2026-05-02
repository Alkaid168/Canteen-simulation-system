import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.security import generate_password_hash
from app import create_app
from models import db, AdminUser, Window, SeatGroup, Seat, Dish, Student, DailyMenu


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
                print(f"[OK] {wd['name']}创建完成")
        
        # 创建座位组与座位
        for i in range(1, 11):
            group_name = f'A区{i}组'
            if not SeatGroup.query.filter_by(name=group_name).first():
                g = SeatGroup(name=group_name, capacity=4)
                db.session.add(g)
                db.session.flush()
                for j in range(1, 5):
                    seat = Seat(
                        seat_number=f'A{i}-{j}',
                        group_id=g.id,
                        is_occupied=False
                    )
                    db.session.add(seat)
                print(f"[OK] {group_name}座位组创建完成")
        
        # 创建菜品
        db.session.flush()
        dishes_data = [
            {'name': '红烧肉盖饭', 'price': 12.00, 'image_url': '/static/images/hongshaorou.png'},
            {'name': '番茄鸡蛋面', 'price': 7.00, 'image_url': '/static/images/fanqiejidanmian.png'},
            {'name': '辣椒炒肉拌面', 'price': 12.00, 'image_url': '/static/images/lajiaochaorou.png'},
            {'name': '猪肉大葱水饺', 'price': 16.00, 'image_url': '/static/images/zhuroudacong.png'},
            {'name': '黄焖鸡米饭', 'price': 12.00, 'image_url': '/static/images/huangmenjimifan.png'},
        ]
        for dish in dishes_data:
            if not Dish.query.filter_by(name=dish['name']).first():
                dd = Dish(**dish, is_active=True)
                db.session.add(dd)
                print(f"[OK] {dish['name']}菜品创建完成")


        # 初始化今日菜单与库存
        db.session.flush()
        today = datetime.date.today()
        windows = Window.query.order_by(Window.window_number.asc()).all()
        dishes = Dish.query.order_by(Dish.id.asc()).all()
        default_stock = 50

        if windows and dishes:
            for idx, dish in enumerate(dishes):
                window = windows[idx % len(windows)]
                existed = DailyMenu.query.filter_by(
                    dish_id=dish.id,
                    window_id=window.id,
                    date=today
                ).first()
                if not existed:
                    db.session.add(DailyMenu(
                        dish_id=dish.id,
                        window_id=window.id,
                        date=today,
                        stock=default_stock,
                        is_sold_out=False
                    ))
                    print(f"[OK] 今日菜单创建: {dish.name} -> {window.name}, 库存{default_stock}")

        # 创建学生账号
        students_data = [
            {'student_id': '24281143', 'name': '王禹凡', 'password': 'wyfnb'},
            {'student_id': '24281135', 'name': '李佳睿', 'password': 'ljrnb'},
            {'student_id': '24281170', 'name': '任笑语', 'password': 'rxynb'},
        ]
        for sd in students_data:
            if not Student.query.filter_by(student_id=sd['student_id']).first():
                s = Student(
                    student_id=sd['student_id'],
                    name=sd['name'],
                    password_hash=generate_password_hash(sd['password'])
                )
                db.session.add(s)
                print(f"[OK] {sd['name']}账号创建完成")
        
        db.session.commit()
        print("[OK] 数据库创建完成")


if __name__ == '__main__':
    init_db()