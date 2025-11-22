from fastapi import APIRouter, Depends
from app.dependencies import login_required
from app.models import UserResponse

router = APIRouter(prefix="/pc", tags=["pc"])

@router.get("/api/data")
async def get_pc_data(user: UserResponse = Depends(login_required)):
    """
    PC 业务接口示例
    需要登录才能访问
    """
    return {
        "project": "pc",
        "user": {
            "username": user.username,
            "roles": user.roles,
            "user_type": user.user_type,
            "permissions": user.permissions
        },
        "items": [
            {"id": 1, "name": "PC Item 1"},
            {"id": 2, "name": "PC Item 2"}
        ]
    }
