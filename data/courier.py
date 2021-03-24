from sqlalchemy.orm import relation
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Integer, String, JSON, Float, DateTime


class Courier(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, primary_key=True, nullable=False)
    courier_type = Column(String, nullable=False)
    regions = Column(JSON, nullable=False)
    working_hours = Column(JSON, nullable=False)
    rating = Column(Float)
    earnings = Column(Integer)
    assign_time = Column(DateTime)
    transfers = Column(Integer, default=0)
    courier_type_when_formed = Column(String)

    orders = relation('Order', back_populates='courier')
