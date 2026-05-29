from 软件综合实训.final_canteen.backend.models import Window, Order, SeatGroup, Seat, OrderSeat


def assign_window(db_session):
    """
    窗口分配算法：
    选择当前排队人数最少的窗口。如果有多个人数最少的窗口并列，则选择序号小的。
    如果没有在线窗口，返回 None。
    """
    # 查询所有在线窗口
    online_windows = db_session.query(Window).filter(Window.is_online == True).all()
    if not online_windows:
        return None
    
    # 统计每个窗口的排队数
    def pending_count(window):
        return db_session.query(Order).filter(
            Order.window_id == window.id,
            Order.is_completed == False
        ).count()
    
    # 按排队数为第一关键字，序号为第二关键字，找出对应窗口
    res = min(online_windows, key=lambda w: (pending_count(w), w.window_number))
    return res.id


def assign_seats(db_session, order_id, party_size):
    """
    座位分配算法：
    从前往后遍历所有座位组，找到第一个空座位组。
    如果没有空座位组，从前往后遍历所有座位组，找到第一个剩余座位数量足够的组。
    如果没有剩余作为数量足够的组，返回暂无可用座位。
    此函数会修改座位占用状态！
    """
    groups = db_session.query(SeatGroup).order_by(SeatGroup.id.asc()).all()

    # 查询每组空位数量
    group_free = []
    for g in groups:
        free_seats = db_session.query(Seat).filter(
            Seat.group_id == g.id,
            Seat.is_occupied == False
        ).order_by(Seat.id.asc()).all()
        group_free.append((g, free_seats))

    # 遍历寻找空座位组
    for g, free_seats in group_free:
        if len(free_seats) == g.capacity and len(free_seats) >= party_size:
            chosen = free_seats[:party_size]
            for seat in chosen:
                seat.is_occupied = True
                db_session.add(OrderSeat(order_id=order_id, seat_id=seat.id))
            return [seat.id for seat in chosen]

    # 遍历寻找座位数量足够的组
    for g, free_seats in group_free:
        if len(free_seats) >= party_size:
            chosen = free_seats[:party_size]
            for seat in chosen:
                seat.is_occupied = True
                db_session.add(OrderSeat(order_id=order_id, seat_id=seat.id))
            return [seat.id for seat in chosen]

    # 无可用座位组
    return []