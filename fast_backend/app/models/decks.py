from .base import BasicModel
from tortoise import fields

class Deck(BasicModel):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, unique=True)
    description = fields.TextField(null=True)
    is_valid = fields.BooleanField(default=False)
    owner_id = fields.IntField()
    deck_cards: fields.ReverseRelation["DeckCard"]
    
    class Meta:
        table = "decks"

