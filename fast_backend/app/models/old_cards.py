from tortoise import fields
from tortoise.exceptions import DoesNotExist
from .base import BasicModel


class Card(BasicModel):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    text = fields.TextField(null=True)
    # more to come
    deck_cards: fields.ReverseRelation["DeckCard"]

    class Meta:
        table = "cards"
