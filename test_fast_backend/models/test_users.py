import pytest
from beanie import PydanticObjectId, Link
from datetime import datetime
from pymongo.errors import DuplicateKeyError
from pydantic import ValidationError

from fast_backend.app.models import User, UserLink
from fast_backend.app.schemas import UserListItem


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserModelCreate:
    async def test_create_user_success(self, data):
        user_data = data.user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password="hashed_" + user_data["password"],
            created_at=datetime.now(),
        )
        await user.insert()
        assert isinstance(user.id, PydanticObjectId)
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.hashed_password.startswith("hashed_")
        assert isinstance(user.created_at, datetime)
        assert user.updated_at is None

        db_user = await User.get(user.id)
        assert db_user is not None
        assert isinstance(db_user.id, PydanticObjectId)
        assert db_user.username == user_data["username"]
        assert db_user.email == user_data["email"]
        assert db_user.hashed_password.startswith("hashed_")
        assert isinstance(db_user.created_at, datetime)
        assert db_user.updated_at is None

    async def test_create_user_duplicate_username_fails(self, data):
        user_data1 = data.user
        user_data2 = data.user
        user1 = User(
            username=user_data1["username"],
            email=user_data1["email"],
            hashed_password="hashed_" + user_data1["password"],
            created_at=datetime.now(),
        )
        await user1.insert()
        user2 = User(
            username=user_data1["username"],  # duplicate username
            email=user_data2["email"],
            hashed_password="hashed_" + user_data2["password"],
            created_at=datetime.now(),
        )
        with pytest.raises(DuplicateKeyError) as e:
            await user2.insert()
        assert "dup key" in str(e.value)
        assert "username" in str(e.value)

    async def test_create_user_duplicate_email_fails(self, data):
        user_data1 = data.user
        user_data2 = data.user
        user1 = User(
            username=user_data1["username"],
            email=user_data1["email"],
            hashed_password="hashed_" + user_data1["password"],
            created_at=datetime.now(),
        )
        await user1.insert()
        user2 = User(
            username=user_data2["username"],
            email=user_data1["email"],  # duplicate email
            hashed_password="hashed_" + user_data2["password"],
            created_at=datetime.now(),
        )
        with pytest.raises(DuplicateKeyError) as e:
            await user2.insert()

        assert "dup key" in str(e.value)
        assert "email" in str(e.value)

    async def test_create_user_missing_fields(self, data):
        user_data = data.user
        user_data["hashed_password"] = "hashed_" + user_data["password"]
        user_data["created_at"] = datetime.now()
        for key in ["username", "email", "hashed_password"]:
            bad_data = user_data.copy()
            del bad_data[key]
            with pytest.raises(ValueError) as e:
                user = User(**bad_data)
                await user.insert()
            assert key in str(e.value)


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserModelRead:
    async def test_read_existing_user(self, data):
        user_data = data.user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password="hashed_" + user_data["password"],
            created_at=datetime.now(),
        )
        await user.insert()
        found = await User.get(user.id)
        assert found is not None
        assert found.username == user_data["username"]
        assert found.email == user_data["email"]

    async def test_read_nonexistent_user(self):
        id = PydanticObjectId()
        found = await User.get(id)
        assert found is None

    async def test_read_all_users(self, data):
        users = []
        for _ in range(3):
            user_data = data.user
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password="hashed_" + user_data["password"],
                created_at=datetime.now(),
            )
            await user.insert()
            users.append(user)
        all_users = await User.find_all().to_list()
        assert len(all_users) >= 3
        usernames = [u.username for u in all_users]
        for user in users:
            assert user.username in usernames


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserModelUpdate:
    async def test_update_username(self, data):
        user_data = data.user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password="hashed_" + user_data["password"],
            created_at=datetime.now(),
        )
        await user.insert()
        user.username = "new_username"
        await user.save()
        updated = await User.get(user.id)
        assert updated is not None
        assert updated.username == "new_username"

    async def test_update_email(self, data):
        user_data = data.user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password="hashed_" + user_data["password"],
            created_at=datetime.now(),
        )
        await user.insert()
        user.email = "new_email@example.com"
        await user.save()
        updated = await User.get(user.id)
        assert updated is not None
        assert updated.email == "new_email@example.com"


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserModelDelete:
    async def test_delete_user(self, data):
        user_data = data.user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password="hashed_" + user_data["password"],
            created_at=datetime.now(),
        )
        await user.insert()
        await user.delete()
        deleted = await User.get(user.id)
        assert deleted is None


@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
@pytest.mark.asyncio
class TestUserLinkModel:
    async def test_userlink_creation(self, data):
        user_data = data.user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password="hashed_" + user_data["password"],
            created_at=datetime.now(),
        )
        await user.insert()
        user_link = user.to_link()
        assert isinstance(user_link, UserLink)
        assert user_link.username == user.username
        assert user_link.id == user.id
        assert hasattr(user_link, "link")
        assert isinstance(user_link.link, Link)


    async def test_userlink_to_list_item(self, data):
        user_data = data.user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password="hashed_" + user_data["password"],
            created_at=datetime.now(),
        )
        await user.insert()
        user_link = user.to_link()
        list_item = user_link.to_list_item()
        assert isinstance(list_item, UserListItem)
        assert list_item.username == user.username
        assert list_item.id == user.id
        
    async def test_userlink_missing_fields_raises(self):
        data = {"id": PydanticObjectId(), "username": "sample", "link": Link}
        for key in data:
            data_copy = data.copy()
            del data_copy[key]
            with pytest.raises(ValidationError):
                UserLink(**data_copy)
