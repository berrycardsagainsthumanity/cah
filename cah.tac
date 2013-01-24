import os

import yaml

from twisted.application import internet, service
from twisted.web import static, server
from autobahn.wamp import WampServerFactory

from caewebsockets import CahWampServer, CahWampService

with open("config.yml") as f:
    config = yaml.load(f)
    config['admin_password'] = os.getenv('CAH_ADMIN_PASS', config['admin_password'])

cahService = service.MultiService()

serverURI = "ws://{}".format(config['websocket_domain'])
cahWampFactory = WampServerFactory(serverURI, debug=False, debugWamp=True)
cahWampFactory.protocol = CahWampServer
CahWampService(9000, cahWampFactory).setServiceParent(cahService)

fileServer = server.Site(static.File(os.path.join(os.path.dirname(os.path.realpath(__file__)), "webroot", "static")))
internet.TCPServer(8000, fileServer).setServiceParent(cahService)

application = service.Application("CAH")
cahService.setServiceParent(application)
