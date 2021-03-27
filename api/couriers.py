from flask import request
from flask_restful import abort, Resource

from api.logic import validate_time_interval, check_time, calculate_capacity, end_session_for_courier
from data.courier import Courier
from data.db_session import create_session
from data.order import Order


class CouriersResource(Resource):
    """/couriers/{courier_id}"""

    def patch(self, courier_id):
        session = create_session()
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).scalar()
        if courier is None:
            abort(404)

        args = request.json
        for key in args:
            if len(args[key]) != 0:
                if key == 'courier_type':
                    if args['courier_type'] in ('foot', 'bike', 'car'):
                        courier.courier_type = args['courier_type']
                    else:
                        abort(400)
                elif key == 'regions':
                    if any([True for i in args['regions'] if not isinstance(i, int)]):
                        abort(400)
                    courier.regions = args['regions']
                elif key == 'working_hours':
                    if (not isinstance(args['working_hours'], list)) or \
                            any([True for i in args['working_hours'] if validate_time_interval(i) is not None]):
                        abort(400)
                    courier.working_hours = args['working_hours']
                else:
                    abort(400)
            else:
                abort(400)

        capacity = calculate_capacity(courier.courier_type)
        orders = session.query(Order).filter(Order.courier_id == courier_id).filter(Order.complete_time == None) \
            .order_by(Order.weight.desc()).all()
        orders_weight = sum([order.weight for order in orders])

        for order in orders:
            if orders_weight <= capacity:
                break
            order.courier_id = None
            orders_weight -= order.weight

        for order in orders:
            if not check_time(courier.working_hours, order.delivery_hours) or order.region not in courier.regions:
                order.courier_id = None

        if len(orders) != 0 and len(session.query(Order).filter(Order.courier_id == courier_id).filter(
                Order.complete_time == None).all()) == 0:
            end_session_for_courier(courier)

        try:
            session.commit()
        except Exception as e:
            print(e)
            abort(400)

        return {'courier_id': courier.courier_id,
                'courier_type': courier.courier_type,
                'regions': courier.regions,
                'working_hours': courier.working_hours}, 200

    def get(self, courier_id):
        session = create_session()
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).scalar()
        if courier is None:
            abort(404)

        response = dict()
        response['courier_id'] = courier.courier_id
        response['courier_type'] = courier.courier_type
        response['regions'] = courier.regions
        response['working_hours'] = courier.working_hours

        average_time = [courier.delivery_time_for_regions[i][1] / courier.delivery_time_for_regions[i][0]
                        for i in courier.delivery_time_for_regions.keys()]
        if len(average_time) > 0:
            response['rating'] = round((60 * 60 - min(min(average_time), 60 * 60)) / (60 * 60) * 5, 2)

        response['earnings'] = courier.earnings
        return response, 200


class CouriersListResource(Resource):
    """/couriers"""

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

            if not isinstance(dataset['courier_id'], int) or dataset['courier_id'] < 1:
                errors.append('Courier ID must be positive integer.')

            if 'courier_type' not in dataset:
                errors.append('Courier type must be specified.')
            elif not isinstance(dataset['courier_type'], str):
                errors.append('Courier type must be a string.')
            elif dataset['courier_type'] not in ('foot', 'car', 'bike'):
                errors.append('Courier type must be one of following values: foot, car, bike.')

            if 'regions' not in dataset:
                errors.append('Courier regions must be specified.')
            elif not isinstance(dataset['regions'], list):
                errors.append('Regions must be an array.')
            elif len(dataset['regions']) == 0:
                errors.append('At least one region is required.')
            elif any([True for i in dataset['regions'] if not (isinstance(i, int) and i >= 0)]):
                errors.append('Regions must be positive integers.')
            elif len(set(dataset['regions'])) != len(dataset['regions']):
                errors.append('Regions must be unique')

            if 'working_hours' not in dataset:
                errors.append('Courier working hours must be specified')
            elif not isinstance(dataset['working_hours'], list):
                errors.append('Working hours must be a string.')
            elif len(dataset['working_hours']) == 0:
                errors.append('At least one working time slot is required.')
            else:
                for time_interval in dataset['working_hours']:
                    result = validate_time_interval(time_interval)
                    if result is not None:
                        errors.append(result)

            if len(errors) > 0:
                unsuccessful.append({'id': dataset['courier_id'], 'errors': errors})
                continue

            courier = Courier(
                courier_id=dataset['courier_id'],
                courier_type=dataset['courier_type'],
                regions=dataset['regions'],
                working_hours=dataset['working_hours']
            )
            session.add(courier)
            successful.append({'id': dataset['courier_id']})

        if len(unsuccessful) > 0:
            return {'validation_error': {'couriers': unsuccessful}}, 400
        else:
            session.commit()
            return {'couriers': successful}, 201
