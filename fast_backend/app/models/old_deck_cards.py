from .old_base import BasicModel
from tortoise import fields


class DeckCard(BasicModel):
    id = fields.IntField(primary_key=True)
    deck: fields.ForeignKeyRelation["Deck"] = fields.ForeignKeyField(
        "models.Deck", related_name="deck_cards", on_delete=fields.CASCADE
    )
    card: fields.ForeignKeyRelation["Card"] = fields.ForeignKeyField(
        "models.Card", related_name="deck_cards", on_delete=fields.CASCADE
    )
    quantity = fields.IntField(default=1)

    class Meta:
        table = "deck_cards"
        unique_together = (("deck", "card"),)
