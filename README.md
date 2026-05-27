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
REGION_NAME=<region-of-dynamodb-table-and-s3-bucket>
S3_DEFAULT_KEY=<default-s3-key-for-product-images>
```

## Running the App

```bash
flask run --debug
```

## Running Tests

```bash
pytest
```