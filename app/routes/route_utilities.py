import os
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from flask import abort, make_response, Response


def generate_presigned_url(item):
    CLIENT_METHOD = "get_object"
    EXPIRES_IN = 1000
    REGION_NAME = "us-east-1"
    BUCKET_NAME = os.environ.get("BUCKET_NAME")

    if not BUCKET_NAME:
        raise ValueError("BUCKET environment variable not set")

    METHOD_PARAMS = {
        "Bucket": BUCKET_NAME,
        "Key": f"{item["s3_key"]}",
    }

    try:
        s3_client = boto3.client("s3", region_name=REGION_NAME)
        url = s3_client.generate_presigned_url(
            ClientMethod=CLIENT_METHOD,
            Params=METHOD_PARAMS,
            ExpiresIn=EXPIRES_IN
        )
        item["image_url"] = url

    except ClientError as e:
        abort(make_response("There was an error generating URL", 500))


def validate_item(table, key_name, id):
    response = table.get_item(Key={key_name: id})
    item = response.get("Item")

    if not item:
        not_found = {"message": f"Item with {key_name} ({id}) not found."}
        abort(make_response(not_found, 404))

    generate_presigned_url(item)

    return item


def get_items_with_filters(table, args):
    sort_by = args.get("sort_by")
    order = args.get("order", "asc").lower()
    name = args.get("name")

    sortable_fields = {"name", "price"}

    if sort_by and sort_by not in sortable_fields:
        return {"error": f"sort_by must be one of: {', '.join(sortable_fields)}"}, 400

    if order not in ("asc", "desc"):
        return {"error": "order must be asc or desc"}, 400

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

    return items, 200


def build_and_run_update(table, key, body):
    existing = validate_item(table, list(key.keys())[0], list(key.values())[0])

    allowed = {k: v for k, v in body.items() if k in existing and k not in key}

    if not allowed:
        abort(make_response({"message": "No valid attributes to update"}, 400))

    update_expr = "SET " + \
        ", ".join(f"#n{i} = :v{i}" for i in range(len(allowed)))
    attr_names = {f"#n{i}": k for i, k in enumerate(allowed.keys())}
    attr_values = {f":v{i}": v for i, v in enumerate(allowed.values())}

    table.update_item(
        Key=key,
        UpdateExpression=update_expr,
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
    )

    return Response(status=204, mimetype="application/json")
