from contextlib import closing
import copy
from itertools import cycle
import json
import random
from threading import Timer
from webroot.db import Session
from webroot.models import Cards, CardSets

def get_card_ids(is_black_card):
    with closing(Session()) as s:
        card_ids = (
            s.query(Cards.id)
            .join(CardSets, CardSets.id == Cards.cardset)
            .filter(CardSets.active == True)
            .filter(Cards.is_black_card == is_black_card)
            .all()
            )
        return [x[0] for x in card_ids]

white_card_ids = get_card_ids(False)
black_card_ids = get_card_ids(True)
publish = "http://example.com/cahevent#{0}"

def find(seq, f):
    """Return first item in sequence where f(item) == True."""
    for item in seq:
        if f(item):
            return item


class Game(object):
    def __init__(self):
        self._state = State()
        self._users = []
        self._wamp_client = None

    def add_user(self, username, session_id):
        if self._get_user(username):
            return False

        self._users.append(User(username, session_id))
        self.sync_users()
        return True

    def remove_user(self, username):
        try:
            user = self._get_user(username)
            if not user:
                return
            if user.czar:
                try:
                    if self._state.step == "start_round":
                        self._start_round()
                    elif self._state.step == "begin_judging":
                        self._force_round_end()
                    elif self._state.step == "round_winner":
                        self._set_next_czar()
                except:
                    pass
                self._users.remove(user)
            else:
                self._users.remove(user)

            if len([u for u in self._users if not u.afk]) < 3:
                self._cancel_round_timer()
                self._state.step = "no_game"
                self.sync_me()

        except ValueError:
            pass
        self.sync_users()

    def sync_users(self):
        users = []
        black_card = self._state.black_card
        for user in self._users:
            if self._state.step == "start_round" and user.is_unplayed(
                black_card['num_white_cards']):
                user.unplayed = True
            else:
                user.unplayed = False
            users.append(user)

        self._publish("sync_users", {"users": [x.to_dict() for x in users]})

    def register_client(self, wamp_client):
        self._wamp_client = wamp_client

    def start_game(self):
        if len([u for u in self._users if not u.afk]) < 3:
            return "Can't start a game with less than 3 users"
        try:
            self._state.round_timer.cancel()
        except:
            pass
        self._state = State()
        for user in self._users:
            user.reset()
        self._start_round()

    def choose_white(self, username, card_id):
        user = self._get_user(username)
        max_whites = self._state.black_card['num_white_cards']
        whites_played = len(user.white_cards_played) + 1

        if whites_played > max_whites:
            raise "[](/flutno)"

        if whites_played == max_whites:
            self._publish("max_whites",
                eligible=[self._get_user(username).session_id])

        card = [x for x in user.hand if x['card_id'] == card_id][0]
        user.hand = [x for x in user.hand if x['card_id'] != card_id]
        user.white_cards_played.append(card)
        user.afk = False

        self.sync_users()
        self._publish("white_chosen",
            exclude=[self._get_user(username).session_id])
        self._update_round()

    def judge_group(self, username, group_id):
        czar = self._get_user(username)
        if (not czar.czar) or self._state.step != "begin_judging":
            raise '[](/abno)'

        self._cancel_round_timer()
        self._state.step = "judge_group"
        round_winner = self._get_user(session_id=group_id)
        round_winner.score += 1
        round_winner.round_winner = True

        self._state.step = "round_winner"
        self._publish("round_winner", {
            "username": round_winner.username,
            "group_id": round_winner.session_id
        })
        self._publish("chat_message", {
            "username": "Winner",
            "server": True,
            "message": ''.join([round_winner.username,
                                ' won - Black Card: ',
                                self._state.black_card['text'],
                                ' - White Card(s): ',
                                ' '.join([c['text'] for c in
                                         round_winner.white_cards_played])
            ])
        })

        if round_winner.score >= self._state.winning_score:
            self._publish("winner", round_winner.username)
            self._state.step = "no_game"
            self.sync_me()
        else:
            self.sync_users()
            self._publish('show_timer', {
                "title": "Next Round",
                "duration": 10
            })
            Timer(10, self._start_round, ()).start()

    def sync_me(self):
        self.sync_users()
        self._publish("sync_me", {
            "game_running": False if self._state.step == "no_game" else True
        })

    def update_afk(self, username, afk):
        self._get_user(username).afk = afk
        self._update_round()
        self.sync_users()

    def restart_timer(self):
        self._start_round_timer(self._state.round_length)

    def _start_round_timer(self, duration):
        self._cancel_round_timer()
        self._publish("show_timer", {
            "title": "Round ending in: ",
            "duration": self._state.round_length
        })
        self._state.round_timer = Timer(duration,
            self._force_round_end, ())
        self._state.round_timer.start()

    def _cancel_round_timer(self):
        try:
            self._state.round_timer.cancel()
        except:
            pass
        self._publish("cancel_timer")

    def _start_round(self):
        self._state.step = "start_round"
        self._publish("start_round")
        for user in self._users:
            user.white_cards_played = []
            user.round_winner = False
            if user.playing_round is None:
                user.playing_round = True

        black_card = self._get_black_card()
        self._state.black_card = black_card

        self._publish("add_black", black_card)
        czar = self._set_next_czar()
        self._publish("czar_chosen", czar.username)
        self.sync_users()

        for i, user in enumerate(self._users):
            num_cards = len(user.hand)
            cards = self._get_white_cards(10 - num_cards)
            if len(cards) > 0:
                user.hand.extend(cards)
                self._publish("send_hand",
                    {"white_cards": user.hand},
                    eligible=[user.session_id])
        self._start_round_timer(self._state.round_length)

    def _set_next_czar(self):
        set_czar = False
        users = [u for u in self._users if u.afk == False]
        for i in range(0, len(users) + 1):
            user = users[(i + 1) % len(users)]
            if user.czar:
                user.czar = None
                set_czar = True
            elif set_czar:
                user.czar = 'czar'
                return user
        if not set_czar:
            users[0].czar = 'czar'
            return users[0]

    def _get_white_cards(self, num_cards):
        cards = []
        for _ in range(0, num_cards):
            card = random.choice(self._state.available_white_cards)
            cards.append(card)
            self._state.available_white_cards.remove(card)
            if len(self._state.available_white_cards) <= 0:
                self._state.available_white_cards = copy.deepcopy(
                    white_card_ids)
        with closing(Session()) as s:
            white_cards = (s.query(Cards)
                           .filter(Cards.id.in_(cards))
                           .all())
        return [{
                    "text": card.text,
                    "card_id": card.id
                } for card in white_cards]

    def _get_black_card(self):
        with closing(Session()) as s:
            card = random.choice(self._state.available_black_cards)
            self._state.available_black_cards.remove(card)
            with closing(Session()) as s:
                black_card = (s.query(Cards)
                              .filter(Cards.id == card)
                              .first())
        return {"text": black_card.text,
                "card_id": black_card.id,
                "num_white_cards": 1 if not black_card.pick else black_card.pick}

    def _update_round(self):
        # Playing white cards, see if round should go to judging
        if self._state.step == "start_round":
            players_outstanding = False
            max_whites = self._state.black_card['num_white_cards']
            for user in self._users:
                if user.czar or user.afk or not user.playing_round:
                    continue
                if len(user.white_cards_played) != max_whites:
                    players_outstanding = True

            if not players_outstanding:
                self._cancel_round_timer()
                cards = []
                for user in self._users:
                    if user.czar or user.afk:
                        continue
                    cards.append({
                        "group_id": user.session_id,
                        "white_cards": user.white_cards_played,
                        "num_cards": max_whites
                    })
                self._state.step = "begin_judging"
                random.shuffle(cards)
                self._publish("begin_judging", {"cards": cards})
                self.sync_users()
                self._start_round_timer(self._state.round_length)


    def _get_user(self, username=None, session_id=None):
        if username:
            return find(self._users, lambda u: u.username == username)
        if session_id:
            return find(self._users, lambda u: u.session_id == session_id)


    def _publish(self, topic, data=None, exclude=None, eligible=None):
        if self._wamp_client:
            self._wamp_client.publish(publish.format(topic),
                data, exclude=exclude, eligible=eligible)


    def _force_round_end(self, set_afk=True):
        if self._state.step == "start_round":
            max_whites = self._state.black_card['num_white_cards']
            for user in self._users:
                if user.czar or user.afk or not user.playing_round:
                    continue
                if len(user.white_cards_played) != max_whites:
                    if set_afk:
                        user.afk = True
                    user.white_cards_played = []
            self._update_round()
        elif self._state.step == "begin_judging":
            for user in self._users:
                if user.czar:
                    self._start_round()
                    user.afk = True
                    user.czar = None
                    break



class User(object):
    def __init__(self, username, session_id):
        self.username = username
        self.session_id = session_id
        self.white_cards_played = []
        self.hand = []
        self.czar = ''
        self.played_round = ''
        self.score = 0
        self.playing_round = None
        self.afk = False
        self.unplayed = False
        self.round_winner = False

    def to_dict(self):
        return {
            "username": self.username,
            "session_id": self.session_id,
            "czar": self.czar,
            "score": self.score,
            "afk": self.afk,
            "played_round": self.played_round,
            "unplayed": self.unplayed,
            "round_winner": self.round_winner
        }

    def reset(self):
        self.white_cards_played = []
        self.hand = []
        self.czar = None
        self.score = 0
        self.played_round = '',
        self.unplayed = False,
        self.round_winner = False

    def is_unplayed(self, max_whites):
        if self.czar or self.afk or not self.playing_round:
            return False
        played = len(self.white_cards_played)
        if played < max_whites:
            return True
        return False


class State(object):
    def __init__(self):
        self.step = "no_game"
        self.available_white_cards = copy.deepcopy(white_card_ids)
        self.available_black_cards = copy.deepcopy(black_card_ids)
        self.winning_score = 6
        self.round_length = 90
        self.black_card = None
        self.round_timer = None
        self.extended_round_time = self.round_length