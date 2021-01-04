from typing import Optional
from flask import jsonify

from core.connection.server.FlaskServer import Server


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


class Value:
    __tablename__ = 'values'
    id = Server.db.Column(Server.db.Integer, primary_key=True)
    time = Server.db.Column(Server.db.DateTime)
    value = Server.db.Column(Server.db.Float)
    dev_id = Server.db.Column(Server.db.String(100), Server.db.ForeignKey('devices.id'))
    var_id = Server.db.Column(Server.db.String(100), Server.db.ForeignKey('variables.code'))
    channel = Server.db.Column(Server.db.Integer, nullable=True, default=None)
    note = Server.db.Column(Server.db.String(100), nullable=True, default=None)


class Variable:
    __tablename__ = 'variables'
    code = Server.db.Column(Server.db.String(30), primary_key=True)
    name = Server.db.Column(Server.db.String(100))
    type = Server.db.Column(Server.db.Enum(['measured','computed','adjusted','aggregate']), nullable=True, default=None)
    unit = Server.db.Column(Server.db.Integer, nullable=True, default=None)


class Event:
    __tablename__ = 'events'
    id = Server.db.Column(Server.db.Integer, primary_key=True)
    dev_id = Server.db.Column(Server.db.String(100), Server.db.ForeignKey('devices.id'))
    event_type = Server.db.Column(Server.db.Integer, Server.db.ForeignKey('event_types.id'))
    time = Server.db.Column(Server.db.DateTime)
    args = Server.db.Column(Server.db.String(100))
    command = Server.db.Column(Server.db.String(100))
    response = Server.db.Column(Server.db.String(100))


class EventType:
    __tablename__ = 'event_types'
    id = Server.db.Column(Server.db.Integer, primary_key=True)
    type = Server.db.Column(Server.db.String(100))


# TEMPORAL HACK !!!
class Experiment:
    __tablename__ = 'experiments'
    id = Server.db.Column(Server.db.Integer, primary_key=True)
    dev_id = Server.db.Column(Server.db.String(100), Server.db.ForeignKey('devices.id'))
    start = Server.db.Column(Server.db.DateTime)
    end = Server.db.Column(Server.db.DateTime, nullable=True, default=None)
    description = Server.db.Column(Server.db.String(100), nullable=True, default=None)
