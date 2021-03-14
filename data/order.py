from sqlalchemy.orm import relation
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, JSON, Float


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    weight = Column(Float)
    region = Column(Integer)
    delivery_hours = Column(JSON)

    courier_id = Column(Integer, ForeignKey('couriers.courier_id'))
    courier = relation('Courier')