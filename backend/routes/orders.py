import datetime

from flask import Blueprint, request, session, jsonify

from models import db, Student, Order, OrderDish, OrderSeat, DailyMenu, Dish, Window, Seat
from utils.dispatch_algo import assign_window, assign_seats

orders_bp = Blueprint('orders_bp', __name__)


# 创建订单
@orders_bp.route('/orders', methods=['POST'])
def create_order():
    # 验证登录状态
    student_id = session.get('student_id')
    if not student_id:
        return jsonify(success=False, error='未登录'), 401
    
    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify(success=False, error='状态校验失败'), 401
    
    # 验证就餐人数
    data = request.get_json(silent=True) or {}
    party_size = data.get('party_size')
    items = data.get('items', [])
    if not isinstance(party_size, int) or not (1 <= party_size <= 4):
        return jsonify(success=False, error='就餐人数非法'), 400
    
    # 检验菜品库存
    today = datetime.date.today()
    menu_entries = []
    for item in items:
        dish_id = item.get('dish_id')
        quantity = item.get('quantity', 0)

        menu = DailyMenu.query.filter_by(dish_id=dish_id, date=today).first()
        if not menu or menu.is_sold_out:
            return jsonify(success=False, error='菜品不可用'), 400
        if menu.stock < quantity:
            return jsonify(success=False, error='菜品库存不足'), 400
        
        menu_entries.append((menu, item))

    # 分配窗口
    window_id = assign_window(db.session)
    if window_id is None:
        return jsonify(success=False, error='暂无可用窗口'), 503
    
    # 创建订单
    order = Order(
        student_id=student.id,
        window_id=window_id,
        party_size=party_size,
        is_completed=False
    )
    db.session.add(order)
    db.session.flush()

    # 创建 OrderDish 并扣减库存
    for menu, item in menu_entries:
        dish = Dish.query.get(item['dish_id'])
        order_dish = OrderDish(
            order_id=order.id,
            dish_id=item['dish_id'],
            quantity=item['quantity'],
            price=dish.price
        )
        db.session.add(order_dish)

        menu.stock -= item['quantity']

    # 分配座位
    seat_ids = assign_seats(db.session, order.id, party_size)
    if not seat_ids:
        db.session.rollback()
        return jsonify(success=False, error='暂无可用座位'), 503
    
    # 提交
    db.session.commit()

    # 构建提交数据
    window = Window.query.get(window_id)
    seats = Seat.query.filter(Seat.id.in_(seat_ids)).all()
    seat_numbers = [s.seat_number for s in seats]

    return jsonify(success=True, data={
        'order_id': order.id,
        'window_number': window.window_number,
        'seat_numbers': seat_numbers,
        'is_completed': order.is_completed
    })


# 查询订单详情
@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    # 验证登录
    student_id = session.get('student_id')
    if not student_id:
        return jsonify(success=False, error='未登录'), 401

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify(success=False, error='状态校验失败'), 401

    order = Order.query.get(order_id)
    if not order:
        return jsonify(success=False, error='订单不存在'), 404
    if order.student_id != student.id:
        return jsonify(success=False, error='禁止访问'), 403

    window = Window.query.get(order.window_id)

    # 查询座位
    order_seats = OrderSeat.query.filter_by(order_id=order_id).all()
    seat_ids = [os.seat_id for os in order_seats]
    seats = Seat.query.filter(Seat.id.in_(seat_ids)).all() if seat_ids else []
    seat_numbers = [s.seat_number for s in seats]

    # 查询菜品
    items = []
    for od in order.order_dishes:
        dish = Dish.query.get(od.dish_id)
        items.append({
            'dish_name': dish.name,
            'quantity': od.quantity,
            'price': float(od.price)
        })

    return jsonify(success=True, data={
        'order_id': order.id,
        'is_completed': order.is_completed,
        'party_size': order.party_size,
        'created_at': order.created_at.isoformat(),
        'window_number': window.window_number if window else None,
        'seat_numbers': seat_numbers,
        'items': items,
    })


# 查询今日菜单
@orders_bp.route('/menu/today', methods=['GET'])
def get_today_menu():
    today = datetime.date.today()

    menus = (
        DailyMenu.query
        .join(Dish, DailyMenu.dish_id == Dish.id)
        .join(Window, DailyMenu.window_id == Window.id)
        .filter(DailyMenu.date == today)
        .all()
    )

    data = []
    for m in menus:
        data.append({
            'daily_menu_id': m.id,
            'dish_id': m.dish_id,
            'name': m.dish.name,
            'price': float(m.dish.price),
            'image_url': m.dish.image_url,
            'window_id': m.window_id,
            'window_number': m.window.window_number,
            'window_name': m.window.name,
            'stock': m.stock,
            'is_sold_out': m.is_sold_out,
        })

    return jsonify(success=True, data=data)