from fastapi import Request
from fastapi.responses import JSONResponse
from fast_backend.app.exceptions.users import ValidationError



async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors},
    )