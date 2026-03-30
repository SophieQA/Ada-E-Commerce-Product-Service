from flask import Flask
from .routes.products_routes import bp as products_bp
import os

def create_app():
  app = Flask(__name__)

  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  app.register_blueprint(products_bp)

  @app.get('/')
  def index():
    return {
      "status": "ok"
    }

  return app