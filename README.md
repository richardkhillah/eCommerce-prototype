# ShopRK — eCommerce Prototype
A full-stack e-commerce platform built with Django and deployed on AWS. Supports user registration, product browsing, shopping cart, PayPal checkout, order tracking, and refund requests via a customer dashboard.

## Why I Built This
I wanted end-to-end experience building a real commerce flow — from authentication and session management through payment processing and post-purchase customer tooling. The refund dashboard in particular mirrors the kind of customer lifecycle tooling I find interesting to build and use.

## Stack
Python, Django, PostgreSQL, JavaScript, Bootstrap, AWS (EC2, S3), PayPal REST API

## Running Locally
bash```
git clone https://github.com/richardkhillah/eCommerce-prototype
cd eCommerce-prototype
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Note: PayPal sandbox credentials and AWS config are required for full functionality. Contact me for setup details.
