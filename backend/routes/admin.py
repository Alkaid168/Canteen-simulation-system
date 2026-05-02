import datetime
from functools import wraps

from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash

from models import (
    db, Dish, Window, SeatGroup, Seat, Student,
    DailyMenu, DishPrediction, Order, OrderSeat, SystemConfig
)

admin_bp = Blueprint('admin', __name__)


# 管理员登录状态校验
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_username'):
            return jsonify(success=False, error='未登录'), 401
        return f(*args, **kwargs)
    return decorated


# 菜品管理
@admin_bp.route('/dishes', methods=['GET'])
@admin_required
def get_dishes():
    dishes = Dish.query.all()
    return jsonify(success=True, data=[{
        'id': d.id,
        'name': d.name,
        'price': float(d.price),
        'image_url': d.image_url,
        'is_active': d.is_active,
    } for d in dishes])


@admin_bp.route('/dishes', methods=['POST'])
@admin_required
def create_dish():
    body = request.get_json(silent=True) or {}
    dish = Dish(
        name=body['name'],
        price=body['price'],
        image_url=body.get('image_url', ''),
        is_active=True,
    )
    db.session.add(dish)
    db.session.commit()
    return jsonify(success=True, data={'id': dish.id}), 201


@admin_bp.route('/dishes/<int:dish_id>', methods=['PUT'])
@admin_required
def update_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    body = request.get_json(silent=True) or {}
    for field in ('name', 'price', 'image_url', 'is_active'):
        if field in body:
            setattr(dish, field, body[field])
    db.session.commit()
    return jsonify(success=True)


@admin_bp.route('/dishes/<int:dish_id>', methods=['DELETE'])
@admin_required
def delete_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    dish.is_active = False
    db.session.commit()
    return jsonify(success=True)


# 窗口管理
@admin_bp.route('/windows', methods=['GET'])
@admin_required
def get_windows():
    windows = Window.query.all()
    return jsonify(success=True, data=[{
        'id': w.id,
        'name': w.name,
        'window_number': w.window_number,
        'is_online': w.is_online,
    } for w in windows])


@admin_bp.route('/windows', methods=['POST'])
@admin_required
def create_window():
    body = request.get_json(silent=True) or {}
    window = Window(
        name=body['name'],
        window_number=body['window_number'],
        is_online=body.get('is_online', True),
    )
    db.session.add(window)
    db.session.commit()
    return jsonify(success=True, data={'id': window.id}), 201


@admin_bp.route('/windows/<int:window_id>', methods=['PUT'])
@admin_required
def update_window(window_id):
    window = Window.query.get_or_404(window_id)
    body = request.get_json(silent=True) or {}
    for field in ('name', 'window_number', 'is_online'):
        if field in body:
            setattr(window, field, body[field])
    db.session.commit()
    return jsonify(success=True)


@admin_bp.route('/windows/<int:window_id>', methods=['DELETE'])
@admin_required
def delete_window(window_id):
    window = Window.query.get_or_404(window_id)
    db.session.delete(window)
    db.session.commit()
    return jsonify(success=True)


# 座位组管理
@admin_bp.route('/seat-groups', methods=['GET'])
@admin_required
def get_seat_groups():
    groups = SeatGroup.query.all()
    return jsonify(success=True, data=[{
        'id': g.id,
        'name': g.name,
        'capacity': g.capacity,
        'seats': [{
            'id': s.id,
            'seat_number': s.seat_number,
            'is_occupied': s.is_occupied,
        } for s in g.seats],
    } for g in groups])


@admin_bp.route('/seat-groups', methods=['POST'])
@admin_required
def create_seat_group():
    body = request.get_json(silent=True) or {}
    group = SeatGroup(
        name=body['name'],
        capacity=body['capacity'],
    )
    db.session.add(group)
    db.session.commit()
    return jsonify(success=True, data={'id': group.id}), 201


@admin_bp.route('/seat-groups/<int:group_id>', methods=['DELETE'])
@admin_required
def delete_seat_group(group_id):
    group = SeatGroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    return jsonify(success=True)


# 座位管理
@admin_bp.route('/seats', methods=['GET'])
@admin_required
def get_seats():
    seats = Seat.query.all()
    return jsonify(success=True, data=[{
        'id': s.id,
        'seat_number': s.seat_number,
        'group_id': s.group_id,
        'is_occupied': s.is_occupied,
    } for s in seats])


@admin_bp.route('/seats', methods=['POST'])
@admin_required
def create_seat():
    body = request.get_json(silent=True) or {}
    seat = Seat(
        seat_number=body['seat_number'],
        group_id=body['group_id'],
        is_occupied=body.get('is_occupied', False),
    )
    db.session.add(seat)
    db.session.commit()
    return jsonify(success=True, data={'id': seat.id}), 201


@admin_bp.route('/seats/<int:seat_id>', methods=['PUT'])
@admin_required
def update_seat(seat_id):
    seat = Seat.query.get_or_404(seat_id)
    body = request.get_json(silent=True) or {}
    for field in ('seat_number', 'group_id', 'is_occupied'):
        if field in body:
            setattr(seat, field, body[field])
    db.session.commit()
    return jsonify(success=True)


@admin_bp.route('/seats/<int:seat_id>', methods=['DELETE'])
@admin_required
def delete_seat(seat_id):
    seat = Seat.query.get_or_404(seat_id)
    db.session.delete(seat)
    db.session.commit()
    return jsonify(success=True)


# 学生管理
@admin_bp.route('/students', methods=['GET'])
@admin_required
def get_students():
    students = Student.query.all()
    return jsonify(success=True, data=[{
        'id': s.id,
        'student_id': s.student_id,
        'name': s.name,
        'created_at': s.created_at.isoformat() if s.created_at else None,
    } for s in students])


@admin_bp.route('/students', methods=['POST'])
@admin_required
def create_student():
    body = request.get_json(silent=True) or {}
    student = Student(
        student_id=body['student_id'],
        name=body['name'],
        password_hash=generate_password_hash(body['password']),
    )
    db.session.add(student)
    db.session.commit()
    return jsonify(success=True, data={'id': student.id}), 201


@admin_bp.route('/students/<int:student_id>', methods=['PUT'])
@admin_required
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    body = request.get_json(silent=True) or {}
    if 'name' in body:
        student.name = body['name']
    if 'student_id' in body:
        student.student_id = body['student_id']
    if 'password' in body:
        student.password_hash = generate_password_hash(body['password'])
    db.session.commit()
    return jsonify(success=True)


@admin_bp.route('/students/<int:student_id>', methods=['DELETE'])
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify(success=True)


# 每日菜单与预测管理
@admin_bp.route('/daily-menu', methods=['GET'])
@admin_required
def get_daily_menu():
    today = datetime.date.today()
    menus = DailyMenu.query.filter_by(date=today).all()
    return jsonify(success=True, data=[{
        'id': m.id,
        'dish_id': m.dish_id,
        'dish_name': m.dish.name if m.dish else None,
        'window_id': m.window_id,
        'window_name': m.window.name if m.window else None,
        'stock': m.stock,
        'is_sold_out': m.is_sold_out,
    } for m in menus])


@admin_bp.route('/daily-menu/<int:menu_id>', methods=['PUT'])
@admin_required
def update_daily_menu(menu_id):
    menu = DailyMenu.query.get_or_404(menu_id)
    body = request.get_json(silent=True) or {}
    for field in ('stock', 'is_sold_out', 'window_id'):
        if field in body:
            setattr(menu, field, body[field])
    db.session.commit()
    return jsonify(success=True)


@admin_bp.route('/predictions', methods=['GET'])
@admin_required
def get_predictions():
    today = datetime.date.today()
    preds = DishPrediction.query.filter_by(date=today).all()
    return jsonify(success=True, data=[{
        'id': p.id,
        'dish_id': p.dish_id,
        'predicted_quantity': p.predicted_quantity,
        'adjusted_quantity': p.adjusted_quantity,
        'created_at': p.created_at.isoformat() if p.created_at else None,
    } for p in preds])


@admin_bp.route('/prediction/<int:pred_id>/adjust', methods=['PUT'])
@admin_required
def adjust_prediction(pred_id):
    pred = DishPrediction.query.get_or_404(pred_id)
    body = request.get_json(silent=True) or {}
    adjusted = body['adjusted_quantity']
    pred.adjusted_quantity = adjusted

    menu = DailyMenu.query.filter_by(dish_id=pred.dish_id, date=pred.date).first()
    if menu:
        menu.stock = adjusted
        menu.is_sold_out = adjusted <= 0

    db.session.commit()
    return jsonify(success=True, data={
        'id': pred.id,
        'dish_id': pred.dish_id,
        'predicted_quantity': pred.predicted_quantity,
        'adjusted_quantity': pred.adjusted_quantity,
    })


# 订单管理
@admin_bp.route('/orders', methods=['GET'])
@admin_required
def admin_get_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify(success=True, data=[{
        'id': o.id,
        'student_id': o.student.student_id if o.student else None,
        'window_id': o.window_id,
        'window_name': o.window.name if o.window else None,
        'is_completed': o.is_completed,
        'created_at': o.created_at.isoformat() if o.created_at else None,
        'completed_at': o.completed_at.isoformat() if o.completed_at else None,
    } for o in orders])


@admin_bp.route('/orders/<int:order_id>/complete', methods=['PUT'])
@admin_required
def complete_order(order_id):
    order = Order.query.get_or_404(order_id)

    if order.is_completed:
        return jsonify(success=True, data={'order_id': order.id, 'is_completed': True})

    order.is_completed = True
    order.completed_at = datetime.datetime.now(datetime.timezone.utc)

    order_seats = OrderSeat.query.filter_by(order_id=order.id).all()
    for os in order_seats:
        seat = Seat.query.get(os.seat_id)
        if seat:
            seat.is_occupied = False

    db.session.commit()
    return jsonify(success=True, data={
        'order_id': order.id,
        'is_completed': order.is_completed,
        'completed_at': order.completed_at.isoformat() if order.completed_at else None,
    })


# 运营报表
@admin_bp.route('/reports/orders', methods=['GET'])
@admin_required
def report_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify(success=True, data=[{
        'id': o.id,
        'student_id': o.student.student_id if o.student else None,
        'window_id': o.window_id,
        'window_name': o.window.name if o.window else None,
        'is_completed': o.is_completed,
        'created_at': o.created_at.isoformat() if o.created_at else None,
    } for o in orders])


@admin_bp.route('/reports/daily', methods=['GET'])
@admin_required
def report_daily():
    from sqlalchemy import func

    rows = (
        db.session.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('count')
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )
    return jsonify(success=True, data=[
        {'date': str(r.date), 'count': r.count} for r in rows
    ])


@admin_bp.route('/reports/windows', methods=['GET'])
@admin_required
def report_windows():
    from sqlalchemy import func

    rows = (
        db.session.query(Order.window_id, func.count(Order.id).label('count'))
        .filter(Order.is_completed == True)
        .group_by(Order.window_id)
        .all()
    )
    windows = {w.id: w.name for w in Window.query.all()}
    return jsonify(success=True, data=[{
        'window_id': r.window_id,
        'window_name': windows.get(r.window_id),
        'completed_orders': r.count,
    } for r in rows])


@admin_bp.route('/reports/seats', methods=['GET'])
@admin_required
def report_seats():
    groups = SeatGroup.query.all()
    data = []
    for g in groups:
        total = len(g.seats)
        occupied = sum(1 for s in g.seats if s.is_occupied)
        data.append({
            'group_id': g.id,
            'group_name': g.name,
            'total': total,
            'occupied': occupied,
        })
    return jsonify(success=True, data=data)


# 系统配置
@admin_bp.route('/config', methods=['GET'])
@admin_required
def get_config():
    configs = SystemConfig.query.all()
    return jsonify(success=True, data=[{
        'id': c.id,
        'key': c.key,
        'value': c.value,
        'description': c.description,
    } for c in configs])


@admin_bp.route('/config', methods=['PUT'])
@admin_required
def update_config():
    body = request.get_json(silent=True) or {}
    for key, value in body.items():
        cfg = SystemConfig.query.filter_by(key=key).first()
        if cfg:
            cfg.value = str(value)
        else:
            db.session.add(SystemConfig(key=key, value=str(value)))
    db.session.commit()
    return jsonify(success=True)
