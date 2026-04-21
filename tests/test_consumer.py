import os
import json
import pytest

from app.consumers.consumer import process_message

# ─── Helpers ──────────────────────────────────────────────────────────────────

def seed(table, *items):
    for item in items:
        table.put_item(Item=item)


def send_order(queue, items):
    """Send an order.placed event to the moto SQS queue."""
    event = json.dumps({"event_type": "order.placed", "payload": {"items": items}})
    queue.send_message(
        MessageBody=json.dumps({"Message": event}),
        MessageGroupId="orders",
    )


def send_event(queue, event_type, payload):
    """Send an arbitrary event to the moto SQS queue."""
    event = json.dumps({"event_type": event_type, "payload": payload})
    queue.send_message(
        MessageBody=json.dumps({"Message": event}),
        MessageGroupId="orders",
    )


# ---------------------------------------------------------------------------
# process_message via SQS
# ---------------------------------------------------------------------------

@pytest.mark.skip
def test_process_message_order_placed_decrements_stock(consumer_table, sqs_queue):
    seed(consumer_table, {os.environ["KEY_NAME"]: "prod-1", "name": "Widget",
                          "stock": 10, "s3_key": "widget.jpg"})

    send_order(sqs_queue, [{"product_id": "prod-1", "quantity": 3}])
    messages = sqs_queue.receive_messages(MaxNumberOfMessages=1)

    result = process_message(messages[0])

    item = consumer_table.get_item(Key={os.environ["KEY_NAME"]: "prod-1"})["Item"]
    assert result is True
    assert item["stock"] == 7

@pytest.mark.skip
def test_process_message_order_placed_multiple_items_decrements_each(consumer_table, sqs_queue):
    seed(consumer_table,
         {os.environ["KEY_NAME"]: "prod-1", "name": "Widget", "stock": 10, "s3_key": "widget.jpg"},
         {os.environ["KEY_NAME"]: "prod-2", "name": "Gadget", "stock": 5, "s3_key": "gadget.jpg"})

    send_order(sqs_queue, [
        {"product_id": "prod-1", "quantity": 2},
        {"product_id": "prod-2", "quantity": 1},
    ])
    messages = sqs_queue.receive_messages(MaxNumberOfMessages=1)

    result = process_message(messages[0])

    item1 = consumer_table.get_item(Key={os.environ["KEY_NAME"]: "prod-1"})["Item"]
    item2 = consumer_table.get_item(Key={os.environ["KEY_NAME"]: "prod-2"})["Item"]
    assert result is True
    assert item1["stock"] == 8
    assert item2["stock"] == 4

@pytest.mark.skip
def test_process_message_unknown_event_type_does_not_modify_stock(consumer_table, sqs_queue):
    seed(consumer_table, {os.environ["KEY_NAME"]: "prod-1", "name": "Widget",
                          "stock": 10, "s3_key": "widget.jpg"})

    send_event(sqs_queue, "order.cancelled", {
        "items": [{"product_id": "prod-1", "quantity": 3}]
    })
    messages = sqs_queue.receive_messages(MaxNumberOfMessages=1)

    result = process_message(messages[0])

    item = consumer_table.get_item(Key={os.environ["KEY_NAME"]: "prod-1"})["Item"]
    assert result is True
    assert item["stock"] == 10

@pytest.mark.skip
def test_processed_message_is_deleted_from_sqs(consumer_table, sqs_queue):
    seed(consumer_table, {os.environ["KEY_NAME"]: "prod-1", "name": "Widget",
                          "stock": 10, "s3_key": "widget.jpg"})

    send_order(sqs_queue, [{"product_id": "prod-1", "quantity": 1}])
    messages = sqs_queue.receive_messages(MaxNumberOfMessages=1)

    process_message(messages[0])
    messages[0].delete()

    remaining = sqs_queue.receive_messages(MaxNumberOfMessages=1)
    assert remaining == []