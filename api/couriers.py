from flask import request, jsonify, make_response
from flask_restful import abort, Resource

from data.courier import Courier
from data.db_session import create_session


class CouriersResource(Resource):
    def patch(self, courier_id):
        session = create_session()
        courier = session.query(Courier).filter(Courier.courier_id == courier_id).scalar()
        if courier is None:
            abort(404)

        args = request.json
        for key in args:
            if len(args[key]) != 0:
                if key == 'courier_type':
                    courier.courier_type = args['courier_type']
                elif key == 'regions':
                    courier.courier_type = args['regions']
                elif key == 'working_hours':
                    courier.courier_type = args['working_hours']
            else:
                abort(400)

        try:
            session.commit()
        except Exception:
            abort(400)

        make_response(jsonify({'courier_id': courier.courier_id,
                               'courier_type': courier.courier_type,
                               'regions': courier.regions,
                               'working_hours': courier.working_hours}), 200)


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
