from datetime import datetime

from flask import request
from flask_restful import abort, Resource

from api.logic import check_time, format_date, calculate_time, validate_time_interval, calculate_capacity, \
    end_session_for_courier
from data.courier import Courier
from data.order import Order
from data.db_session import create_session


class OrdersAssignment(Resource):
    """/orders/assign"""

    def post(self):
        try:
            courier_id = request.json['courier_id']
        except KeyError:
            abort(400)
        session = create_session()
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).scalar()
        if courier is None:
            abort(400)

        orders = list()

        if courier.assign_time is not None:
            for order in courier.orders:
                if order.complete_time is None:
                    orders.append({'id': order.order_id})
            if len(orders) == 0:
                end_session_for_courier(courier)
                session.commit()
            else:
                return {'orders': orders, 'assign_time': courier.assign_time}, 200

        capacity = calculate_capacity(courier.courier_type)

        for order in session.query(Order).filter((Order.courier_id == None) | (Order.courier_id == courier.courier_id)) \
                .order_by(Order.weight).filter(Order.complete_time == None).all():
            if capacity - order.weight < 0:
                break
            if check_time(courier.working_hours, order.delivery_hours) and order.region in courier.regions:
                orders.append({'id': order.order_id})
                order.courier_id = courier.courier_id
                capacity -= order.weight

        if len(orders) == 0:
            return {'orders': orders}, 200

        courier.assign_time = format_date(datetime.utcnow())
        courier.last_action_time = courier.assign_time
        courier.courier_type_when_formed = courier.courier_type
        session.commit()
        return {'orders': orders, 'assign_time': courier.assign_time}, 200


class OrdersListResource(Resource):
    """/orders"""

    def post(self):
        try:
            args = request.json['data']
        except KeyError:
            abort(400)
        session = create_session()
        successful = list()
        unsuccessful = list()
        for dataset in args:

            errors = list()

            if not isinstance(dataset['order_id'], int) or dataset['order_id'] < 1:
                errors.append('Order ID must be positive integer.')

            if 'weight' not in dataset:
                errors.append('Weight must be specified.')
            elif not (isinstance(dataset['weight'], float) or isinstance(dataset['weight'], int)):
                errors.append('Weight must be float.')
            elif dataset['weight'] < 0.01:
                errors.append('The weight must be greater than or equal to 0.01.')
            elif dataset['weight'] > 50:
                errors.append('The weight must be less than or equal to 50.')

            if 'region' not in dataset:
                errors.append('Region must be specified.')
            elif not isinstance(dataset['region'], int) or dataset['region'] < 0:
                errors.append('Region must be positive integer.')

            if 'delivery_hours' not in dataset:
                errors.append('Delivery hours must be specified.')
            elif not isinstance(dataset['delivery_hours'], list):
                errors.append('Delivery hours must be an array.')
            elif len(dataset['delivery_hours']) == 0:
                errors.append('At least one delivery time slot is required.')
            else:
                for time_interval in dataset['delivery_hours']:
                    result = validate_time_interval(time_interval)
                    if result is not None:
                        errors.append(result)

            if len(errors) > 0:
                unsuccessful.append({'id': dataset['order_id'], 'errors': errors})
                continue

            order = Order(
                order_id=dataset['order_id'],
                weight=float(dataset['weight']),
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


class OrdersCompletion(Resource):
    """/orders/complete"""

    def post(self):
        order_id, courier_id, complete_time = None, None, None
        try:
            order_id = request.json['order_id']
            courier_id = request.json['courier_id']
            complete_time = request.json['complete_time']
        except KeyError:
            abort(400)
        session = create_session()
        order = session.query(Order).filter(Order.order_id == order_id).scalar()
        if order is None or order.courier_id != courier_id:
            abort(400)

        courier = order.courier

        if str(order.region) not in courier.delivery_time_for_regions.keys():
            courier.delivery_time_for_regions[order.region] = list()
            courier.delivery_time_for_regions[order.region].append(1)
            courier.delivery_time_for_regions[order.region].append(
                calculate_time(courier.last_action_time, complete_time))
        else:
            courier.delivery_time_for_regions[str(order.region)][0] += 1
            courier.delivery_time_for_regions[str(order.region)][1] += calculate_time(courier.last_action_time,
                                                                                      complete_time)

        courier.last_action_time = complete_time
        order.complete_time = complete_time

        if len([True for order in courier.orders if order.complete_time is None]) == 0:
            end_session_for_courier(courier)

        session.commit()
        return {'order_id': order_id}, 200
