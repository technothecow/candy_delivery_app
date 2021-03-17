from flask import Flask
from flask_restful import Api

from api.orders import OrdersAssignment, OrdersListResource
from api.couriers import CouriersListResource, CouriersResource
from data.db_session import global_init

app = Flask(__name__)
api = Api(app)

if __name__ == '__main__':
    global_init('db/database.db')
    api.add_resource(CouriersListResource, '/couriers')
    api.add_resource(CouriersResource, '/couriers/<int:courier_id>')
    api.add_resource(OrdersListResource, '/orders')
    api.add_resource(OrdersAssignment, '/orders/assign')
    app.run(debug=True)
