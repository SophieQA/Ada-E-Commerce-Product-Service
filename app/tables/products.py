from decimal import Decimal
import os
import boto3
from dotenv import load_dotenv

load_dotenv()

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get("REGION_NAME"))
products_table = dynamodb.Table(name=os.environ.get("TABLE_NAME"))

# # Scan to see all products
# response = products_table.scan()
# print("Current products in table:")
# for item in response['Items']:
#     print(f"- {item.get('product_key')}: {item.get('product_name')}")

# # Add the products that the order system expects
# new_products = [
#     {
#         'product_key': 'sku-001',
#         'product_name': 'Notebook',
#         'product_price': Decimal('12.5'),
#         'quantity': 100
#     },
#     {
#         'product_key': 'sku-007',
#         'product_name': 'Pen', 
#         'product_price': Decimal('1.75'),
#         'quantity': 100
#     }
# ]

# for product in new_products:
#     products_table.put_item(Item=product)
#     print(f"Added product: {product['product_key']} - {product['product_name']}")

# Check the structure of your products
response = products_table.scan()
print("Current product structure:")
for item in response['Items']:
    print(f"Product {item['product_key']}:")
    for key, value in item.items():
        print(f"  {key}: {value}")
    print()


# # Update S001 and S002 to use 'quantity' instead of 'stock'
# products_to_fix = [
#     {'product_key': 'S001', 'stock_value': 90},
#     {'product_key': 'S002', 'stock_value': 100}
# ]

# for product in products_to_fix:
#     # Add quantity field and remove stock field
#     products_table.update_item(
#         Key={'product_key': product['product_key']},
#         UpdateExpression='SET quantity = :qty REMOVE stock',
#         ExpressionAttributeValues={':qty': product['stock_value']}
#     )
#     print(f"Updated {product['product_key']} to use 'quantity' field")

