from pydantic.v1.utils import import_string
from saq import Queue

from fast_backend.app.core.config_app import settings

BACKGROUND_FUNCTIONS = [
    "fast_backend.app.services.tasks.log_user_email",
    "fast_backend.app.services.email.send_email_task",
]
FUNCTIONS = [import_string(bg_func) for bg_func in BACKGROUND_FUNCTIONS]


async def startup(_: dict):
    """
    Binds a connection set to the db object.
    """
    #await Tortoise.init(config=TORTOISE_ORM)
    return

async def shutdown(_: dict):
    """
    Pops the bind on the db object.
    """
    #await Tortoise.close_connections()
    return

DUMMY_REDIS_URL = "redis://localhost:6380/0"
queue = Queue.from_url(DUMMY_REDIS_URL)

settings = {
    "queue": queue,
    "functions": FUNCTIONS,
    "concurrency": 10,
    "startup": startup,
    "shutdown": shutdown,
}
