from flask import Flask
from .config import Config
from .core.extensions import db, jwt, socketio
from .api import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register routes
    register_blueprints(app)

    return app
