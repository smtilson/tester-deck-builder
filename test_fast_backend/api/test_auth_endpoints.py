from beanie import PydanticObjectId
import pytest
from fast_backend.app.models.users import User

@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestRegistration:
    async def test_register_success(self, client):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == payload["username"]
        assert data["email"] == payload["email"]
        assert isinstance(data['id'], PydanticObjectId)

        # Query the database for the user

        user = await User.find_one({"id": data["id"]})
        assert user is not None
        assert user.username == payload["username"]
        assert user.email == payload["email"]
        assert user.is_staff is False
        assert user.name is None
        assert user.created_at is not None
        assert user.updated_at is None
        assert user.playtesting == []
        assert user.designing == []
        assert user.developing == []

        # Check response fields
        expected_fields = [
            "id", "username", "email", "is_staff", "name",
            "playtesting", "designing", "developing", "created_at", "updated_at"
        ]
        for field in expected_fields:
            assert field in data


    async def test_register_duplicate_email(self, client):
        payload = {
            "username": "userdup",
            "email": "userdup@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        response1 = await client.post("/auth/register", json=payload)
        assert response1.status_code == 201

        payload["username"] = "userdup2"
        response2 = await client.post("/auth/register", json=payload)
        assert response2.status_code in (400, 409)


    async def test_register_duplicate_username(self, client):
        payload = {
            "username": "dupeuser",
            "email": "dupeuser1@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        response1 = await client.post("/auth/register", json=payload)
        assert response1.status_code == 201

        payload["email"] = "dupeuser2@example.com"
        response2 = await client.post("/auth/register", json=payload)
        assert response2.status_code in (400, 409)
        

    async def test_register_passwords_do_not_match(self, client):
        payload = {
            "username": "nomatchuser",
            "email": "nomatchuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "wrongpassword"
        }
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 400
        

    async def test_register_invalid_email(self, client):
        payload = {
            "username": "bademailuser",
            "email": "not-an-email",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 422  # FastAPI validation error
        print(payload)
        print(response.json())

    async def test_register_empty_fields(self, client):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        for key in payload.keys():
            new_payload = {k:v for k,v in payload.items()}
            new_payload[key] = ""
            response = await client.post("/auth/register", json=new_payload)
            assert response.status_code in (400, 422)
        

@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client):
        payload = {
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        reg_response = await client.post("/auth/register", json=payload)
        assert reg_response.status_code == 201

        login_payload = {
            "username": "loginuser@example.com",
            "password": "strongpassword123"
        }
        response = await client.post("/auth/jwt/login", data=login_payload)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_login_wrong_password(self, client):
        payload = {
            "username": "wrongpwuser",
            "email": "wrongpwuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        reg_response = await client.post("/auth/register", json=payload)
        assert reg_response.status_code == 201

        login_payload = {
            "username": "wrongpwuser@example.com",
            "password": "incorrectpassword"
        }
        response = await client.post("/auth/jwt/login", data=login_payload)
        assert response.status_code == 400

@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestPasswordReset:
    async def test_reset_password_request(self, client):
        payload = {
            "username": "resetpwuser",
            "email": "resetpwuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        reg_response = await client.post("/auth/register", json=payload)
        assert reg_response.status_code == 201

        reset_payload = {"email": "resetpwuser@example.com"}
        response = await client.post("/auth/forgot-password", json=reset_payload)
        assert response.status_code == 202

@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestVerification:
    async def test_verify_request(self, client):
        payload = {
            "username": "verifyuser",
            "email": "verifyuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        reg_response = await client.post("/auth/register", json=payload)
        assert reg_response.status_code == 201

        token = "testtoken"
        response = await client.get(f"/auth/verify-email?token={token}")
        assert response.status_code == 200
        data = response.json()
        assert data["msg"] == "Email verified successfully"

    async def test_resend_verification_email(self, client):
        payload = {
            "username": "resenduser",
            "email": "resenduser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        reg_response = await client.post("/auth/register", json=payload)
        assert reg_response.status_code == 201

        resend_payload = {"email": "resenduser@example.com"}
        response = await client.post("/auth/resend-verification", json=resend_payload)
        assert response.status_code == 202
        assert True

@pytest.mark.skip("standard")
@pytest.mark.asyncio
class TestUserUpdateDelete:
    async def test_update_user(self, client):
        payload = {
            "username": "updateuser",
            "email": "updateuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        reg_response = await client.post("/auth/register", json=payload)
        assert reg_response.status_code == 201

        login_payload = {
            "username": "updateuser@example.com",
            "password": "strongpassword123"
        }
        login_response = await client.post("/auth/jwt/login", data=login_payload)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        update_payload = {
            "username": "updateduser",
            "email": "updateduser@example.com"
        }
        response = await client.put("/auth/users/me", json=update_payload, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == update_payload["username"]
        assert data["email"] == update_payload["email"]

    async def test_delete_user(self, client):
        payload = {
            "username": "deleteuser",
            "email": "deleteuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123"
        }
        reg_response = await client.post("/auth/register", json=payload)
        assert reg_response.status_code == 201

        login_payload = {
            "username": "deleteuser@example.com",
            "password": "strongpassword123"
        }
        login_response = await client.post("/auth/jwt/login", data=login_payload)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        response = await client.delete("/auth/users/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204

        login_response = await client.post("/auth/jwt/login", data=login_payload)
        assert login_response.status_code == 400