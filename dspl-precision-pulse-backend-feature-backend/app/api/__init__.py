from .routes.user_routes import user_bp
from .routes.user_routes import health_bp

def register_blueprints(app):
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(health_bp, url_prefix="/api/health")
