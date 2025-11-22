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

## Production Deployment

**⚠️ 重要：部署到生产环境前，请务必阅读 [DEPLOYMENT.md](./DEPLOYMENT.md)**

生产环境部署的关键注意事项：

1. **安全配置**（必须修改）：
   - 使用强随机 `SECRET_KEY`
   - 设置 `COOKIE_SECURE=True`（HTTPS）
   - 配置 `COOKIE_DOMAIN` 为你的域名
   - 明确设置 `CORS_ORIGINS`，不要使用通配符

2. **环境变量**：
   ```bash
   SECRET_KEY=your-secret-key
   COOKIE_DOMAIN=.yourdomain.com
   COOKIE_SECURE=True
   COOKIE_SAMESITE=none
   CORS_ORIGINS=https://app.yourdomain.com
   ```

3. **数据库**：
   - 修改默认管理员密码
   - 考虑使用 PostgreSQL/MySQL（生产环境）

4. **服务器**：
   - 使用 Nginx 作为反向代理
   - 配置 SSL/TLS 证书
   - 使用 systemd 管理服务进程

详细部署指南请参考：[DEPLOYMENT.md](./DEPLOYMENT.md)