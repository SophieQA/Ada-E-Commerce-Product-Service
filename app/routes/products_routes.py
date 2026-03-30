from ..tables.products import products_table
from flask import Blueprint, request
from decimal import Decimal
from uuid import uuid4

bp = Blueprint("products_bp", __name__, url_prefix="/products")

@bp.post("/")
def create_product():
  product_info = request.get_json()
  product_info["product-key"] = str(uuid4())

  if product_info.get("price"):
    product_info["price"] = Decimal(str(product_info["price"]))
  
  products_table.put_item(Item=product_info)

  return product_info

@bp.get("/")
def get_all_products():
  response = products_table.scan()

  return response["Items"]

@bp.get("/<id>")
def get_single_product(id):
  response = products_table.get_item(Key={
    'product-key': id
  })

  return response["Item"]

@bp.patch("/<product_id>")
def update_product(id):
  products_table.upate_item(Key={
    'product-key': id
  })