import pytest_asyncio
import pytest
import random


@pytest_asyncio.fixture(scope="function")
async def setup(init_db, managers, data):
    class Setup:
        def __init__(self):
            self._users = None
            self._games = None
            self._cards = None
            self._decks = None

        async def users(self):
            if self._users is None:
                self._users = []
                for user_data in data.users:
                    user = await managers.user.create_from_dict(user_data)
                    self._users.append(user)
            return self._users

        async def games(self):
            if self._games is None:
                users = await self.users()
                self._games = []
                for game_data in data.games:
                    num1 = random.randint(1, len(users))
                    num2 = random.randint(1, len(users))
                    designer_ids = list({user.id for user in random.sample(users, num1)})
                    developer_ids = list({user.id for user in random.sample(users, num2)})
                    game_data["designer_ids"] = designer_ids
                    game_data["developer_ids"] = developer_ids
                    created_game = await managers.game.create_from_dict(game_data)
                    self._games.append(created_game)
            return self._games

        async def decks(self):
            if self._decks is None:
                users = await self.users()
                games = await self.games()
                self._decks = []
                for deck_data in data.decks:
                    deck_data["owner_id"] = random.choice(users).id
                    deck_data["game_id"] = random.choice(games).id
                    created_deck = await managers.deck.create_from_dict(deck_data)
                    self._decks.append(created_deck)
            return self._decks

        async def cards(self):
            if self._cards is None:
                games = await self.games()
                self._cards = []
                for card_data in data.cards:
                    card_data["game_id"] = random.choice(games).id
                    created_card = await managers.card.create_from_dict(card_data)
                    self._cards.append(created_card)
            return self._cards

        async def _pick_random(self, data_list):
            try:
                return data_list.pop()
            except IndexError:
                raise ValueError("All items have been picked.")

        @property
        async def card(self):
            if self._cards is None:
                await self.cards()
            return await self._pick_random(self._cards)

        @property
        async def deck(self):
            if self._decks is None:
                await self.decks()
            return await self._pick_random(self._decks)

        @property
        async def user(self):
            if self._users is None:
                await self.users()
            return await self._pick_random(self._users)

        @property
        async def game(self):
            if self._games is None:
                await self.games()
            return await self._pick_random(self._games)

        async def begin(self):
            await self.users()
            await self.games()
            await self.cards()
            await self.decks()

        async def clean_up(self):
            self._users = []
            self._games = []
            self._decks = []
            self._cards = []
            await managers.deck.delete_all()
            await managers.game.delete_all()
            await managers.card.delete_all()
            await managers.user.delete_all()

    setup_instance = Setup()
    await setup_instance.begin()
    yield setup_instance
    await setup_instance.clean_up()