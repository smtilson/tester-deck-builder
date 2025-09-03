from datetime import datetime
from typing import Optional, ClassVar, Type, TypeVar, Generic

from pydantic import Field, BaseModel
from beanie import Document, PydanticObjectId, Link


T = TypeVar("T", bound=BaseModel)


class LinkHelper(Generic[T]):
    def __init__(self, link_class: Type[T]):
        self.link_class = link_class

    def to_link(self, instance) -> T:
        if instance.id is None:
            raise ValueError("Cannot create link for unsaved document")
        if self.link_class is None:
            raise NotImplementedError(
                f"Link class is not set yet for {instance.__class__.__name__}"
            )
        return self.link_class.from_instance(instance)


class BaseDocument(Document):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Settings:
        is_root = False
        use_state_management = True
