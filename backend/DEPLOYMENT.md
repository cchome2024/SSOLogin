# 生产环境部署指南

本文档说明如何将 SSO Login Service 部署到生产服务器。

## 📋 部署前检查清单

### 1. 安全配置

#### ✅ 必须修改的配置项

- [ ] **SECRET_KEY**: 必须使用强随机密钥（至少 32 字符）
- [ ] **COOKIE_SECURE**: 必须设置为 `True`（HTTPS 环境）
- [ ] **COOKIE_SAMESITE**: 跨域场景设置为 `"none"`，同域设置为 `"lax"`
- [ ] **COOKIE_DOMAIN**: 设置为你的域名（例如 `.chenchen.city`）
- [ ] **CORS_ORIGINS**: 明确指定允许的前端域名，不要使用通配符

#### ✅ 数据库安全

- [ ] 修改默认管理员密码（`admin123`）
- [ ] 删除或禁用测试用户
- [ ] 使用生产级数据库（PostgreSQL/MySQL），不要使用 SQLite

### 2. 服务器配置

#### ✅ 反向代理（推荐使用 Nginx）

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # SSL 证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 代理到后端
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### ✅ 进程管理（使用 systemd）

创建 `/etc/systemd/system/sso-login.service`:

```ini
[Unit]
Description=SSO Login Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
Environment="SECRET_KEY=your-secret-key-here"
Environment="COOKIE_DOMAIN=.yourdomain.com"
Environment="COOKIE_SECURE=True"
Environment="COOKIE_SAMESITE=none"
Environment="CORS_ORIGINS=https://app.yourdomain.com,https://www.yourdomain.com"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable sso-login
sudo systemctl start sso-login
sudo systemctl status sso-login
```

### 3. 环境变量配置

创建 `.env` 文件（不要提交到 Git）：

```bash
# 安全密钥（必须修改！）
SECRET_KEY=your-very-long-random-secret-key-at-least-32-characters

# Cookie 配置
COOKIE_DOMAIN=.yourdomain.com
COOKIE_SECURE=True
COOKIE_SAMESITE=none

# CORS 配置（用逗号分隔多个域名）
CORS_ORIGINS=https://app.yourdomain.com,https://www.yourdomain.com

# 认证模式
AUTH_MODE=required

# 数据库配置（如果使用 PostgreSQL/MySQL）
DATABASE_URL=postgresql://user:password@localhost/sso_db
```

### 4. 数据库迁移

#### 如果使用 SQLite（仅限小型应用）

```bash
# 备份现有数据库
cp database.db database.db.backup

# 数据库会自动初始化，但建议先检查
python -c "from app.database import init_db; init_db()"
```

#### 如果使用 PostgreSQL（推荐生产环境）

1. 安装 PostgreSQL 客户端库：
```bash
pip install psycopg2-binary
```

2. 修改 `app/database.py`:
```python
import os
from sqlmodel import SQLModel, Session, create_engine

database_url = os.getenv("DATABASE_URL", "sqlite:///database.db")
engine = create_engine(database_url)
```

3. 创建数据库：
```sql
CREATE DATABASE sso_db;
CREATE USER sso_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE sso_db TO sso_user;
```

### 5. 防火墙配置

```bash
# 只允许 Nginx 访问后端端口
sudo ufw allow from 127.0.0.1 to any port 8000
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 🚀 部署步骤

### 步骤 1: 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 和依赖
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# 创建应用目录
sudo mkdir -p /var/www/sso-login
sudo chown $USER:$USER /var/www/sso-login
```

### 步骤 2: 部署代码

```bash
# 克隆或上传代码
cd /var/www/sso-login
git clone <your-repo> backend
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤 3: 配置环境变量

```bash
# 创建 .env 文件
nano .env
# 填入上述环境变量配置

# 设置文件权限
chmod 600 .env
```

### 步骤 4: 配置 SSL 证书

```bash
# 使用 Let's Encrypt
sudo certbot --nginx -d api.yourdomain.com
```

### 步骤 5: 启动服务

```bash
# 测试运行
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 如果测试通过，使用 systemd 服务
sudo systemctl start sso-login
```

## 🔍 监控和日志

### 查看日志

```bash
# systemd 日志
sudo journalctl -u sso-login -f

# Nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 健康检查

```bash
# 检查服务状态
curl https://api.yourdomain.com/

# 检查 API 文档
curl https://api.yourdomain.com/docs
```

## 🔐 安全最佳实践

1. **定期更新依赖**
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

2. **定期备份数据库**
   ```bash
   # SQLite
   cp database.db backups/database-$(date +%Y%m%d).db
   
   # PostgreSQL
   pg_dump sso_db > backups/database-$(date +%Y%m%d).sql
   ```

3. **监控异常登录**
   - 实现登录日志记录
   - 设置失败登录次数限制
   - 实现 IP 白名单（如需要）

4. **定期轮换密钥**
   - 定期更换 SECRET_KEY
   - 更换后所有用户需要重新登录

5. **限制 API 访问速率**
   - 使用 Nginx rate limiting
   - 或使用 FastAPI 中间件实现限流

## 📝 常见问题

### Q: Cookie 无法跨域携带？

A: 确保：
- `COOKIE_SECURE=True`
- `COOKIE_SAMESITE=none`
- `COOKIE_DOMAIN` 设置为正确的域名（例如 `.yourdomain.com`）
- 前端请求时设置 `credentials: 'include'`

### Q: CORS 错误？

A: 检查：
- `CORS_ORIGINS` 环境变量包含前端域名
- 前端域名使用 HTTPS（生产环境）
- Nginx 配置正确转发请求头

### Q: 数据库连接失败？

A: 检查：
- 数据库服务是否运行
- `DATABASE_URL` 环境变量是否正确
- 数据库用户权限是否正确

## 🔄 更新部署

```bash
cd /var/www/sso-login/backend
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart sso-login
```

## 📞 支持

如有问题，请检查：
1. 日志文件
2. 环境变量配置
3. Nginx 配置
4. 防火墙规则

