# Medical Appointments

This repository contains the backend and frontend for a medical appointments application.

## Environment Variables

Create a `.env` file inside the `backend` directory with the variables below. You can also export them in your shell.

Required:

- `SECRET_KEY` – Django secret key used for cryptographic signing.

Optional (for email and debugging):

- `DEBUG` – set to `True` for development.
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

Frontend:

- `VUE_APP_API_URL` – Base URL used by the Vue app to reach the backend. Defaults to `/api/`.

## Running the Backend

1. Install Python requirements:
   ```bash
   pip install -r backend/requirements.txt
   ```
2. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
3. (Optional) create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
4. Start the development server:
   ```bash
   python manage.py runserver
   ```

Run these commands from inside the `backend` directory.

## Running the Frontend

From the `frontend` directory run:

```bash
npm install
npm run serve
```

`npm run serve` launches the Vue development server with `VUE_APP_API_URL` set to
`http://127.0.0.1:8000/api/`. When building for production the `npm run build`
script uses the default `/api/` path.

## Optional Setup

You can enable two-factor authentication (2FA) from your user profile after signing in. Follow the on-screen instructions to scan the QR code and confirm the verification code.

## Running Tests

1. Install the Python requirements from `backend/requirements.txt`.
2. Ensure `SECRET_KEY` is set in `backend/.env` or exported as an environment variable.
3. Execute the tests from the `backend` directory with `python manage.py test`.
4. Tests run using a separate SQLite database located at `backend/test_db.sqlite3` which can be safely removed after the tests finish.

## License

This project is licensed under the [MIT License](LICENSE).
