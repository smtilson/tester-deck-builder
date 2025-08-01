from fastapi import APIRouter, Depends

from app.core.auth import current_user, fastapi_users
from app.core.pagination import Page, Params, paginate
from fast_backend.app.services.worker import queue

from ...models import User
from ...schemas import UserRead, UserUpdate

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/", response_model=Page[UserRead], dependencies=[Depends(current_user)])
async def user_list(params: Params = Depends()):
    return await paginate(User.all(), params)


@users_router.get("/log-user-info")
async def log_user_info(user: User = Depends(current_user)):
    await queue.enqueue("log_user_email", user_email=user.email)

users_router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)

