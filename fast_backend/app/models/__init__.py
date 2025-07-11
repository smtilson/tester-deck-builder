from .decks import Deck
from .cards import Card
from .deck_cards import DeckCard
#from .users import User

# You can optionally define the many-to-many through table explicitly here if needed,
# though Tortoise handles it automatically when you define ManyToManyField.
# from tortoise import fields, models
# class DeckCard(models.Model):
#     deck: fields.ForeignKeyRelation[Deck] = fields.ForeignKeyField('models.Deck', on_delete=fields.CASCADE)
#     card: fields.ForeignKeyRelation[Card] = fields.ForeignKeyField('models.Card', on_delete=fields.CASCADE)
#     class Meta:
#         table = "deck_card"
#         unique_together = (("deck", "card"),)