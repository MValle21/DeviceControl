from typing import Optional
from flask import jsonify

from core.data.dao import Dao


class Response:
    def __init__(self, success: bool, data: Optional[dict], cause: Optional[Exception] = None):
        self.cause = cause
        self.data = data
        self.success = success

    def __str__(self):
        return str(self.__dict__)

    def to_json(self):
        return jsonify(
            {
                "success": self.success,
                "cause": str(self.cause),
                "data": self.data,
            }
        )


# DB tables
class Device(Dao.db.Model):
    __tablename__ = 'devices'
    id = Dao.db.Column(Dao.db.String(100), primary_key=True)
    device_class = Dao.db.Column(Dao.db.String(100))
    device_type = Dao.db.Column(Dao.db.String(100))
    address = Dao.db.Column(Dao.db.String(100), nullable=True, default=None)


class Value(Dao.db.Model):
    __tablename__ = 'values'
    id = Dao.db.Column(Dao.db.Integer, primary_key=True)
    time = Dao.db.Column(Dao.db.DateTime)
    value = Dao.db.Column(Dao.db.Float)
    dev_id = Dao.db.Column(Dao.db.String(100), Dao.db.ForeignKey('devices.id'))
    var_id = Dao.db.Column(Dao.db.String(100), Dao.db.ForeignKey('variables.code'))
    channel = Dao.db.Column(Dao.db.Integer, nullable=True, default=None)
    note = Dao.db.Column(Dao.db.String(100), nullable=True, default=None)


class Variable(Dao.db.Model):
    __tablename__ = 'variables'
    code = Dao.db.Column(Dao.db.String(30), primary_key=True)
    name = Dao.db.Column(Dao.db.String(100))
    type = Dao.db.Column(Dao.db.Enum(['measured','computed','adjusted','aggregate']), nullable=True, default=None)
    unit = Dao.db.Column(Dao.db.Integer, nullable=True, default=None)


class Event(Dao.db.Model):
    __tablename__ = 'events'
    id = Dao.db.Column(Dao.db.Integer, primary_key=True)
    dev_id = Dao.db.Column(Dao.db.String(100), Dao.db.ForeignKey('devices.id'))
    event_type = Dao.db.Column(Dao.db.Integer, Dao.db.ForeignKey('event_types.id'))
    time = Dao.db.Column(Dao.db.DateTime)
    args = Dao.db.Column(Dao.db.String(100))
    command = Dao.db.Column(Dao.db.String(100))
    response = Dao.db.Column(Dao.db.String(100))


class EventType(Dao.db.Model):
    __tablename__ = 'event_types'
    id = Dao.db.Column(Dao.db.Integer, primary_key=True)
    type = Dao.db.Column(Dao.db.String(100))


# TEMPORAL HACK !!!
class Experiment(Dao.db.Model):
    __tablename__ = 'experiments'
    id = Dao.db.Column(Dao.db.Integer, primary_key=True)
    dev_id = Dao.db.Column(Dao.db.String(100), Dao.db.ForeignKey('devices.id'))
    start = Dao.db.Column(Dao.db.DateTime)
    end = Dao.db.Column(Dao.db.DateTime, nullable=True, default=None)
    description = Dao.db.Column(Dao.db.String(100), nullable=True, default=None)
