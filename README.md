# Product Service

## Description

The Product Service is one of 3 microservices for the Ada Developers Academy Cloud Curriculum e-commerce application. It handles the creation and management of products, including inventory stock tracking.

### Data Models

- **Product** — represents a product listing, containing `name`, `description`, `price`, `stock`, and `s3_key` (for product images stored in S3)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/products/` | Create a new product |
| GET | `/products/` | Get all products (supports `name`, `sort_by`, and `order` query filters) |
| GET | `/products/<id>` | Get a single product by ID |
| PATCH | `/products/<id>` | Update a product by ID |
| DELETE | `/products/<id>` | Delete a product by ID |

## Prerequisites

- Python 3.13+
- AWS account or local AWS credentials (for DynamoDB and SQS consumer)

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd product-service
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```
TABLE_NAME=<your-dynamodb-table-name>
KEY_NAME=<your-dynamodb-partition-key>
BUCKET_NAME=<your-s3-bucket-name>
S3_DEFAULT_KEY=<default-s3-key-for-product-images>
QUEUE_URL=<your-sqs-queue-url>
```

## Running the App

```bash
flask run --debug
```

## Running the SQS Consumer

The consumer polls an SQS FIFO queue for `order.placed` events and decrements product stock accordingly. It runs as a standalone process separate from the Flask application.

```bash
python -m app.consumers.consumer
```

## Running Tests

```bash
pytest
```

## (Optional) Working With a Local DynamoDB Table

### 1. Set up environment variables

Add the local variables to your `.env` file alongside your real AWS values. Comment out whichever set you are not using:

```bash
# --- Real AWS (comment out when using local) ---
# TABLE_NAME=<your-dynamodb-table-name>
# KEY_NAME=<your-dynamodb-partition-key>
# BUCKET_NAME=<your-s3-bucket-name>
# AWS_DEFAULT_REGION=<your-aws-region>
# AWS_ACCESS_KEY_ID=<your-aws-access-key>
# AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>

# --- Local DynamoDB (comment out when using real AWS) ---
TABLE_NAME=products
KEY_NAME=product-key
BUCKET_NAME=local-product-images
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
AWS_ENDPOINT_URL_DYNAMODB=http://localhost:8000
```

### 2. Install Docker

```bash
brew install --cask docker
```

Then open the Docker app to complete installation and make sure it is running before proceeding.

### 3. Start a local DynamoDB Docker container

> Port 8000 must be available.

```bash
docker run --name dynamodb-local -p 8000:8000 amazon/dynamodb-local
```

### 4. Create the table

```bash
set -a; source .env; set +a; aws dynamodb create-table \
  --table-name "$TABLE_NAME" \
  --attribute-definitions AttributeName="$KEY_NAME",AttributeType=S \
  --key-schema AttributeName="$KEY_NAME",KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url "$AWS_ENDPOINT_URL_DYNAMODB" \
  --region "$AWS_DEFAULT_REGION"
```

### 5. Verify the table was created

```bash
aws dynamodb list-tables --endpoint-url http://localhost:8000 --region us-east-1
```

### Restarting the container

If the Docker container stops, restart it with:

```bash
docker start -ai dynamodb-local
```