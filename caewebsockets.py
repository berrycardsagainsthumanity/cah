from contextlib import closing
import sys
from twisted.internet import reactor
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc, WampClientFactory, WampClientProtocol
from autobahn.websocket import listenWS, connectWS
from twisted.python import log
from webroot.db import Session
from webroot.game import Game

from webroot.models import Admin
from webroot.roomsmanager import rooms, get_smallest_game_id, create_new_game, get_or_create_room

admin_password = ''

class CahWampServer(WampServerProtocol):
    def __init__(self):
        self._username = ""
        self._game_id = -1
        self._game = None

    @exportRpc
    def join(self, username):
        result = self._game.add_user(username, self)
        if result:
            self._username = username
        return result

    @exportRpc
    def sync_me(self):
        self._game.sync_me()

    @exportRpc
    def start_game(self):
        return self._game.start_game()

    @exportRpc
    def choose_white(self, card_id):
        self._game.choose_white(self._username, card_id)

    @exportRpc
    def judge_group(self, group_id):
        self._game.judge_group(self._username, group_id)

    @exportRpc
    def kick_user(self, admin_pass, username):
        if admin_pass == admin_password:
            self._game.remove_user(username)

    @exportRpc
    def update_afk(self, afk):
        self._game.update_afk(self._username, afk)

    @exportRpc
    def restart_timer(self):
        self._game.restart_timer()

    @exportRpc
    def get_rooms(self):
        return {
            "rooms": [{
                    "game_id": game_id,
                    "users":[{"username": u.username} for u in game.users]
                } for game_id, game in rooms.items()]
        }

    @exportRpc
    def create_game(self):
        game = create_new_game()
        self.join_game(game.game_id)
        return game.game_id

    def join_game(self, game_id):
        if game_id < 0:
            game_id = get_smallest_game_id()
        elif self._game:
            self._game.remove_user(self._username)
        self._game_id = game_id
        prefix = 'http://example.com/{0}{1}#'
        self.registerForRpc(self, prefix.format(game_id, '_rpc'))
        self.registerForPubSub(prefix.format(game_id, ''), True)
        self._game = get_or_create_room(game_id)
        if self._username:
            self.join(self._username)
        return game_id

    def onSessionOpen(self):
        self.registerProcedureForRpc("http://example.com/#join_game",
            self.join_game)
        self.registerProcedureForRpc("http://example.com/#join_game",
            self.join_game)

    def connectionLost(self, reason):
        if self._game:
            self._game.remove_user(self._username)
        try:
            super(self, reason)
        except:
            pass


if __name__ == '__main__':
    with closing(Session()) as s:
        admin_password = s.query(Admin.password).scalar()
    log.startLogging(sys.stdout)
    server = "ws://localhost:9000"
    factory = WampServerFactory(server, debug=False, debugWamp=True)
    factory.protocol = CahWampServer
    Game.register_cah_wamp_client(factory)
    listenWS(factory)
    try:
        reactor.run()
    except:
        pass

