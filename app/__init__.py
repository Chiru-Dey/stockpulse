import os

from flask import Flask, jsonify

from config import Config
from .extensions import db, jwt, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
    )

    # Import models so they are registered with SQLAlchemy before DB creation
    from . import models
    from .api.auth import auth_bp
    from .api.categories import categories_bp
    from .api.products import products_bp
    from .api.movements import movements_bp
    from .api.dashboard import dashboard_bp
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(movements_bp)
    app.register_blueprint(dashboard_bp)

    @app.get("/api/health")
    def health():
        return jsonify(service="StockPulse", status="ok")

    return app