from contextlib import closing
from twisted.internet import reactor
from autobahn.wamp import WampServerFactory, WampServerProtocol, exportRpc, WampClientFactory, WampClientProtocol
from autobahn.websocket import listenWS, connectWS
from webroot.db import Session

from webroot.game import Game
from webroot.models import Admin

game = Game()
admin_password = ''

class CahWampServer(WampServerProtocol):
    def __init__(self):
        self._username = ""

    @exportRpc
    def join(self, username, session_id):
        result = game.add_user(username, session_id)
        if result:
            self._username = username
        return result

    @exportRpc
    def sync_me(self):
        game.sync_me()

    @exportRpc
    def start_game(self):
        return game.start_game()

    @exportRpc
    def choose_white(self, card_id):
        game.choose_white(self._username, card_id)

    @exportRpc
    def judge_group(self, group_id):
        game.judge_group(self._username, group_id)

    @exportRpc
    def kick_user(self, admin_pass, username):
        if admin_pass == "MOVEMETODB":
            game.remove_user(username)

    @exportRpc
    def update_afk(self, afk):
        game.update_afk(self._username, afk)

    @exportRpc
    def restart_timer(self):
        game.restart_timer()

    def onSessionOpen(self):
        self.registerForRpc(self, "http://example.com/cah#")
        self.registerForPubSub("http://example.com/cahevent#", True)

    def connectionLost(self, reason):
        game.remove_user(self._username)
        try:
            super(self, reason)
        except:
            pass

class CahWampClient(WampClientProtocol):
    def onConnect(self, connectionResponse):
        game.register_client(self)


if __name__ == '__main__':
    with closing(Session()) as s:
        admin_password = s.query(Admin.password).scalar()

    server = "ws://localhost:9000"
    factory = WampServerFactory(server)
    factory.protocol = CahWampServer
    clientfactory = WampClientFactory(server)
    clientfactory.protocol = CahWampClient
    listenWS(factory)
    connectWS(clientfactory)
    try:
        reactor.run()
    except:
        pass

