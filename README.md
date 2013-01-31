BerryCAH
=========

BerryCAH is a live, online version of the popular [Cards Against Humanity](http://www.cardsagainsthumanity.com/) party game.

Installation
============

Set up a virtualenv; you can also use virtualenv-wrapper:

    $ virtualenv --distribute BerryCAH
    $ cd BerryCAH
    $ . bin/activate

Then grab the source and dependencies:

    $ git clone https://github.com/berrycardsagainsthumanity/cah.git
    $ pip install -e cah

To start the server (on http://localhost:8765/ by default), run:

    $ cd cah/src
    $ twistd -noy cah.tac

Or on Windows:

    > cd cah\src
    > python ..\..\Scripts\twistd.py -noy cah.tac

Note that since BerryCAH is run using the standard `twistd` runner for Twisted programs, you can also run daemonized, redirect logging output, and more using [its options](http://linux.die.net/man/1/twistd).

Configuration
=============

Server configuration is contained in `src/config.yml`.

Licenses
========
BerryCAH still doesn't have one until Marm fixes #6.

The standard Cards Against Humanity cardsets are (C) Cards Against Humanity, LLC., used under a [CC-BY-NC-SA 2.0](http://creativecommons.org/licenses/by-nc-sa/2.0/) license.

Other cardsets are taken from their respective online communities.

[jQuery](http://jquery.org/), [jQuery Mobile Events](https://github.com/benmajor/jQuery-Mobile-Events), [jQuery UI](http://jqueryui.com/), [iCanHaz.js](http://icanhazjs.com/), [mustache.js](https://github.com/janl/mustache.js), [AutobahnJS](http://autobahn.ws/js), [Twisted](http://twistedmatrix.com/), [PyYAML](http://pyyaml.org/), and [Pystache](http://pypi.python.org/pypi/pystache) were created by their respective authors and used under the terms of the [MIT license](http://opensource.org/licenses/MIT), reprinted here because several of these libraries are delivered as a part of this repository:

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[AutobahnPython](http://autobahn.ws/python) was created by Tavendo GmbH and is used under the terms of the [Apache License 2.0](http://opensource.org/licenses/Apache-2.0).
