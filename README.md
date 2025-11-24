# BackendLab1 - Recipe API with Authentication

FastAPI-based Recipe Management API with user authentication and authorization.

## Features

- User registration and authentication (JWT-based)
- Recipe CRUD operations with author tracking
- Authorization checks (only recipe authors can update/delete their recipes)
- Cuisine, Allergen, and Ingredient management
- Recipe filtering and pagination

## Setup

1. Install dependencies:
```bash
pip install -e .
```

2. Create `.env` file from template:
```bash
cp .env.template .env
```

3. Run the application:
```bash
cd app
python -m uvicorn main:main_app --reload
```

## Authentication

### Register a new user
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

This returns an access token that should be used in subsequent requests.

## Recipe Operations

### Create Recipe (requires authentication)
```bash
curl -X POST http://localhost:8000/api/lab1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Spaghetti Carbonara",
    "description": "Classic Italian pasta",
    "cooking_time": 30,
    "difficulty": 2,
    "cuisine_id": 1,
    "allergen_ids": [1],
    "ingredients": [{"ingredient_id": 1, "quantity": 200, "measurement": 1}]
  }'
```

### Get Recipes (public)
```bash
curl http://localhost:8000/api/lab1/
curl http://localhost:8000/api/lab1/1
```

### Update Recipe (requires authentication + ownership)
```bash
curl -X PUT http://localhost:8000/api/lab1/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title": "Updated Title"}'
```

### Delete Recipe (requires authentication + ownership)
```bash
curl -X DELETE http://localhost:8000/api/lab1/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
