import datetime

import requests


def format_date(date: datetime.datetime):
    return date.isoformat('T')[:-4] + 'Z'


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
                    "order_id": 50,
                    "weight": 40,
                    "region": 2,
                    "delivery_hours": ["01:00-23:00"]
                },
                {
                    "order_id": 51,
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
        assert request.json()['orders'] == [{'id': 51}]


class TestOrdersPost:
    def test_correct_input(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 11,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 12,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 13,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        })
        assert (request.status_code, request.json()) == (201, {"orders": [{"id": 11}, {"id": 12}, {"id": 13}]})

    def test_empty_field(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 11,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": []
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400,
            {'validation_error': {'orders': [{'id': 11, 'errors': ['At least one delivery time slot is required.']}]}})

    def test_absent_field(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 11,
                    "weight": 0.23,
                    "region": 12
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {'orders': [{'id': 11, 'errors': ['Delivery hours must be specified.']}]}})

    def test_wrong_datatype(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 11,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": '13:00-16:00'
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {'orders': [{'id': 11, 'errors': ['Delivery hours must be an array.']}]}})

    def test_limit_exceeding_weight_value(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 11,
                    "weight": 55,
                    "region": 12,
                    "delivery_hours": ['13:00-16:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400,
            {'validation_error': {'orders': [{'id': 11, 'errors': ['The weight must be less than or equal to 50.']}]}})

    def test_below_limit_weight_value(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 11,
                    "weight": 0.001,
                    "region": 12,
                    "delivery_hours": ['13:00-16:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {
                'orders': [{'id': 11, 'errors': ['The weight must be greater than or equal to 0.01.']}]}})

    def test_minimal_weight_value(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 111,
                    "weight": 0.01,
                    "region": 12,
                    "delivery_hours": ['13:00-16:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (201, {'orders': [{'id': 111}]})

    def test_maximum_weight_value(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 112,
                    "weight": 50,
                    "region": 12,
                    "delivery_hours": ['13:00-16:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (201, {'orders': [{'id': 112}]})

    def test_wrong_time_interval(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 111,
                    "weight": 0.01,
                    "region": 12,
                    "delivery_hours": ['13:00-25:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (400, {'validation_error': {
            'orders': [{'id': 111, 'errors': ['There are only 24 hours in a day and 60 minutes in an hour.']}]}})

    def test_wrong_time_interval_formatting(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 111,
                    "weight": 0.01,
                    "region": 12,
                    "delivery_hours": ['13:00-23:00', '7:00-12:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (400, {'validation_error': {
            'orders': [{'id': 111, 'errors': ['Wrong time interval format. Correct usage: "HH:MM-HH:MM"']}]}})

    def test_wrong_id_datatype(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 'one',
                    "weight": 1,
                    "region": 12,
                    "delivery_hours": ['13:00-23:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {'orders': [{'id': 'one', 'errors': ['Order ID must be positive integer.']}]}})

    def test_negative_id(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": -1,
                    "weight": 1,
                    "region": 12,
                    "delivery_hours": ['13:00-23:00']
                }
            ]
        })
        assert (request.status_code, request.json()) == (
            400, {'validation_error': {'orders': [{'id': -1, 'errors': ['Order ID must be positive integer.']}]}})

    def test_multiple_errors(self):
        request = requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 0,
                    "region": 'two',
                    "delivery_hours": ['all day']
                }
            ]
        })
        assert (request.status_code, request.json()) == (400, {'validation_error': {'orders': [{'id': 0, 'errors': [
            'Order ID must be positive integer.', 'Weight must be specified.', 'Region must be positive integer.',
            'Wrong time interval format. Correct usage: "HH:MM-HH:MM"']}]}})


class TestOrdersAssignPost:
    def test_correct_input(self):
        request = requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 3
        })
        assert (request.status_code, request.json()['orders']) == (200, [{'id': 111}, {'id': 11}])

    def test_nonexistent_id(self):
        request = requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 1001
        })
        assert request.status_code == 400

    def test_empty_order_list(self):
        requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 500,
                    "courier_type": "car",
                    "regions": [99],
                    "working_hours": ["09:00-18:00"]
                }
            ]
        })
        request = requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 500
        })
        assert (request.status_code, request.json()) == (200, {'orders': []})

    def test_completed_order(self):
        requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 201,
                    "weight": 0.23,
                    "region": 99,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 202,
                    "weight": 15,
                    "region": 99,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 203,
                    "weight": 0.01,
                    "region": 99,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        })
        time = requests.post(ADDRESS + 'orders/assign', json={'courier_id': 500}).json()['assign_time']
        requests.post(ADDRESS + 'orders/complete',
                      json={'courier_id': 500, 'order_id': 201, 'complete_time': '2021-01-10T10:33:01.42Z'})
        request = requests.post(ADDRESS + 'orders/assign', json={'courier_id': 500})
        assert request.json() == {'orders': [{'id': 202}, {'id': 203}], 'assign_time': time}

    def test_odd_time_intervals(self):
        requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 600,
                    "courier_type": "car",
                    "regions": [228],
                    "working_hours": ["12:00-18:00"]
                }
            ]
        })
        requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 301,
                    "weight": 0.23,
                    "region": 228,
                    "delivery_hours": ["09:00-12:00"]
                },
                {
                    "order_id": 302,
                    "weight": 15,
                    "region": 228,
                    "delivery_hours": ["10:00-14:00"]
                },
                {
                    "order_id": 303,
                    "weight": 0.01,
                    "region": 228,
                    "delivery_hours": ["17:00-19:00"]
                },
                {
                    "order_id": 304,
                    "weight": 1,
                    "region": 228,
                    "delivery_hours": ["15:00-17:00"]
                }
            ]
        })
        request = requests.post(ADDRESS + 'orders/assign', json={'courier_id': 600})
        assert request.json()['orders'] == [{'id': 303}, {'id': 304}, {'id': 302}]


class TestOrdersCompletePost:
    def test_correct_input(self):
        requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 5000,
                    "courier_type": "car",
                    "regions": [555],
                    "working_hours": ["09:00-18:00"]
                }
            ]
        })
        requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 5551,
                    "weight": 0.23,
                    "region": 555,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 5552,
                    "weight": 15,
                    "region": 555,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 5553,
                    "weight": 0.01,
                    "region": 555,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        })
        requests.post(ADDRESS + 'orders/assign', json={
            "courier_id": 5000
        })
        request = requests.post(ADDRESS + 'orders/complete', json={
            "courier_id": 5000,
            "order_id": 5551,
            "complete_time": "2021-01-10T10:33:01.42Z"
        })
        assert (request.status_code, request.json()) == (200, {'order_id': 5551})

    def test_nonexistent_courier_id(self):
        request = requests.post(ADDRESS + 'orders/complete', json={
            "courier_id": 94535,
            "order_id": 5551,
            "complete_time": "2021-01-10T10:33:01.42Z"
        })
        assert request.status_code == 400

    def test_nonexistent_order_id(self):
        request = requests.post(ADDRESS + 'orders/complete', json={
            "courier_id": 5000,
            "order_id": 35345,
            "complete_time": "2021-01-10T10:33:01.42Z"
        })
        assert request.status_code == 400

    def test_non_assigned_order(self):
        request = requests.post(ADDRESS + 'orders/complete', json={
            "courier_id": 5000,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        })
        assert request.status_code == 400

    def test_idempotency(self):
        request = requests.post(ADDRESS + 'orders/complete', json={
            "courier_id": 5000,
            "order_id": 5551,
            "complete_time": "2021-01-10T10:33:01.42Z"
        })
        assert (request.status_code, request.json()) == (200, {'order_id': 5551})


class TestCouriersGet:
    def test_correct_input_without_rating(self):
        requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 9,
                    "courier_type": "foot",
                    "regions": [1],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        })
        request = requests.get(ADDRESS + 'couriers/9')
        assert (request.status_code, request.json()) == (200, {'courier_id': 9, 'courier_type': 'foot',
                                                               'regions': [1],
                                                               'working_hours': ['11:35-14:05', '09:00-11:00'],
                                                               'earnings': 0})

    def test_correct_input_with_rating(self):
        requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 951,
                    "weight": 1,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                }
            ]
        })
        a = requests.post(ADDRESS + 'orders/assign', json={'courier_id': 9})
        dt = datetime.datetime.now() + datetime.timedelta(minutes=12)
        requests.post(ADDRESS + 'orders/complete', json={'courier_id': 9, 'order_id': 951,
                                                         'complete_time': format_date(dt)})
        request = requests.get(ADDRESS + 'couriers/9')
        assert (request.status_code, request.json()) == (200, {'courier_id': 9, 'courier_type': 'foot', 'regions': [1],
                                                               'working_hours': ['11:35-14:05', '09:00-11:00'],
                                                               'rating': 4.0, 'earnings': 1000})

    def test_correct_input_with_change_of_rating(self):
        requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 955,
                    "weight": 1,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                }
            ]
        })
        requests.post(ADDRESS + 'orders/assign', json={'courier_id': 9})
        dt = datetime.datetime.now() + datetime.timedelta(minutes=20)
        requests.post(ADDRESS + 'orders/complete', json={'courier_id': 9, 'order_id': 955,
                                                         'complete_time': format_date(dt)})
        request = requests.get(ADDRESS + 'couriers/9')
        assert (request.status_code, request.json()) == (200, {'courier_id': 9, 'courier_type': 'foot', 'regions': [1],
                                                               'working_hours': ['11:35-14:05', '09:00-11:00'],
                                                               'rating': 3.67, 'earnings': 2000})

    def test_nonexistent_courier_id(self):
        request = requests.get(ADDRESS + 'couriers/324234')
        assert request.status_code == 404

    def test_complicated_case_with_different_regions(self):
        requests.post(ADDRESS + 'couriers', json={
            "data": [
                {
                    "courier_id": 1337,
                    "courier_type": "car",
                    "regions": [73, 733],
                    "working_hours": ["00:00-24:00"]
                }
            ]
        })
        requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 21,
                    "weight": 1,
                    "region": 73,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 22,
                    "weight": 30,
                    "region": 73,
                    "delivery_hours": ["09:00-18:00"]
                }
            ]
        })
        requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 1337
        })
        dt = datetime.datetime.now()
        dt += datetime.timedelta(minutes=24)
        requests.post(ADDRESS + 'orders/complete', json={
            "courier_id": 1337,
            "order_id": 21,
            "complete_time": format_date(dt)
        })
        requests.patch(ADDRESS + 'couriers/1337', json={
            'courier_type': 'foot'
        })
        requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 1337
        })
        requests.post(ADDRESS + 'orders', json={
            "data": [
                {
                    "order_id": 23,
                    "weight": 1,
                    "region": 733,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 24,
                    "weight": 2,
                    "region": 733,
                    "delivery_hours": ["09:00-18:00"]
                }
            ]
        })
        requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 1337
        })
        dt = datetime.datetime.now()
        dt += datetime.timedelta(minutes=10)
        requests.post(ADDRESS + 'orders/complete', json={
            "courier_id": 1337,
            "order_id": 23,
            "complete_time": format_date(dt)
        })
        requests.post(ADDRESS + 'orders/assign', json={
            'courier_id': 1337
        })
        dt += datetime.timedelta(minutes=12)
        requests.post(ADDRESS + 'orders/complete', json={
            "courier_id": 1337,
            "order_id": 24,
            "complete_time": format_date(dt)
        })
        request = requests.get(ADDRESS + 'couriers/1337').json()
        assert (request['earnings'], request['rating']) == (5500, 4.08)
