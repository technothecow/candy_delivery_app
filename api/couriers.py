from flask import request, jsonify, make_response
from flask_restful import abort, Resource

from data.courier import Courier
from data.db_session import create_session


class CouriersResource(Resource):
    pass


class CouriersListResource(Resource):
    def post(self):
        args = request.json['data']
        session = create_session()
        successful = list()
        unsuccessful = list()
        for dataset in args:
            if 'courier_type' not in dataset or len(dataset['courier_type']) == 0 \
                    or 'regions' not in dataset or len(dataset['regions']) == 0 \
                    or 'working_hours' not in dataset or len(dataset['working_hours']) == 0:
                unsuccessful.append({'id': dataset['courier_id']})
                continue

            try:
                courier = Courier(
                    courier_id=dataset['courier_id'],
                    courier_type=dataset['courier_type'],
                    regions=dataset['regions'],
                    working_hours=dataset['working_hours']
                )
                session.add(courier)
                session.commit()
            except Exception:
                unsuccessful.append({'id': dataset['courier_id']})
            successful.append({'id': dataset['courier_id']})
        if len(unsuccessful) > 0:
            return make_response(jsonify({'validation_error': {'couriers': unsuccessful}}), 400)
        else:
            return make_response(jsonify({'couriers': successful}), 201)
