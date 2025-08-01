from __future__ import annotations

from fastapi_users_tortoise import (
    TortoiseBaseUserAccountModelUUID,
    TortoiseUserDatabase,
)
from tortoise import fields

from .base import BasicModel


class User(TortoiseBaseUserAccountModelUUID, BasicModel):
    username = fields.CharField(max_length=255, unique=True)
    # email, is_superuser, is_active, is_verified,
    # and hashed_password are inherited from TortoiseBaseUserAccountModelUUID
    name = fields.CharField(max_length=255, null=True)
    is_admin = fields.BooleanField(default=False)
    class Meta:
        table = "users"

    def __str__(self):
        return self.username or self.name or self.email