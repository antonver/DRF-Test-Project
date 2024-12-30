Here is a README file based on the details you've provided:

---

# DRF Task Project

This project is a Django-based API system for managing book borrowings, users, and notifications, integrated with Telegram bot functionality for communication and updates. It includes scheduled tasks using Celery, notifications via Telegram, and a user authentication system with JWT.

## Features

- **Books Service**: Implements CRUD functionality for books.
  - Admins can create, update, and delete books.
  - All users can list books.
  
- **Users Service**: Manages user authentication with email and JWT tokens.
  - JWT token-based authentication is used for securing API endpoints.
  
- **Borrowing Service**: Handles book borrowing actions, including:
  - List and detail views for borrowings.
  - Users can create borrowings if books are available in the inventory.
  - Return borrowings functionality that updates book inventory.
  - Filtering by active borrowings and user-specific borrowings.
  
- **Telegram Bot**: Notifies users and admins about borrowing actions.
  - Sends notifications about new borrowings.
  - Sends notifications about overdue borrowings.
  - The bot also implements API functionality (e.g., creating borrowings, viewing borrowings).

- **Scheduled Tasks**: Uses Celery and `django-celery-beat` for background tasks.
  - Checks overdue borrowings daily and sends notifications.
  
- **Redis**: Used as a broker and backend for Celery.

## Project Setup

### Requirements

- Python 3.x
- Django
- Redis (Docker)
- Celery
- `django-celery-beat`
- `telebot` for Telegram bot functionality
- Redis should be running in Docker as the Celery broker and backend.

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/antonver/DRF-Test-Project.git
   cd <project_directory>
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Redis in Docker:**
   ```bash
   docker run -p 6379:6379 -d redis
   ```

4. **Set up environment variables:**
   Create a `.env` file to store your sensitive data like the Telegram bot API token, Redis configuration, and other credentials. Ensure `.env` is not pushed to GitHub by adding it to `.gitignore`.

5. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser to access the Django admin interface:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Celery worker and beat scheduler:**

   For Celery worker:
   ```bash
   celery -A drf_task_project worker -B
   ```

   For Celery beat (scheduler):
   ```bash
   celery -A drf_task_project beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
   ```

8. **Run the Django development server:**
   ```bash
   python manage.py runserver
   ```

9. **Access the Django admin panel at `http://127.0.0.1:8000/admin/` to manage the project.**

### How to Use the Telegram Bot

1. **Login the bot**: When the user logs in via the Telegram bot, their `chat_id` and `email` are associated in the user model.

2. **Interact with the bot**: The bot will send notifications and also provide the ability to interact with the API, such as creating borrowings or checking the status of borrowings.

### Testing

The project has 92% test coverage, and all the API endpoints are tested with comprehensive unit tests.

To run tests:
```bash
python manage.py test
```

### Reuse and Extending

You can reuse this project by forking it and modifying the models, views, and serializers for your own needs. The Telegram bot implementation allows for easy integration with other services or additional features.

