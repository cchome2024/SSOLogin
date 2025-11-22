from typing import List, Optional
from sqlmodel import SQLModel, Field
from pydantic import BaseModel
import json

# 基础用户模型 (Pydantic)
class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    user_type: str
    # SQLite 不直接支持 List，我们存为 JSON 字符串，读取时再转换
    # 这里为了简化，我们在 DB 模型中用 str 存储，在业务逻辑中转换
    # 或者使用 Pydantic 的 validator (但在 SQLModel 中直接用 str 存比较简单)
    roles_json: str = "[]"
    permissions_json: str = "[]"

    @property
    def roles(self) -> List[str]:
        return json.loads(self.roles_json)

    @roles.setter
    def roles(self, value: List[str]):
        self.roles_json = json.dumps(value)

    @property
    def permissions(self) -> List[str]:
        return json.loads(self.permissions_json)

    @permissions.setter
    def permissions(self, value: List[str]):
        self.permissions_json = json.dumps(value)

# 数据库表模型
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

# 用于 API 响应的 Pydantic 模型 (不包含 hashed_password)
class UserResponse(BaseModel):
    username: str
    roles: List[str]
    user_type: str
    permissions: List[str]

# 登录请求模型 (支持 JSON)
class LoginRequest(BaseModel):
    username: str
    password: str

# Token 响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Token 数据载荷
class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []
    user_type: Optional[str] = None
    permissions: List[str] = []
