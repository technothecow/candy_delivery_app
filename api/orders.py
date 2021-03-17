from datetime import datetime

from flask import request, jsonify, make_response
from flask_restful import abort, Resource

from data.courier import Courier
from data.order import Order
from data.db_session import create_session


def time_to_minutes(time):
    time = time.split(':')
    return int(time[0]) * 60 + int(time[1])


def check_intervals(time1, time2):
    time1 = time1.split('-')
    time1 = time_to_minutes(time1[0]), time_to_minutes(time1[1])
    time2 = time2.split('-')
    time2 = time_to_minutes(time2[0]), time_to_minutes(time2[1])
    if time1[0] < time2[0] < time2[1] < time1[1]:
        return True
    return False


def check_time(time1, time2):
    for i in time1:
        for j in time2:
            if check_intervals(i, j) or check_intervals(j, i):
                return True
    return False


class OrdersAssignment(Resource):
    def post(self):
        courier_id = request.json['courier_id']
        session = create_session()
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).scalar()
        if courier is None:
            abort(400)

        orders = list()

        if courier.assign_time is not None:
            for order in courier.orders:
                if order.completed == 0:
                    orders.append({'id': order.order_id})
            if len(orders) == 0:
                courier.assign_time = None
                courier.transfers += 1
            else:
                print(jsonify({'orders': orders, 'assign_time': str(courier.assign_time)}))
                return {'orders': orders, 'assign_time': str(courier.assign_time)}, 200

        for order in session.query(Order).filter(
                (Order.courier_id == None) | (Order.courier_id == courier.courier_id)).filter(Order.completed == 0):
            if check_time(courier.working_hours, order.delivery_hours):
                orders.append({'id': order.order_id})
                order.courier_id = courier.courier_id

        if len(orders) == 0:
            return jsonify({'orders': orders}), 200

        courier.assign_time = datetime.now()
        session.commit()
        return jsonify({'orders': orders, 'assign_time': courier.assign_time}), 200


class OrdersListResource(Resource):
    def post(self):
        args = request.json['data']
        session = create_session()
        successful = list()
        unsuccessful = list()
        for dataset in args:
            if 'weight' not in dataset or not (0.01 <= dataset['weight'] <= 50) \
                    or 'region' not in dataset \
                    or 'delivery_hours' not in dataset or len(dataset['delivery_hours']) == 0:
                unsuccessful.append({'id': dataset['order_id']})
                continue
            order = Order(
                order_id=dataset['order_id'],
                weight=dataset['weight'],
                region=dataset['region'],
                delivery_hours=dataset['delivery_hours']
            )
            session.add(order)
            successful.append({'id': dataset['order_id']})
        if len(unsuccessful) > 0:
            return make_response(jsonify({'validation_error': {'orders': unsuccessful}}), 400)
        else:
            session.commit()
            return make_response(jsonify({'orders': successful}), 201)