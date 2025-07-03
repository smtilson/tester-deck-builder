from tortoise import fields
from tortoise.exceptions import DoesNotExist
from .base import BasicModel

class Card(BasicModel):
    id=fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    text = fields.TestField(null=True)
    # more to come
    
    class Meta:
        table = "cards"