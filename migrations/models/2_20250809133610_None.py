from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(1024) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_superuser" BOOL NOT NULL DEFAULT False,
    "is_verified" BOOL NOT NULL DEFAULT False,
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "version" VARCHAR(50),
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "name" VARCHAR(255),
    "is_admin" BOOL NOT NULL DEFAULT False
);
CREATE INDEX IF NOT EXISTS "idx_users_email_133a6f" ON "users" ("email");
CREATE TABLE IF NOT EXISTS "decks" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "version" VARCHAR(50),
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "description" TEXT,
    "is_valid" BOOL NOT NULL DEFAULT False,
    "owner_id" UUID NOT NULL
);
CREATE TABLE IF NOT EXISTS "cards" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "version" VARCHAR(50),
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "text" TEXT
);
CREATE TABLE IF NOT EXISTS "deck_cards" (
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "version" VARCHAR(50),
    "id" SERIAL NOT NULL PRIMARY KEY,
    "quantity" INT NOT NULL DEFAULT 1,
    "card_id" INT NOT NULL REFERENCES "cards" ("id") ON DELETE CASCADE,
    "deck_id" INT NOT NULL REFERENCES "decks" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_deck_cards_deck_id_41a536" UNIQUE ("deck_id", "card_id")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
