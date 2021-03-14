from flask import Flask
from flask_restful import Api

from data.db_session import global_init
from api.couriers import CouriersListResource, CouriersResource

app = Flask(__name__)
api = Api(app)

if __name__ == '__main__':
    global_init('db/database.db')
    api.add_resource(CouriersListResource, '/couriers')
    app.run(debug=True)
