import os
from webroot.roomsmanager import get_smallest_game_id
from webroot.settings import MUSTACHE_DIRS
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

@require_http_methods(['GET','HEAD']) # only allow GET and HEAD
def index(request, hash=None):
    filesContents = []
    for folder in MUSTACHE_DIRS:
        for file in os.listdir(folder):
            filesContents.append(open(''.join([folder, file]), 'rb').read())

    template_args = {
        "templates": ''.join(filesContents),
        "version": "0.12"
    }
    return render(request, 'index.html', template_args)
