from flask import Flask
from flask_cors import CORS
from .routes.products_routes import bp as products_bp


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(products_bp)

    @app.get('/')
    def index():
        return {
            "status": "ok"
        }

    return app
