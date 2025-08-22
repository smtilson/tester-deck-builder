import sentry_sdk
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration
from contextlib import asynccontextmanager

# from fast_backend.app.core.auth import get_auth_router
from fast_backend.app.core.config_app import Environment, settings
from fast_backend.app.db.config_db import init_db, close_db
from fast_backend.app.health import router as health_check_router
from fast_backend.app.auth.fast_api_users_instance import fastapi_users

# from fast_backend.app.users.routes import router as users_router
from fast_backend.app.api.routes import router as api_router
from fast_backend.app.api.endpoints.test import router as test_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to database...")
    client = await init_db()
    try:
        yield  # app starts processing here,
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        print("Closing connection to database...")
        await close_db(client)


def get_application() -> FastAPI:
    _app = FastAPI(
        title="fast-backend",
        description="This is a backend for a card management system. The idea is that it be useable by playtesters and game developers alike.",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    # _app.include_router(get_auth_router())
    # _app.include_router(users_router)
    _app.include_router(health_check_router)
    _app.include_router(test_router, prefix="/test")
    #_app.include_router(api_router, prefix="/api")
    
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # below is for non testing I think
        # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if settings.ENVIRONMENT == Environment.prod:
        assert (
            settings.SENTRY_DSN
        ), "Set SENTRY_DSN to monitor and track errors in production!"
        sentry_sdk.init(
            settings.SENTRY_DSN, integrations=[LoggingIntegration()]# type: ignore[arg-type]
        )
        _app.add_middleware(SentryAsgiMiddleware)

    return _app


app = get_application()


@app.get("/")
async def root():
    return {"message": "Welcome to the fast-backend API!"}
