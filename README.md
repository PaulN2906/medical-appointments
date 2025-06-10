# Medical Appointments

This repository contains the backend and frontend for a medical appointments application.

## Environment Variables

The backend uses the following environment variables:

- `SECRET_KEY` – the Django secret key used for cryptographic signing. **Required**.

Create a `.env` file in the `backend` directory and define these variables before running the app.

## Running Tests

1. Install the Python requirements from `backend/requirements.txt`.
2. Ensure `SECRET_KEY` is set in `backend/.env` or exported as an environment variable.
3. Execute the tests from the `backend` directory with `python manage.py test`.
4. Tests run using a separate SQLite database located at `backend/test_db.sqlite3` which can be safely removed after the tests finish.
