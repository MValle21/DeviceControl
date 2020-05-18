from core.connection.server.FlaskServer import Server as FlaskServer
from core.connection.client.websocket_client import Client as WebsocketClient
from core.connection.client.flask_client import Client as FlaskClient

classes = {
    "flask_server": (FlaskServer, []),
    "websocket_client": (WebsocketClient, ["http://127.0.0.1:5000/"]),
    "flask_client": (FlaskClient, ["http://127.0.0.1:5000"])
}