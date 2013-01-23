import os

os.environ['DJANGO_SETTINGS_MODULE'] = "webroot.settings"

import unittest
from webroot.game import Game


class TestGame(unittest.TestCase):

    def black_card_factory(self, cards):
        def next_card():
            return cards.pop(0)
        return next_card

    def get_mocked_game(self, num_players, *black_cards):
        wamp_server = MockWampServer()
        game = Game(0, lambda a: None)
        game._start_round_timer = lambda a: None
        game.register_cah_wamp_client(wamp_server)
        game._get_black_card = self.black_card_factory(*black_cards)

        for x in range(0, num_players):
            game.add_user(str(x), MockSession(str(x)))
        game.start_game()
        return game, wamp_server

    def get_hands(self, wamp_server):
        white_cards = {}
        for topic, data, exclude, eligible in wamp_server.messages:
            if topic.endswith("send_hand"):
                white_cards[eligible[0].session_id] = data['white_cards']
        return white_cards

    def test_draw2_black(self):
        num_players = 3
        game, wamp_server = self.get_mocked_game(num_players,
            [{"card_id": 1, "text": "{}{}{}", "tag": "test", "num_white_cards": 3}])
        white_cards = self.get_hands(wamp_server)
        self.assertEqual(12 * num_players, sum([len(x) for x in white_cards.itervalues()]))


    def test_draw0_black(self):
        num_players = 3
        game, wamp_server = self.get_mocked_game(num_players,
            [{"card_id": 1, "text": "{}{}", "tag": "test", "num_white_cards": 2}])
        white_cards = self.get_hands(wamp_server)
        self.assertEqual(10 * num_players, sum([len(x) for x in white_cards.itervalues()]))


class MockWampServer(object):
    def __init__(self):
        self.messages = []

    def dispatch(self, topic, data, exclude=None, eligible=None):
        self.messages.append((topic, data, exclude, eligible));


class MockSession(object):
    def __init__(self, session_id):
        self.session_id = session_id