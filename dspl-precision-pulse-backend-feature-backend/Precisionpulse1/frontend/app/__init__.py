from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Allow all origins (dev mode) OR specify frontend
    CORS(app, origins=["http://localhost:3000"])

    # Register Blueprints

    return app
