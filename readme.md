# Order Service

Simple Django REST service for creating orders with promo codes.


---

## Features 

- Order creation  
- Promo codes support  
- Category-based discounts  
- Excluded goods logic  

---

## Tech Stack

- Python 3.12  
- Django 4.2
- Django REST Framework  
- drf-spectacular  
- PostgreSQL 
- Poetry  

---

## Create Order Example

### Request
```json
{
  "user_id": 2,
  "goods": [
    { "good_id": 1, "quantity": 2 },
    { "good_id": 2, "quantity": 1 }
  ],
  "promo_code": "SALE10"
}
```

### Response
```json
{
  "user_id": 2,
  "order_id": 2,
  "goods": [
    {
      "good_id": 1,
      "quantity": 2,
      "price": 100,
      "discount": 0.1,
      "total": 180
    },
    {
      "good_id": 2,
      "quantity": 1,
      "price": 500,
      "discount": 0.1,
      "total": 450
    }
  ],
  "price": 700,
  "discount": 0.1,
  "total": 630
}
```

---

## Setup


```bash
git clone https://github.com/issmushi/order-service.git
cd order-service

# create env file
cp .env.template .env

# run database
docker-compose up -d

# local run
poetry install

poetry run python manage.py migrate
poetry run python manage.py runserver

# run tests
poetry run python manage.py test apps.orders.tests.test_create_order    
```
---
