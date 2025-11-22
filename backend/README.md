# SSO Login Service Walkthrough

This backend service implements a Single Sign-On (SSO) system using FastAPI, JWT, and HttpOnly Cookies.

## Prerequisites

- Python 3.10+
- pip

## Installation

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    *Note: This will also install `sqlmodel` and `bcrypt`.*

## Running the Server

Start the server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.
On the first run, it will automatically create a `database.db` file and initialize default users (`admin` and `user`).

## API Usage & Testing

You can use the interactive API docs at `http://127.0.0.1:8000/docs` to test the endpoints.

### 1. Login
- **Endpoint**: `POST /auth/login`
- **Credentials**:
    - Username: `admin`
    - Password: `admin123`
- **Response**: Returns a JWT token and sets the `sso_token` HttpOnly cookie.

### 2. Check Login Status (Me)
- **Endpoint**: `GET /auth/me`
- **Behavior**: Automatically reads the `sso_token` cookie. Returns user details including `roles`, `user_type`, and `permissions`.

### 3. Access Protected Resources
- **PC Endpoint**: `GET /pc/api/data`
- **FS Endpoint**: `GET /fs/api/data`
- **Behavior**: Requires a valid login. Returns data specific to the service along with user context.

### 4. Logout
- **Endpoint**: `POST /auth/logout`
- **Behavior**: Clears the `sso_token` cookie.

## Configuration

Configuration is located in `app/config.py`. Key settings:
- `SECRET_KEY`: Change this for production!
- `COOKIE_DOMAIN`: Set to your domain (e.g., `.chenchen.city`) in production.
- `AUTH_MODE`: Defaults to `required`. Set to `public` to make login optional.
