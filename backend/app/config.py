import os
from datetime import timedelta

# 密钥配置 (生产环境请使用环境变量)
SECRET_KEY = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token 有效期 24 小时

# 认证模式: required (必须登录) / public (可选登录)
AUTH_MODE = os.getenv("AUTH_MODE", "required")

# Cookie 配置
COOKIE_NAME = "sso_token"
# 域名配置: 开发环境为 None (留空，不设置 domain)，生产环境例如 ".chenchen.city"
# 开发环境下设置为 None 可以让浏览器自动处理 localhost 的跨端口 Cookie
_cookie_domain = os.getenv("COOKIE_DOMAIN", "").strip()
COOKIE_DOMAIN = _cookie_domain if _cookie_domain else None
# 安全配置: 开发环境为 False (HTTP)，生产环境应为 True (HTTPS)
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() == "true"
# SameSite 配置: 
# - "lax": 适用于同站点或顶级导航（适用于 localhost 同端口）
# - "none": 允许跨站 Cookie（需要 secure=True，适用于 HTTPS 跨域场景）
# - "strict": 最严格，不允许任何跨站请求携带 Cookie
# 开发环境默认 "lax"，对于 localhost 跨端口场景，现代浏览器通常允许
# 如果遇到跨端口 Cookie 不携带的问题，可以尝试设置为 "none"（但需要配合 secure=True，仅适用于 HTTPS）
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")

def get_access_token_expires():
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
