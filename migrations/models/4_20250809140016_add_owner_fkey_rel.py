from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "decks" ADD "owner_id" uuid.UUID NOT NULL;
        ALTER TABLE "decks" ADD CONSTRAINT "fk_decks_users_677c09b6" FOREIGN KEY ("owner_id") REFERENCES "users" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "decks" DROP CONSTRAINT IF EXISTS "fk_decks_users_677c09b6";
        ALTER TABLE "decks" DROP COLUMN "owner_id";"""
