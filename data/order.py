from sqlalchemy.orm import relation
from .db_session import SqlAlchemyBase
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, JSON, Float, String


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    weight = Column(Float)
    region = Column(Integer)
    delivery_hours = Column(JSON)
    complete_time = Column(String, default=None)

    courier_id = Column(Integer, ForeignKey('couriers.courier_id'))
    courier = relation('Courier')
