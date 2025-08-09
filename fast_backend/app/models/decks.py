from .base import BasicModel
from tortoise import fields


class Deck(BasicModel):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255, unique=True)
    description = fields.TextField(null=True)
    is_valid = fields.BooleanField(default=False)
    owner: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="decks", to_field="id", on_delete=fields.CASCADE
    )
    deck_cards: fields.ReverseRelation["DeckCard"]

    class Meta:
        table = "decks"
