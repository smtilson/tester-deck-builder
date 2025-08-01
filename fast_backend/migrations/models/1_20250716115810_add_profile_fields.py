from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "username" VARCHAR(255) NOT NULL UNIQUE;
        ALTER TABLE "users" ADD "is_admin" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "users" RENAME COLUMN "full_name" TO "name";
        ALTER TABLE "users" DROP COLUMN "short_name";
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_users_usernam_266d85" ON "users" ("username");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_users_usernam_266d85";
        ALTER TABLE "users" ADD "short_name" VARCHAR(255);
        ALTER TABLE "users" RENAME COLUMN "name" TO "full_name";
        ALTER TABLE "users" DROP COLUMN "username";
        ALTER TABLE "users" DROP COLUMN "is_admin";"""
