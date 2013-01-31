import os

import yaml

from twisted.application import internet, service
from twisted.web import static, server, resource
from autobahn.wamp import WampServerFactory

import pystache
from caewebsockets import CahWampServer, CahWampService

WEBROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "www")

with open("config.yml") as f:
    config = yaml.load(f)
    config['admin_password'] = os.getenv('CAH_ADMIN_PASS', config['admin_password'])

cahService = service.MultiService()

## Set up the websocket server
serverURI = "ws://{websocket_domain}:{websocket_port}".format(**config)
cahWampFactory = WampServerFactory(serverURI, debug=False, debugWamp=True)
cahWampFactory.protocol = CahWampServer
CahWampService(
    config['websocket_domain'],
    config['websocket_port'],
    "{server_domain}:{server_port}".format(**config),
    cahWampFactory,
    ).setServiceParent(cahService)

## Set up the web server
fileResource = static.File(os.path.join(WEBROOT_DIR))

# This is the ugly bit--we need to construct a resource tree to get our templated .js in here
jsResource = static.File(os.path.join(WEBROOT_DIR, "js"))
with open(os.path.join(WEBROOT_DIR, "js", "init.mustache")) as f:
    jsResource.putChild(
        'init.js',
        static.Data(pystache.render(f.read(), config).encode('utf-8'), "application/javascript"),
        )
fileResource.putChild('js', jsResource)

fileResource.indexNames=['index.mustache']

fileServer = server.Site(fileResource)
internet.TCPServer(config['server_port'], fileServer).setServiceParent(cahService)

## Define the application
application = service.Application("CAH")
cahService.setServiceParent(application)
