import core.connection.server.FlaskServer as FlaskServer
from core.connection.client.websocket_client import Client as WebsocketClient

classes = {
    "flask_server": (FlaskServer.Server, []),
    "websocket_client": (WebsocketClient, ["http://127.0.0.1:5000/"])
}