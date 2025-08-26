from fastapi import APIRouter, Depends

from fast_backend.app.core.auth import current_user, fastapi_users
from fast_backend.app.core.pagination import Page, Params, paginate
from fast_backend.app.services.worker import queue

from fast_backend.app.models import User
from fast_backend.app.schemas import UserResponse, UserUpdate

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get(
    "/", response_model=Page[UserResponse], dependencies=[Depends(current_user)]
)
async def user_list(params: Params = Depends()):
    return await paginate(User.all(), params)


@users_router.get("/log-user-info")
async def log_user_info(user: User = Depends(current_user)):
    await queue.enqueue("log_user_email", user_email=user.email)


users_router.include_router(
    fastapi_users.get_users_router(UserResponse, UserUpdate),
)
