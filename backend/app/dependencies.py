from typing import Optional
from fastapi import Depends, HTTPException, status, Request, Cookie
from app.auth import decode_access_token
from app.models import UserResponse
from app.config import AUTH_MODE, COOKIE_NAME

async def get_current_user_optional(request: Request) -> Optional[UserResponse]:
    """
    从 Cookie 中尝试获取并解析当前用户。
    如果 Cookie 不存在或 Token 无效，返回 None。
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    
    token_data = decode_access_token(token)
    if not token_data:
        return None
        
    # 构造 UserResponse 对象
    return UserResponse(
        username=token_data.username,
        roles=token_data.roles,
        user_type=token_data.user_type,
        permissions=token_data.permissions
    )

async def login_required(user: Optional[UserResponse] = Depends(get_current_user_optional)) -> Optional[UserResponse]:
    """
    强制登录依赖项。
    根据 AUTH_MODE 配置决定行为：
    - required: 如果未登录，抛出 401 错误。
    - public: 即使未登录也允许通过 (返回 None)。
    """
    if AUTH_MODE == "required":
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return user
