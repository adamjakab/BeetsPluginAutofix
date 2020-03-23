#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/21/20, 11:28 AM
#  License: See LICENSE.txt

import logging
import sys
import os
import subprocess
import tempfile

from beets import util
from beets import config
from beets.library import Item
from beetsplug import convert
from beetsplug.convert import ConvertPlugin

__logger__ = logging.getLogger('beets.autofix')

ROSAMERICA_GENRES = {
    "cla": "classical",
    "dan": "dance",
    "hip": "hip-hop",
    "jaz": "jazz",
    "pop": "pop",
    "rhy": "rhythm and blues",
    "roc": "rock",
    "spe": "speech"
}


def convert_item(item: Item, temp_path):
    orig_path = item.get("path")

    command, ext = convert.get_format()
    fd, dest_path = tempfile.mkstemp(util.py3_path(b'.' + ext), dir=temp_path)
    os.close(fd)
    dest_path = util.bytestring_path(dest_path)

    try:
        plg = ConvertPlugin()
        plg.encode(command, orig_path, dest_path)
    except subprocess.CalledProcessError:
        say("There was an error.")

    item.path = dest_path
    item.write()
    item.read()
    os.unlink(orig_path)
    item.move()
    item.store()


def get_plugin_config(plugin_name):
    cfg = None
    if config[plugin_name].exists():
        cfg = config[plugin_name]

    return cfg

def say(msg, log_only=False):
    """Log and write to stdout
    """
    __logger__.debug(msg)
    if not log_only:
        sys.stdout.write(msg + "\n")
