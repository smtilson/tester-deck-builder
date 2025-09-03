from beanie import PydanticObjectId
import pytest
from fastapi_users.password import PasswordHelper

from fast_backend.app.models import User
from fast_backend.app.auth.manager import UserManager


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestRegistration:
    async def test_register_success(self, client):
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123",
        }
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == payload["username"]
        assert data["email"] == payload["email"]
        assert isinstance(data["id"], str)
        assert data["id"]
        print(data)
        # Query the database for the user

        user = await User.get(data["id"])
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
            "id",
            "username",
            "email",
            "is_staff",
            "name",
            "playtesting",
            "designing",
            "developing",
            "created_at",
            "updated_at",
        ]
        for field in expected_fields:
            assert field in data

    async def test_register_duplicate_email(self, client):
        payload = {
            "username": "userdup",
            "email": "userdup@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123",
        }
        response1 = await client.post("/auth/register", json=payload)
        assert response1.status_code == 201

        payload["username"] = "userdup2"
        response2 = await client.post("/auth/register", json=payload)
        assert response2.status_code in (400, 422)

    async def test_register_duplicate_username(self, client):
        payload = {
            "username": "dupeuser",
            "email": "dupeuser1@example.com",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123",
        }
        response1 = await client.post("/auth/register", json=payload)
        assert response1.status_code == 201

        payload["email"] = "dupeuser2@example.com"
        response2 = await client.post("/auth/register", json=payload)
        assert response2.status_code in (400, 422)

    async def test_register_passwords_do_not_match(self, client):
        payload = {
            "username": "nomatchuser",
            "email": "nomatchuser@example.com",
            "password": "strongpassword123",
            "confirm_password": "wrongpassword",
        }
        response = await client.post("/auth/register", json=payload)
        assert response.status_code == 422

    async def test_register_invalid_email(self, client):
        payload = {
            "username": "bademailuser",
            "email": "not-an-email",
            "password": "strongpassword123",
            "confirm_password": "strongpassword123",
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
            "confirm_password": "strongpassword123",
        }
        for key in payload.keys():
            new_payload = {k: v for k, v in payload.items()}
            new_payload[key] = ""
            response = await client.post("/auth/register", json=new_payload)
            assert response.status_code in (400, 422)


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestLogin:
    async def test_login_fails_for_unverified_user(self, client, unverified_user):
        login_payload = {"username": unverified_user.email, "password": "strongpassword123"}
        response = await client.post("/auth/jwt/login", data=login_payload)
        print("Unverified login response:", response.json())
        assert response.status_code == 400
        assert response.json().get("detail") == "LOGIN_USER_NOT_VERIFIED"
        assert "access_token" not in response.json()
        assert "refresh_token" not in response.json()

    async def test_login_success_for_verified_user(self, client, verified_user):
        login_payload = {"username": verified_user.email, "password": "strongpassword123"}
        response = await client.post("/auth/jwt/login", data=login_payload)
        print("Verified login response:", response.json())
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert isinstance(data["access_token"], str)
        # If your setup uses refresh tokens, check for it too:
        if "refresh_token" in data:
            assert isinstance(data["refresh_token"], str)

    async def test_login_wrong_password(self, client, verified_user):
        login_payload = {
            "username": verified_user.email,
            "password": "incorrectpassword",
        }
        response = await client.post("/auth/jwt/login", data=login_payload)
        assert response.status_code == 400
        assert "access_token" not in response.json()
        assert "refresh_token" not in response.json()

    async def test_login_fails_for_nonexistent_user(self, client):
        """Test that login fails for a user not in the database."""
        login_payload = {"username": "notindb@example.com", "password": "doesnotmatter"}
        response = await client.post("/auth/jwt/login", data=login_payload)
        print("Nonexistent user login response:", response.json())
        assert response.status_code == 400
        assert "access_token" not in response.json()
        assert "refresh_token" not in response.json()

    async def test_login_fails_for_invalid_email_format(self, client):
        login_payload = {"username": "not-an-email", "password": "doesnotmatter"}
        response = await client.post("/auth/jwt/login", data=login_payload)
        assert response.status_code == 400
        assert "access_token" not in response.json()
        assert "refresh_token" not in response.json()

    async def test_login_fails_for_empty_password(self, client, verified_user):
        login_payload = {"username": verified_user.email, "password": ""}
        response = await client.post("/auth/jwt/login", data=login_payload)
        assert response.status_code == 400
        assert "access_token" not in response.json()
        assert "refresh_token" not in response.json()

    @pytest.mark.skip("not yet implemented")
    async def test_login_case_sensitivity(self, client, verified_user):
        login_payload = {
            "username": verified_user.email.upper(),  # Different case
            "password": "strongpassword123",
        }
        response = await client.post("/auth/jwt/login", data=login_payload)
        #print("Case sensitivity login response:", response.json())
        assert response.status_code == 200
        #raise NotImplementedError("Case sensitivity test not implemented")
        # Depending on your system, this may succeed or fail


@pytest.mark.skip("standard")
@pytest.mark.asyncio
@pytest.mark.usefixtures("init_db")
class TestPasswordReset:
    async def test_password_reset_flow(self, client, verified_user, monkeypatch):
        # Step 1: Check password in DB
        db_user = await User.get(verified_user.id)
        assert db_user is not None
        verified, _ = PasswordHelper().verify_and_update(
            verified_user._password, db_user.hashed_password
        )
        assert verified is True

        # Step 2: Monkeypatch the callback to capture the token
        captured = {}

        async def capture_token(self, user, token, request):
            captured["token"] = token

        
        monkeypatch.setattr(UserManager, "on_after_forgot_password", capture_token)

        # Step 3: Send password reset request
        reset_payload = {"email": verified_user.email}
        response = await client.post("/auth/forgot-password", json=reset_payload)
        assert response.status_code == 202

        # Step 4: Use the captured token to reset the password
        token = captured.get("token")
        assert token is not None

        new_password = "newpassword456"
        reset_confirm_payload = {
            "token": token,
            "password": new_password,
            #"confirm_password": new_password,
        }
        response = await client.post("/auth/reset-password", json=reset_confirm_payload)
        assert response.status_code == 200

        # Step 5: Check password was changed in DB
        db_user = await User.get(verified_user.id)
        assert db_user is not None
        verified, _ = PasswordHelper().verify_and_update(
            new_password, db_user.hashed_password
        )
        assert verified is True

    async def test_password_reset_nonexistent_email(self, client):
        """Should accept request but not send a token for nonexistent email."""
        reset_payload = {"email": "doesnotexist@example.com"}
        response = await client.post("/auth/forgot-password", json=reset_payload)
        assert response.status_code == 202

    async def test_password_reset_inactive_user(self, client, inactive_user):
        """Should not send a token or allow reset for inactive user."""
        reset_payload = {"email": inactive_user.email}
        response = await client.post("/auth/forgot-password", json=reset_payload)
        # Depending on your implementation, this may be 202 or an error
        assert response.status_code in (202, 400, 403)

    async def test_password_reset_unverified_user(self, client, unverified_user):
        """Should handle reset for unverified user according to policy."""
        reset_payload = {"email": unverified_user.email}
        response = await client.post("/auth/forgot-password", json=reset_payload)
        assert response.status_code == 202

    async def test_password_reset_invalid_token(self, client, verified_user):
        """Should not reset password with an invalid token."""
        reset_confirm_payload = {
            "token": "invalidtoken",
            "password": "newpassword456",
        }
        response = await client.post("/auth/reset-password", json=reset_confirm_payload)
        assert response.status_code in (400, 403)
    
    @pytest.mark.skip("not yet implemented")
    async def test_password_reset_password_policy(
        self, client, verified_user, monkeypatch
    ):
        """Should fail if new password does not meet requirements."""
        raise NotImplementedError("Password policy test not implemented")
        captured = {}

        async def capture_token(self, user, token, request):
            captured["token"] = token

        from fast_backend.app.auth.manager import UserManager
        monkeypatch.setattr(UserManager, "on_after_forgot_password", capture_token)

        reset_payload = {"email": verified_user.email}
        response = await client.post("/auth/forgot-password", json=reset_payload)
        assert response.status_code == 202

        token = captured.get("token")
        assert token is not None

        # Too short password
        reset_confirm_payload = {
            "token": token,
            "password": "123",
            #"confirm_password": "123",
        }
        response = await client.post("/auth/reset-password", json=reset_confirm_payload)
        assert response.status_code in (400, 422)

    async def test_password_reset_token_reuse(
        self, client, verified_user, monkeypatch
    ):
        """Should not allow the same token to be used twice."""
        captured = {}

        async def capture_token(self, user, token, request):
            captured["token"] = token

        monkeypatch.setattr(UserManager, "on_after_forgot_password", capture_token)

        reset_payload = {"email": verified_user.email}
        response = await client.post("/auth/forgot-password", json=reset_payload)
        assert response.status_code == 202

        token = captured.get("token")
        assert token is not None

        reset_confirm_payload = {
            "token": token,
            "password": "newpassword456",
            #"confirm_password": "newpassword456",
        }
        response = await client.post("/auth/reset-password", json=reset_confirm_payload)
        assert response.status_code == 200

        # Try to reuse the token
        response = await client.post("/auth/reset-password", json=reset_confirm_payload)
        assert response.status_code


