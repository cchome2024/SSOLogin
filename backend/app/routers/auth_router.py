from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.auth import verify_password, create_access_token
from app.models import User, Token, UserResponse, LoginRequest
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_NAME, COOKIE_DOMAIN, COOKIE_SECURE, COOKIE_SAMESITE
from app.dependencies import get_current_user_optional
from app.database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])

def _create_login_response(user: User, response: Response):
    """创建登录响应的辅助函数"""
    # 生成 Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "roles": user.roles,
            "user_type": user.user_type,
            "permissions": user.permissions
        },
        expires_delta=access_token_expires
    )
    
    # 设置 Cookie
    # 开发环境：domain=None (不设置)，secure=False，让浏览器自动处理 localhost 跨端口
    cookie_params = {
        "key": COOKIE_NAME,
        "value": access_token,
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE,
        "max_age": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    # 只有当 domain 不为 None 时才设置 domain（开发环境留空）
    if COOKIE_DOMAIN:
        cookie_params["domain"] = COOKIE_DOMAIN
    
    response.set_cookie(**cookie_params)
    
    # 构造响应
    user_response = UserResponse(
        username=user.username,
        roles=user.roles,
        user_type=user.user_type,
        permissions=user.permissions
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    登录接口 (支持 JSON 和表单两种格式):
    1. JSON 格式: {"username": "admin", "password": "admin123"}
    2. 表单格式: application/x-www-form-urlencoded (OAuth2 标准格式)
    
    流程:
    1. 验证用户名密码 (从数据库读取)
    2. 生成 JWT
    3. 设置 HttpOnly Cookie
    4. 返回 Token 和用户信息
    """
    content_type = request.headers.get("content-type", "").lower()
    username = None
    password = None
    
    # 根据 Content-Type 解析请求数据
    if "application/json" in content_type:
        # JSON 格式
        try:
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid JSON format: {str(e)}"
            )
    else:
        # 表单格式 (application/x-www-form-urlencoded)
        try:
            form = await request.form()
            username = form.get("username")
            password = form.get("password")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid form data: {str(e)}"
            )
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing required fields: username and password. Please send JSON: {'username': 'xxx', 'password': 'xxx'} or form data."
        )
    
    # 从数据库查找用户
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return _create_login_response(user, response)

@router.get("/me", response_model=UserResponse)
async def read_users_me(user: UserResponse = Depends(get_current_user_optional)):
    """
    获取当前登录用户信息 (通过 Cookie 自动验证)
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user

@router.post("/logout")
async def logout(response: Response):
    """
    登出接口: 清除 Cookie
    """
    # 清除 Cookie，开发环境 domain=None (不设置)
    cookie_params = {
        "key": COOKIE_NAME,
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": COOKIE_SAMESITE
    }
    # 只有当 domain 不为 None 时才设置 domain（开发环境留空）
    if COOKIE_DOMAIN:
        cookie_params["domain"] = COOKIE_DOMAIN
    
    response.delete_cookie(**cookie_params)
    return {"message": "logged out"}
