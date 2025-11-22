from fastapi import APIRouter, Depends
from app.dependencies import login_required
from app.models import UserResponse

router = APIRouter(prefix="/fs", tags=["fs"])

@router.get("/api/data")
async def get_fs_data(user: UserResponse = Depends(login_required)):
    """
    FS 业务接口示例
    需要登录才能访问
    """
    return {
        "project": "fs",
        "user": {
            "username": user.username,
            "roles": user.roles,
            "user_type": user.user_type,
            "permissions": user.permissions
        },
        "items": [
            {"id": 101, "name": "File System Item A"},
            {"id": 102, "name": "File System Item B"}
        ]
    }
