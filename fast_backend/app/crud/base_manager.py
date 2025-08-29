from typing import Optional, TypeVar, Type, Generic
from beanie.odm.fields import PydanticObjectId
from beanie import Document
from datetime import datetime
from pydantic import BaseModel

from fast_backend.app.models import Card as CardModel
from fast_backend.app.schemas import CardCreate, CardUpdate, CardResponse
from fast_backend.app.core.exceptions import NotFoundException


# Define generic types for our models and schemas
DocType = TypeVar("DocType", bound=Document)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)
ListItemSchemaType = TypeVar("ListItemSchemaType", bound=BaseModel)



class BaseManager(Generic[DocType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType, ListItemSchemaType]):
    def __init__(self, doc_model: Type[DocType], response_schema: Type[ResponseSchemaType], list_item_schema: Type[ListItemSchemaType]):
        self.doc_model = doc_model
        self.response_schema = response_schema
        self.list_item_schema = list_item_schema

    async def create_from_dict(self, item_data: dict) -> DocType:
        """
            Create an item from a dictionary.
        Args:
            item_data: The item data from the request

        Returns:
            The created item as a Pydantic schema instance.
        """
        db_obj = self.doc_model(**item_data)
        await db_obj.insert()
        return db_obj
    
    async def create(self, item_in: CreateSchemaType) -> ResponseSchemaType:
        """
            Create an item.
        Args:
            item_data: The item data from the request

        Returns:
            The created item as a Pydantic schema instance.
        """
        db_obj = await self.create_from_dict(item_in.model_dump())
        if db_obj.id:
            return await self.get(db_obj.id)
        raise Exception(f"There was an error when attempting to create "
                        f"{self.doc_model.__name__} based on {item_in}.")

    def present(self, db_obj:DocType) -> ResponseSchemaType:
        return self.response_schema.model_validate(db_obj)

    async def get_model(self, item_id: PydanticObjectId) -> DocType:
        """
        Get an item by its ID.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            The item as a Pydantic schema, or None if it doesn't exist.
        """
        item = await self.doc_model.get(item_id)
        if not item:
            raise NotFoundException(f"No {self.doc_model.__name__} with ID {item_id} was found.")
        return item

    async def get_list_item(self, item_id: PydanticObjectId) -> Optional[ListItemSchemaType]:
        """
        Get a list item by its ID.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            The item as a Pydantic schema, or None if it doesn't exist.
        """
        item = await self.get_model(item_id)
        return self.list_item_schema.model_validate(item)

    async def _get_by_key(self, key: str, value: str) -> ResponseSchemaType:
        item = await self.doc_model.find_one({key: value})
        if not item:
            raise NotFoundException(f"No {self.doc_model.__name__} found with {key}={value}")
        return self.response_schema.model_validate(item)

    async def get(self, item_id: PydanticObjectId) -> ResponseSchemaType:
        """
        Get an item by its ID.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            The item as a Pydantic schema, or None if it doesn't exist.
        """
        item = await self.get_model(item_id)
        if not item:
            raise NotFoundException(f"No {self.doc_model.__name__} was found with Id: {item_id}.")
        return self.response_schema.model_validate(item)

    async def get_all(self) -> list[ResponseSchemaType]:
        """
        Get all items.

        Returns:
            A list of all items as Pydantic schema instances.
        """
        item_objs = await self.doc_model.find_all().to_list()
        if not item_objs:
            raise NotFoundException(f"No records were found in the {self.doc_model.__name__} table.")
        return [self.response_schema.model_validate(item) for item in item_objs]

    async def update(self,
        item_id: PydanticObjectId, item_data: UpdateSchemaType
    ) -> Optional[ResponseSchemaType]:
        """
        Update an item.

        Args:
            item_id: The ID of the item to update
            item_data: The updated item data from the request

        Returns:
            The updated item as a Pydantic schema, or None if the item doesn't exist.
        """
        item_obj = await self.get_model(item_id)
        update_data = item_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now()
            await item_obj.set(update_data)
            await item_obj.save()
        return self.response_schema.model_validate(item_obj)

    async def delete(self, item_id: PydanticObjectId) -> bool:
        """
        Delete an item.

        Args:
            item_id: The ID of the item to delete

        Returns:
            True if the card was deleted, False if it doesn't exist
        """
        item_obj = await self.get_model(item_id)
        await item_obj.delete()
        return True

    async def delete_all(self) -> bool:
        await self.doc_model.find_all().delete()
        return True

    def validate_fields(self, item_data: dict) -> bool:
        """
        Validate the fields of the item data.

        Args:
            item_data: The item data to validate.

        Returns:
            True if the fields are valid, False otherwise.
        """
        # Implement your validation logic here
        raise NotImplementedError("Field validation not implemented.")
        return True

    def validate_version(self, version: str) -> bool:
        """
        Validate the version string.

        Args:
            version: The version string to validate.

        Returns:
            True if the version is valid, False otherwise.
        """
        # Implement your version validation logic here
        raise NotImplementedError("Version validation not implemented.")
    