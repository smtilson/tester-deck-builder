from .base import BasicModel
from .cards import Card
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import DoesNotExist

class Deck(BasicModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    description = fields.TextField(null=True)
    is_valid = fields.BooleanField(default=False)
    owner_id = fields.IntField()
    cards = fields.ManyToManyField("models.Card", forward_key="card_id", 
                                backward_key="deck_id",
                                related_name="decks", through="deck_card")

    class Meta:
        table = "decks"


class DeckCard(BasicModel):
    id = fields.IntField(pk=True)
    deck = fields.ForeignKeyField("models.Deck", related_name="deck_cards")
    card = fields.ForeignKeyField("models.Card", related_name="card_decks")
    quantity = fields.IntField(default=1)

    class Meta:
        table = "deck_card"
        unique_together = (("deck", "card"),)
        