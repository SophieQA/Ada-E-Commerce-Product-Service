import os
import boto3
from .tables.products import products_table
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

def generate_presigned_url(item):
    if not item.get("s3_key"):
        item["image_url"] = ""
        return

    CLIENT_METHOD = "get_object"
    EXPIRES_IN = 1000
    REGION_NAME = os.environ.get("REGION_NAME")
    BUCKET_NAME = os.environ.get("BUCKET_NAME")

    if not BUCKET_NAME:
        raise ValueError("BUCKET environment variable not set")

    METHOD_PARAMS = {
        "Bucket": BUCKET_NAME,
        "Key": f"images/{item.get("s3_key")}",
    }

    try:
        s3_client = boto3.client(
            "s3", 
            region_name=REGION_NAME,
            config=boto3.session.Config(
                signature_version="s3v4",
                s3={"addressing_style": "virtual"}
            )
          )
        url = s3_client.generate_presigned_url(
            ClientMethod=CLIENT_METHOD,
            Params=METHOD_PARAMS,
            ExpiresIn=EXPIRES_IN
        )
        item["image_url"] = url

    except ClientError:
        raise RuntimeError("There was an error generating URL")


def validate_item(table, id):
    KEY_NAME = os.environ.get("KEY_NAME")
    response = table.get_item(Key={KEY_NAME: id})
    item = response.get("Item")

    if not item:
        raise LookupError(f"Item with {KEY_NAME} ({id}) not found.")

    generate_presigned_url(item)

    return item


def get_items_with_filters(table, args):
    sort_by = args.get("sort_by")
    order = args.get("order", "asc").lower()
    name = args.get("name")

    sortable_fields = {"name", "price"}

    if sort_by and sort_by not in sortable_fields:
        raise ValueError(f"sort_by must be one of: {', '.join(sortable_fields)}")

    if order not in ("asc", "desc"):
        raise ValueError("order must be asc or desc")

    scan_kwargs = {}
    if name:
        scan_kwargs["FilterExpression"] = Attr("name").contains(name)

    response = table.scan(**scan_kwargs)
    items = response["Items"]

    for item in items:
        generate_presigned_url(item)

    if sort_by:
        reverse = order == "desc"
        items.sort(key=lambda item: item.get(sort_by, ""), reverse=reverse)

    return items


def build_and_run_update(table, id, body):
    KEY_NAME = os.environ.get("KEY_NAME")
    existing = validate_item(table, id)

    allowed = {k: v for k, v in body.items() if k in existing and k != KEY_NAME}

    if not allowed:
        raise ValueError("No valid attributes to update")

    update_expr = "SET " + \
        ", ".join(f"#n{i} = :v{i}" for i in range(len(allowed)))
    attr_names = {f"#n{i}": k for i, k in enumerate(allowed.keys())}
    attr_values = {f":v{i}": v for i, v in enumerate(allowed.values())}

    table.update_item(
        Key={KEY_NAME: id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
    )

    return True

def decrement_stock(id, quantity):
    item = validate_item(products_table, id)
    build_and_run_update(products_table, id, {
        "quantity": item["quantity"] - quantity
    })

    return True