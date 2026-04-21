from flask import Flask
from .routes.products_routes import bp as products_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(products_bp)

    @app.get('/')
    def index():
        return {
            "status": "ok"
        }

    return app
