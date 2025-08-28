import pytest_asyncio
import random


@pytest_asyncio.fixture(scope="function")
async def setup(init_db, user_manager, game_manager, card_manager, deck_manager,
                user_test_data, game_test_data, card_test_data, deck_test_data):
    class Setup:
        def __init__(self):
            self._users = None
            self._games = None
            self._cards = None
            self._decks = None

        @property
        def data(self):
            class DataDict:
                def __init__(self, users, games, cards, decks):
                    self.users = users
                    self.games = games
                    self.cards = cards
                    self.decks = decks

                @property
                def user(self):
                    return random.choice(self.users)

                @property
                def game(self):
                    return random.choice(self.games)

                @property
                def card(self):
                    return random.choice(self.cards)

                @property
                def deck(self):
                    return random.choice(self.decks)

            return DataDict(user_test_data, game_test_data, card_test_data, deck_test_data)

        async def users(self):
            if self._users is None:
                self._users = []
                for user_data in user_test_data:
                    user = await user_manager.create_from_dict(user_data)
                    self._users.append(user)
            return self._users

        async def games(self):
            if self._games is None:
                users = await self.users()
                self._games = []
                for game_data in game_test_data:
                    num1 = random.randint(1, len(users))
                    num2 = random.randint(1, len(users))
                    designer_ids = list({user.id for user in random.sample(users, num1)})
                    developer_ids = list({user.id for user in random.sample(users, num2)})
                    game_data["designer_ids"] = designer_ids
                    game_data["developer_ids"] = developer_ids
                    created_game = await game_manager.create_from_dict(game_data)
                    self._games.append(created_game)
            return self._games

        async def decks(self):
            if self._decks is None:
                users = await self.users()
                games = await self.games()
                self._decks = []
                for deck_data in deck_test_data:
                    deck_data["owner_id"] = random.choice(users).id
                    deck_data["game_id"] = random.choice(games).id
                    created_deck = await deck_manager.create_from_dict(deck_data)
                    self._decks.append(created_deck)
            return self._decks

        async def cards(self):
            if self._cards is None:
                games = await self.games()
                self._cards = []
                for card_data in card_test_data:
                    card_data["game_id"] = random.choice(games).id
                    created_card = await card_manager.create_from_dict(card_data)
                    self._cards.append(created_card)
            return self._cards
        @property
        async def card(self):
            if self._cards is None:
                await self.cards()
            return random.choice(self._cards)
        @property
        async def deck(self):
            if self._decks is None:
                await self.decks()
            return random.choice(self._decks)

        @property
        async def user(self):
            if self._users is None:
                await self.users()
            return random.choice(self._users)
        @property
        async def game(self):
            if self._games is None:
                await self.games()
            return random.choice(self._games)

        async def begin(self):
            await self.users()
            await self.games()
            await self.decks()
            await self.cards()
    setup_instance = Setup()
    await setup_instance.begin()
    return setup_instance
