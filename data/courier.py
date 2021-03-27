from sqlalchemy.orm import relation
from sqlalchemy_json import mutable_json_type
from .db_session import SqlAlchemyBase
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Integer, String, JSON, Float


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = Column(Integer, primary_key=True, nullable=False)
    courier_type = Column(String, nullable=False)
    regions = Column(JSON, nullable=False)
    working_hours = Column(JSON, nullable=False)
    rating = Column(Float)
    assign_time = Column(String)
    courier_type_when_formed = Column(String)
    earnings = Column(Integer, default=0)
    delivery_time_for_regions = Column(mutable_json_type(dbtype=JSON, nested=True), default={})
    last_action_time = Column(String, default=None)

    orders = relation('Order', back_populates='courier')
