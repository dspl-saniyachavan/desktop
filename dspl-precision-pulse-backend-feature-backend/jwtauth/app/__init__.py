from flask import Flask
from .extensions import db, migrate, jwt
from .routes import api
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(api, url_prefix="/api")

    return app
