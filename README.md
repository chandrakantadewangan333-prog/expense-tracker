# 💸 Expense Tracker Web App (Django)

A full-featured expense tracking web application built using **Django**, designed to help users manage their expenses and stay within a monthly budget.

## 🚀 Features

- User authentication and session management
- Add, update, delete expenses
- Monthly limit setting with smart validations:
  - Prevents setting limit below total spent
  - Blocks adding expenses if they exceed the monthly limit
  - Warns when 80% of the limit is used
- Responsive UI with Bootstrap 5
- Flash messages for success/error feedback
- Modal form for setting limits
- Pagination for viewing expenses
- SQLite backend with Django ORM models

## 🛠️ Tech Stack

- Django (Python)
- SQLite
- Bootstrap 5
- HTML5, CSS3, JavaScript (jQuery)
- Chart.js *(optional enhancement)*

## Install dependencies

pip install -r requirements.txt

## Run migrations

- python manage.py makemigrations
- python manage.py migrate

## Run the server

python manage.py runserver

## Visit in browser

http://localhost:8000



