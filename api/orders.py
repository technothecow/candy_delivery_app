from datetime import datetime

from flask import request
from flask_restful import abort, Resource

from api.logic import check_time, format_date
from data.courier import Courier
from data.order import Order
from data.db_session import create_session


class OrdersAssignment(Resource):
    """/orders/assign"""

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
                courier.courier_type_when_formed = None
                session.commit()
            else:
                return {'orders': orders, 'assign_time': courier.assign_time}, 200

        capacity_table = {'foot': 10, 'bike': 15, 'car': 50}
        capacity = capacity_table[courier.courier_type]

        for order in session.query(Order).filter((Order.courier_id == None) | (Order.courier_id == courier.courier_id))\
                .filter(Order.completed == 0):
            if check_time(courier.working_hours, order.delivery_hours) and order.region in courier.regions and \
                    order.weight <= capacity:
                orders.append({'id': order.order_id})
                order.courier_id = courier.courier_id

        if len(orders) == 0:
            return {'orders': orders}, 200

        courier.assign_time = format_date(datetime.now())
        courier.courier_type_when_formed = courier.courier_type
        session.commit()
        return {'orders': orders, 'assign_time': courier.assign_time}, 200


class OrdersListResource(Resource):
    """/orders"""

    def post(self):
        args = request.json['data']
        session = create_session()
        successful = list()
        unsuccessful = list()
        for dataset in args:

            errors = list()

            if 'weight' not in dataset:
                errors.append('Weight must be specified.')
            elif not isinstance(dataset['weight'], float):
                errors.append('Weight must be float.')
            elif dataset['weight'] < 0.01:
                errors.append('The weight must be greater than or equal to 0.01.')
            elif dataset['weight'] > 50:
                errors.append('The weight must be less than or equal to 50.')

            if 'region' not in dataset:
                errors.append('Region must be specified.')
            elif not isinstance(dataset['region'], int):
                errors.append('Region must be an integer.')

            if 'delivery_hours' not in dataset:
                errors.append('Delivery hours must be specified.')
            elif not isinstance(dataset['delivery_hours'], list):
                errors.append('Delivery hours must be an array.')
            elif len(dataset['delivery_hours']) == 0:
                errors.append('At least one delivery time slot is required.')

            if len(errors) > 0:
                unsuccessful.append({'id': dataset['order_id'], 'errors': errors})
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
            return {'validation_error': {'orders': unsuccessful}}, 400
        else:
            session.commit()
            return {'orders': successful}, 201
