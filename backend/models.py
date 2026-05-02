from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):    # 学生表
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    orders = db.relationship('Order', backref='student', lazy=True)


class Window(db.Model):     # 窗口表
    __tablename__ = 'windows'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    window_number = db.Column(db.Integer, unique=True, nullable=False, index=True)
    is_online = db.Column(db.Boolean, default=True, nullable=False)

    orders = db.relationship('Order', backref='window', lazy=True)


class SeatGroup(db.Model):  # 座位组表
    __tablename__ = 'seat_groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    seats = db.relationship('Seat', backref='group', lazy=True)


class Seat(db.Model):       # 座位表
    __tablename__ = 'seats'

    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(20), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('seat_groups.id'), nullable=False, index=True)
    is_occupied = db.Column(db.Boolean, default=False, nullable=False)


class Dish(db.Model):       # 菜品表
    __tablename__ = 'dishes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)


class DailyMenu(db.Model):  # 每日菜单表
    __tablename__ = 'daily_menu'

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False, index=True)
    window_id = db.Column(db.Integer, db.ForeignKey('windows.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    stock = db.Column(db.Integer, nullable=False, default=0)
    is_sold_out = db.Column(db.Boolean, default=False, nullable=False)

    dish = db.relationship('Dish', backref='daily_menus', lazy=True)
    window = db.relationship('Window', backref='daily_menus', lazy=True)


class Order(db.Model):      # 订单表
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    window_id = db.Column(db.Integer, db.ForeignKey('windows.id'), nullable=True, index=True)
    party_size = db.Column(db.Integer, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    order_dishes = db.relationship('OrderDish', backref='order', lazy=True)
    order_seats = db.relationship('OrderSeat', backref='order', lazy=True)


class OrderDish(db.Model):  # 订单菜品表
    __tablename__ = 'order_dishes'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(6, 2), nullable=False)


class OrderSeat(db.Model):  # 订单座位表
    __tablename__ = 'order_seats'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, index=True)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)


class DishSales(db.Model):  # 菜品销量表
    __tablename__ = 'dish_sales'

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)


class DishPrediction(db.Model):     # 菜品预测表
    __tablename__ = 'dish_predictions'

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    predicted_quantity = db.Column(db.Integer, nullable=False)  # 预测出餐量
    adjusted_quantity = db.Column(db.Integer, nullable=True)    # 管理员调整后出餐量
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class SystemConfig(db.Model):       # 系统配置表
    __tablename__ = 'system_config'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)


class AdminUser(db.Model):           # 管理员用户表
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))