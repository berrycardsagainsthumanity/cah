import os
import sys

import yaml
from twisted.internet import reactor
from twisted.python import log
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc
from autobahn.websocket import listenWS

from webroot.game import Game
from webroot.roomsmanager import rooms, get_smallest_game_id, create_new_game, get_or_create_room

with open("config.yml") as f:
    config = yaml.load(f)
    config['admin_password'] = os.getenv('CAH_ADMIN_PASS', config['admin_password'])

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
        if admin_pass == config['admin_password']:
            self._game.remove_user(username)

    @exportRpc
    def update_afk(self, afk = None):
        if afk:
            afk = True
        else:
            afk = False
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
        prefix = 'http://{}/{}{}#'
        self.registerForRpc(self, prefix.format(
            config['server_domain'],
            game_id,
            '_rpc',
        ))
        self.registerForPubSub(prefix.format(
            config['server_domain'],
            game_id,
            '',
        ), True)
        self._game = get_or_create_room(game_id)
        if self._username:
            self.join(self._username)
        return game_id

    def onSessionOpen(self):
        self.registerProcedureForRpc("http://{}/#join_game".format(config['server_domain']),
            self.join_game)
        # TODO: Why is this line here?
        self.registerProcedureForRpc("http://{}/#join_game".format(config['server_domain']),
            self.join_game)

    def connectionLost(self, reason):
        if self._game:
            self._game.remove_user(self._username)
        try:
            super(self, reason)
        except:
            pass


if __name__ == '__main__':
    log.startLogging(sys.stdout)
    server = "ws://{}".format(config['websocket_domain'])
    factory = WampServerFactory(server, debug=False, debugWamp=True)
    factory.protocol = CahWampServer
    Game.register_cah_wamp_client(factory)
    listenWS(factory)
    try:
        reactor.run()
    except:
        pass
