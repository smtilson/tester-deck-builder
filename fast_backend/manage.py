from __future__ import annotations

import asyncio
import os
import secrets
import subprocess
import sys
from functools import partial
from itertools import chain
from pathlib import Path

import httpx
import typer
import uvicorn
from email_validator import EmailNotValidError, validate_email
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists
from honcho.manager import Manager as HonchoManager

from beanie import init_beanie, Document
from motor.motor_asyncio import AsyncIOMotorClient

from fast_backend.app.models import User as BeanieUser
from fast_backend.app.schemas import UserCreate
from fast_backend.app.auth.manager import get_user_manager

from fast_backend.app.core.config_app import settings
from fast_backend.app.models import Card
from fast_backend.app.models import Deck
from fast_backend.app.models import DeckCard
from fast_backend.app.models import Game

cli = typer.Typer()

BEANIEDB_MODELS = [BeanieUser, Card, Deck, Game]
# is this right?
MONGO_DB_URL = "mongodb://localhost:27017"
DB_NAME = "fastapi_app_db"  # Use a specific name for your application's database


async def _init_mongodb_beanie():
    """Initialize MonogDB connection with Beanie ODM."""
    client = AsyncIOMotorClient(MONGO_DB_URL)
    await init_beanie(database=client[DB_NAME], document_models=BEANIEDB_MODELS)


def _validate_email(val: str):
    try:
        validate_email(val)
    except EmailNotValidError:
        raise typer.BadParameter(f"{val} is not a valid email")
    return val


@cli.command("init-db", text="Initialize the database")
def init_db():
    """Initialize MongoDB collections for development."""

    async def _init():
        client = AsyncIOMotorClient(MONGO_DB_URL)
        await init_beanie(database=client[DB_NAME], document_models=BEANIEDB_MODELS)
        typer.secho(
            "MongoDB and Beanie initialized. Collections ready.", fg=typer.colors.GREEN
        )
        await client.close()

    asyncio.run(_init())


@cli.command("work")
def work(mailserver: bool = typer.Option(False)):
    """Run all the dev services in a single command."""
    manager = HonchoManager()
    project_env = {
        **os.environ,
        "PYTHONPATH": str(Path().resolve(strict=True)),
        "PYTHONUNBUFFERED": "true",
    }

    manager.add_process("server", "python manage.py run-server", env=project_env)
    manager.add_process("worker", "python manage.py run-worker", env=project_env)
    if mailserver:
        manager.add_process("mailserver", "python manage.py run-mailserver")

    manager.loop()
    sys.exit(manager.returncode)


@cli.command("run-server")
def run_server(
    port: int = 8000,
    host: str = "localhost",
    log_level: str = "debug",
    reload: bool = True,
):
    """Run the API development server(uvicorn)."""
    asyncio.run(_init_mongodb_beanie())
    uvicorn.run(
        "fast_backend.app.main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload,
    )


@cli.command("run-prod-server")
def run_prod_server():
    """Run the API production server(gunicorn)."""
    from gunicorn import util
    from gunicorn.app.base import Application

    config_file = str(
        settings.PATHS.ROOT_DIR.joinpath("gunicorn.conf.py").resolve(strict=True)
    )

    class APPServer(Application):
        def init(self, parser, opts, args):
            pass

        def load_config(self):
            self.load_config_from_file(config_file)

        def load(self):
            return util.import_app("fast_backend.app.main:app")

    asyncio.run(_init_mongodb_beanie())
    APPServer().run()


# blech does this need to be edited to match my model
@cli.command("create-user")
def create_user(
    email: str = typer.Option(..., prompt=True, callback=_validate_email),
    password: str = typer.Option(..., prompt=True, hide_input=True),
    username: str = typer.Option("", prompt=True),
    name: str = typer.Option("", prompt=True),
    is_superuser: bool = typer.Option(False, prompt=True),
):
    """Create a new user."""

    async def _create_user_in_db():
        await _init_mongodb_beanie()
        user_manager = get_user_manager()
        user_create = UserCreate(
            email=email,
            password=password,
            username=username,
            name=name,
            is_superuser=is_superuser,
        )
        try:
            await user_manager.create(user_create, safe=True)
        finally:
            pass

    try:
        asyncio.run(_create_user_in_db())
    except UserAlreadyExists:
        typer.secho(f"user with {email} already exists", fg=typer.colors.BLUE)
    except InvalidPasswordException:
        typer.secho("Invalid password", fg=typer.colors.RED)
    else:
        typer.secho(f"user {email} created", fg=typer.colors.GREEN)


@cli.command("start-app")
def start_app(app_name: str):
    """Create a new fastapi component, similar to django startapp"""
    package_name = app_name.lower().strip().replace(" ", "_").replace("-", "_")
    app_dir = settings.BASE_DIR / package_name
    base_for_models = "from beanie import Document\n"
    base_for_models += "from pydantic import BaseModel\n"
    base_for_models += "from fast_backend.app.models.base import BaseDocument"
    files = {
        "__init__.py": "",
        # suggested by gemini
        "models.py": base_for_models,
        "schemas.py": "from pydantic import BaseModel",
        "routes.py": f"from fastapi import APIRouter\n\nrouter = APIRouter(prefix='/{package_name}')",
        "tests/__init__.py": "",
        "tests/factories.py": "from factory import Factory, Faker",
    }
    app_dir.mkdir()
    (app_dir / "tests").mkdir()
    for file, content in files.items():
        with open(app_dir / file, "w") as f:
            f.write(content)
    typer.secho(f"App {package_name} created", fg=typer.colors.GREEN)


@cli.command()
def shell():
    """Opens an interactive shell with objects auto imported"""
    try:
        from IPython import start_ipython
        from traitlets.config import Config
    except ImportError:
        typer.secho(
            "Install iPython using `poetry add ipython` to use this feature.",
            fg=typer.colors.RED,
        )
        raise typer.Exit()

    def teardown_shell():
        import asyncio

        typer.secho("Closing MongoDB client...", fg=typer.colors.YELLOW)
        # why is this empty

    async def _shell_init_beanie():
        await _init_mongodb_beanie()
        typer.secho("MongoDB and Beanie initialized for shell.", fg=typer.colors.GREEN)

    model_imports = [
        f"from {model.__module__} import {model.__name__}" for model in BEANIEDB_MODELS
    ]
    auto_imports = [
        "from beanie import Document, Link, PydanticObjectId, init_beanie, AsyncIOMotorClient",
        "from motor.motor_asyncio import AsyncIOMotorClient",
        f"MONGO_DB_URL = '{MONGO_DB_URL}'",
        f"DB_NAME = '{DB_NAME}'",
    ] + model_imports
    shell_setup = [
        "import asyncio",
        "import atexit",
        "_ = atexit.register(teardown_shell)",
        "asyncio.run(_shell_init_beanie())",
    ]
    typer.secho("Auto Imports\n" + "\n".join(auto_imports), fg=typer.colors.GREEN)
    c = Config()
    c.InteractiveShell.autoawait = True
    c.InteractiveShellApp.exec_lines = auto_imports + shell_setup
    start_ipython(
        argv=[],
        user_ns={
            "teardown_shell": teardown_shell,
            "_shell_init_beanie": _shell_init_beanie,
        },
        config=c,
    )


@cli.command("run-worker")
def run_worker(reload: bool = typer.Option(True)):
    """Run the saq worker process"""
    if reload:
        subprocess.run(["hupper", "-m", "saq", "app.worker.settings", "--web"])
    else:
        subprocess.run(["python", "-m", "saq", "app.worker.settings", "--web"])


@cli.command(help="run-mailserver")
def run_mailserver(hostname: str = "localhost", port: int = 1025):
    """Run a test smtp server, for development purposes only, for a more robust option try MailHog"""
    from aiosmtpd.controller import Controller
    from aiosmtpd.handlers import Debugging

    typer.secho(f"Now accepting mail at {hostname}:{port}", fg=typer.colors.GREEN)
    controller = Controller(Debugging(), hostname=hostname, port=port)
    controller.start()
    while True:
        pass


@cli.command("secret-key")
def secret_key():
    """Generate a secret key for your application"""
    typer.secho(f"{secrets.token_urlsafe(64)}", fg=typer.colors.GREEN)


@cli.command()
def info():
    """Show project health and settings."""
    with httpx.Client(base_url=settings.SERVER_HOST) as client:
        try:
            resp = client.get("/health", follow_redirects=True)
        except httpx.ConnectError:
            app_health = typer.style(
                "❌ API is not responding", fg=typer.colors.RED, bold=True
            )
        else:
            app_health = "\n".join(
                [f"{key.upper()}={value}" for key, value in resp.json().items()]
            )

    envs = "\n".join([f"{key}={value}" for key, value in settings.dict().items()])
    title = typer.style("===> APP INFO <==============\n", fg=typer.colors.BLUE)
    typer.secho(title + app_health + "\n" + envs)


if __name__ == "__main__":
    cli()
