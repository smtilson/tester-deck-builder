import pytest
from beanie import Link, PydanticObjectId
from pydantic import BaseModel
from typing import ClassVar

from fast_backend.app.models import MinLink, LinkHelper


# DummyLink class
class DummyLink(MinLink):
    link: Link["DummyModel"]
    id: PydanticObjectId
    name: str = "dummy"
    # list_item_class intentionally not set

    @classmethod
    def from_instance(cls, instance):
        return cls(
            link=Link[type(instance)](instance.id, type(instance)),
            id=instance.id,
            name=instance.name,
        )


# DummyModel class (Pydantic, not Beanie Document)
class DummyModel(BaseModel):
    name: str = "dummy"
    link_helper: ClassVar[LinkHelper] = LinkHelper(DummyLink)
    id: PydanticObjectId = PydanticObjectId()

    def to_link(self) -> DummyLink:
        return self.link_helper.to_link(self)


# DummyDoc for testing missing link_class
class DummyDoc(BaseModel):
    link_helper: ClassVar[LinkHelper] = LinkHelper(None)
    id: PydanticObjectId = PydanticObjectId()

@pytest.mark.skip("standard")
@pytest.mark.usefixtures("init_db", "cleanup_db")
class TestMinLinkBehavior:
    def test_minlink_to_list_item_not_implemented(self):
        dummy_model = DummyModel(name="dummy")
        dummy_link = dummy_model.to_link()
        with pytest.raises(NotImplementedError):
            dummy_link.to_list_item()

    def test_linkhelper_link_class_none(self):
        dummy_doc = DummyDoc()
        with pytest.raises(NotImplementedError):
            dummy_doc.link_helper.to_link(dummy_doc)
