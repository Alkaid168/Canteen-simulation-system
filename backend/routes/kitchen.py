import datetime

from flask import Blueprint, jsonify, request

from models import db, Window, Order, OrderSeat, Dish, Seat, DishPrediction

kitchen_bp = Blueprint('kitchen_bp', __name__)


@kitchen_bp.route('/windows', methods=['GET'])
def get_windows():
    windows = Window.query.order_by(Window.window_number.asc()).all()
    return jsonify(success=True, data=[{
        'id': w.id,
        'name': w.name,
        'window_number': w.window_number,
        'is_online': w.is_online,
    } for w in windows])


@kitchen_bp.route('/kitchen/orders', methods=['GET'])
def get_kitchen_orders():
    window_id = request.args.get('window_id', type=int)
    query = Order.query.filter(Order.is_completed == False)
    if window_id is not None:
        query = query.filter_by(window_id=window_id)

    orders = query.order_by(Order.created_at.asc()).all()

    data = []
    for order in orders:
        seat_numbers = []
        for os in order.order_seats:
            seat = Seat.query.get(os.seat_id)
            if seat:
                seat_numbers.append(seat.seat_number)

        items = []
        for od in order.order_dishes:
            dish = Dish.query.get(od.dish_id)
            items.append({
                'dish_name': dish.name if dish else '',
                'quantity': od.quantity,
            })

        data.append({
            'order_id': order.id,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'party_size': order.party_size,
            'window_id': order.window_id,
            'seat_numbers': seat_numbers,
            'items': items,
        })

    return jsonify(success=True, data=data)


@kitchen_bp.route('/kitchen/orders/<int:order_id>/complete', methods=['PUT'])
def complete_order(order_id):
    order = Order.query.get(order_id)
    if order is None:
        return jsonify(success=False, error='订单不存在'), 404

    if not order.is_completed:
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


@kitchen_bp.route('/kitchen/prediction', methods=['GET'])
def get_kitchen_prediction():
    today = datetime.date.today()
    preds = DishPrediction.query.filter_by(date=today).all()

    data = []
    for p in preds:
        dish = Dish.query.get(p.dish_id)
        effective = p.adjusted_quantity if p.adjusted_quantity is not None else p.predicted_quantity
        data.append({
            'dish_id': p.dish_id,
            'dish_name': dish.name if dish else None,
            'predicted_quantity': p.predicted_quantity,
            'adjusted_quantity': p.adjusted_quantity,
            'effective_quantity': effective,
        })

    return jsonify(success=True, data=data)
