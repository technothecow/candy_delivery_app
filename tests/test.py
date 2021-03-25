import requests

ADDRESS = 'http://127.0.0.1:5000/'


class TestCouriersPost:
    def test_correct_input(self):
        request = requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                },
                {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                },
                {
                    "courier_id": 3,
                    "courier_type": "car",
                    "regions": [12, 22, 23, 33],
                    "working_hours": ["15:00-16:00"]
                }
            ]
        })
        assert (request.status_code, request.json()) == (201, {"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]})

    def test_wrong_courier_type_name(self):
        request = requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": "foott",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        })
        assert (request.status_code, request.json()) == (400, {'validation_error': {
            'couriers': [
                {
                    'id': 4,
                    'errors':
                        ['Courier type must be one of following '
                         'values: foot, car, bike.']
                }
            ]
        }})

    def test_wrong_courier_type_datatype(self):
        request = requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": 1,
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {'couriers': [{'id': 4, 'errors': ['Courier type must be a string.']}]}})

    def test_empty_regions_field(self):
        request = requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": 'car',
                    "regions": [],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {'couriers': [{'id': 4, 'errors': ['At least one region is required.']}]}})

    def test_multiple_errors(self):
        request = requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": 13,
                    "regions": 'bike',
                    "working_hours": []
                }
            ]
        })
        assert (request.status_code, request.json()) == (400,
                                                         {'validation_error': {
                                                             'couriers': [
                                                                 {
                                                                     'id': 4,
                                                                     'errors':
                                                                         ['Courier type must be a string.',
                                                                          'Regions must be an array.',
                                                                          'At least one working time slot is required.'
                                                                          ]
                                                                 }
                                                             ]
                                                         }})

    def test_wrong_time_format(self):
        request = requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": 'car',
                    "regions": [1, 2],
                    "working_hours": ['15:00-aa:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (400, {'validation_error': {
            'couriers': [{'id': 4, 'errors': ['Wrong time interval format. Correct usage: "HH:MM-HH:MM"']}]}})

    def test_repetitive_regions(self):
        request = requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": 'car',
                    "regions": [1, 1],
                    "working_hours": ['15:00-18:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {'couriers': [{'id': 4, 'errors': ['Regions must be unique']}]}})

    def test_negative_or_non_integer_regions(self):
        request = requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 4,
                    "courier_type": 'car',
                    "regions": ['no', -1],
                    "working_hours": ['15:00-18:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {'couriers': [{'id': 4, 'errors': ['Regions must be positive integers.']}]}})


class TestCouriersPatch:
    def test_correct_input(self):
        requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 5,
                    "courier_type": "foot",
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        })
        request = requests.patch(ADDRESS + 'couriers/5', json={
            'regions': [11, 33, 2],
            'courier_type': 'car'
        })
        assert (request.status_code, request.json()) == (200, {'courier_id': 5, 'courier_type': 'car',
                                                               'regions': [11, 33, 2],
                                                               'working_hours': ['11:35-14:05', '09:00-11:00']})

    def test_incorrect_courier_type(self):
        request = requests.patch(ADDRESS + 'couriers/5', json={
            'courier_type': 'carr'
        })
        assert request.status_code == 400

    def test_incorrect_regions_format(self):
        request = requests.patch(ADDRESS + 'couriers/5', json={
            'regions': ['one', 'three']
        })
        assert request.status_code == 400

    def test_nonexistent_field(self):
        request = requests.patch(ADDRESS + 'couriers/5', json={
            'orders': [1, 3]
        })
        assert request.status_code == 400

    def test_nonexistent_courier(self):
        request = requests.patch(ADDRESS + 'couriers/999', json={
            'regions': [1, 3]
        })
        assert request.status_code == 404

    def test_empty_field(self):
        request = requests.patch(ADDRESS + 'couriers/5', json={
            'working_hours': []
        })
        assert request.status_code == 400

    def test_reassigning_orders(self):
        requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 0,
                    "weight": 40,
                    "region": 2,
                    "delivery_hours": ["01:00-23:00"]
                },
                {
                    "order_id": 1,
                    "weight": 4,
                    "region": 2,
                    "delivery_hours": ["01:00-23:00"]
                }
            ]})
        requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 5
        })
        requests.patch(ADDRESS + 'couriers/5', json={
            'courier_type': 'bike'
        })
        request = requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 5
        })
        assert request.json()['orders'] == [{'id': 1}]
