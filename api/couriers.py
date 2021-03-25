from flask import request
from flask_restful import abort, Resource

from api.logic import validate_time_interval
from data.courier import Courier
from data.db_session import create_session


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
                elif key == 'regions':
                    courier.regions = args['regions']
                elif key == 'working_hours':
                    courier.working_hours = args['working_hours']
            else:
                abort(400)

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
        assert isinstance(courier, Courier)
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
        args = request.json['data']
        session = create_session()
        successful = list()
        unsuccessful = list()
        for dataset in args:

            errors = list()

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
            else:
                if any([True for i in dataset['regions'] if not (isinstance(i, int) and i >= 0)]):
                    errors.append('Regions must be positive integers.')

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
