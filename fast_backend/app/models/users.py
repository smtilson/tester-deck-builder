from __future__ import annotations

from fastapi_users_tortoise import (
    TortoiseBaseUserAccountModelUUID,
    TortoiseUserDatabase,
)
from tortoise import fields

from app.models.base import BasicModel


class User(TortoiseBaseUserAccountModelUUID, BasicModel):
    short_name = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "users"

    def __str__(self):
        return self.short_name or self.full_name or self.email


async def get_user_db():
    yield TortoiseUserDatabase(User)
