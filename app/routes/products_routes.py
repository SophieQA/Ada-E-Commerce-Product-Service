import os
from uuid import uuid4
from decimal import Decimal
from ..tables.products import products_table
from flask import Blueprint, request, Response
from .route_utilities import build_and_run_update, get_items_with_filters, validate_item

bp = Blueprint("products_bp", __name__, url_prefix="/products")
KEY_NAME = os.environ.get("KEY_NAME")

@bp.post("/")
def create_product():
  product_info = request.get_json()
  product_info[KEY_NAME] = str(uuid4())

  if product_info.get("price"):
    product_info["price"] = Decimal(str(product_info["price"]))
  
  products_table.put_item(Item=product_info)

  return product_info

@bp.get("/")
def get_all_products():
  items = get_items_with_filters(products_table, request.args)
  return items

@bp.get("/<product_id>")
def get_single_product(product_id):
    product = validate_item(products_table, KEY_NAME, product_id)
    return product 

@bp.patch("/<product_id>")
def update_product(product_id):
    body = request.get_json()
    return build_and_run_update(products_table, {KEY_NAME: product_id}, body)

@bp.delete("/<product_id>")
def delete_product(product_id):
  products_table.delete_item(Key={ KEY_NAME: product_id })

  return Response(status=204, mimetype="application/json")