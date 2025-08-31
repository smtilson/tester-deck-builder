import pytest
from httpx import AsyncClient
from fast_backend.app.main import app

BASE_URL = "http://127.0.0.1:8000"
@pytest.mark.skip("standard")
@pytest.mark.asyncio
async def test_test_route():
    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        response = await ac.get("/test/")
        assert response.status_code == 200
        assert response.json()["message"] == "Test route"

@pytest.mark.skip("standard")
@pytest.mark.asyncio
async def test_db_connection(init_db):
    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        response = await ac.get("/test/db-connection")
        assert response.status_code == 200
        assert "Database connection is working" in response.json()["message"]
