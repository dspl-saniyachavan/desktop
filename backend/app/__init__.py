from flask import Flask
from flask_cors import CORS
from config.config import Config
from app.models import db
from app.models.user import User
from app.models.parameter import Parameter
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.parameter_routes import parameter_bp
from app.routes.sync_routes import sync_bp
from app.routes.internal_routes import internal_bp
import asyncio
import threading

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    CORS(app)
    
    with app.app_context():
        db.create_all()
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(parameter_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(internal_bp)
    
    # Start MQTT sync service in background thread
    def start_mqtt_sync():
        from app.services.mqtt_sync_service import MQTTSyncService
        sync_service = MQTTSyncService(app)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(sync_service.start())
        loop.run_forever()
    
    mqtt_thread = threading.Thread(target=start_mqtt_sync, daemon=True)
    mqtt_thread.start()
    
    return app
