import pytest

from test_fast_backend.sample_data import all_test_data

@pytest.mark.skip
class TestSampleData:
    def test_pick_random_user_returns_unique(self, all_test_data):
        picked = set()
        for _ in range(len(all_test_data.user_data)):
            user = all_test_data.user
            assert user["username"] not in picked
            picked.add(user["username"])
    # Should raise ValueError when all are picked
        with pytest.raises(ValueError):
            all_test_data.user

    def test_pick_random_card_returns_unique(self, all_test_data):
        picked = set()
        for _ in range(len(all_test_data.card_data)):
            card = all_test_data.card
            assert card["name"] not in picked
            picked.add(card["name"])
        with pytest.raises(ValueError):
            all_test_data.card

    def test_pick_random_game_returns_unique(self,all_test_data):
        picked = set()
        for _ in range(len(all_test_data.game_data)):
            game = all_test_data.game
            assert game["name"] not in picked
            picked.add(game["name"])
        with pytest.raises(ValueError):
            all_test_data.game

    def test_pick_random_deck_returns_unique(self, all_test_data):
        picked = set()
        for _ in range(len(all_test_data.deck_data)):
            deck = all_test_data.deck
            assert deck["name"] not in picked
            picked.add(deck["name"])
        with pytest.raises(ValueError):
            all_test_data.deck