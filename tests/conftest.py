import os
import boto3
import pytest
from moto import mock_aws

TABLE_NAME = "test-table"
KEY_NAME = "product-key"

os.environ["TABLE_NAME"] = TABLE_NAME
os.environ["KEY_NAME"] = KEY_NAME
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"

from app import create_app


@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": KEY_NAME, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": KEY_NAME, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        yield table


@pytest.fixture
def client(app, dynamodb_table):
    import app.routes.products_routes as routes_module
    original = routes_module.products_table
    routes_module.products_table = dynamodb_table
    with app.test_client() as c:
        yield c
    routes_module.products_table = original
