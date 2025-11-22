import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models import User, TokenData

def verify_password(plain_password, hashed_password):
    """验证密码"""
    # bcrypt.checkpw 需要 bytes 类型
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)

def get_password_hash(password):
    """生成密码哈希"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    # 生成 salt 并 hash
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """生成 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # 将过期时间添加到 payload
    to_encode.update({"exp": expire})
    
    # 生成 JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenData]:
    """解析 JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        roles: List[str] = payload.get("roles", [])
        user_type: str = payload.get("user_type")
        permissions: List[str] = payload.get("permissions", [])
        
        return TokenData(
            username=username,
            roles=roles,
            user_type=user_type,
            permissions=permissions
        )
    except JWTError:
        return None
