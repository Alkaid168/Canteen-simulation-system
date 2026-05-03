from flask import Blueprint, jsonify

from models import db, Seat, SeatGroup

seats_bp = Blueprint('seats_bp', __name__)


@seats_bp.route('/seats', methods=['GET'])
def get_seats():
    groups = SeatGroup.query.order_by(SeatGroup.id.asc()).all()
    data = []
    for g in groups:
        seats = Seat.query.filter_by(group_id=g.id).order_by(Seat.id.asc()).all()
        data.append({
            'group_id': g.id,
            'group_name': g.name,
            'seats': [
                {
                    'seat_id': s.id,
                    'seat_number': s.seat_number,
                    'is_occupied': s.is_occupied,
                }
                for s in seats
            ],
        })
    return jsonify(success=True, data=data)


@seats_bp.route('/seats/<int:seat_id>/release', methods=['PUT'])
def release_seat(seat_id):
    seat = Seat.query.get(seat_id)
    if not seat:
        return jsonify(success=False, error='座位不存在'), 404

    if not seat.is_occupied:
        return jsonify(success=False, error='座位已是空闲状态'), 400

    seat.is_occupied = False
    db.session.commit()
    return jsonify(success=True, data={'seat_id': seat.id, 'is_occupied': seat.is_occupied})
