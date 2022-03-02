#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/21/20, 11:28 AM
#  License: See LICENSE.txt

import logging
import os

from beets import config

# Get values as: plg_ns['__PLUGIN_NAME__']
plg_ns = {}
about_path = os.path.join(os.path.dirname(__file__), u'about.py')
with open(about_path) as about_file:
    exec(about_file.read(), plg_ns)

__logger__ = logging.getLogger('beets.{plg}'.format(plg=plg_ns['__PLUGIN_NAME__']))


def is_plugin_enabled(plugin_name):
    enabled_plugins = config["plugins"].get() if config["plugins"].exists() else []
    return plugin_name in enabled_plugins


def get_plugin_config(plugin_name):
    cfg = None
    if config[plugin_name].exists():
        cfg = config[plugin_name]
    return cfg


def say(msg, log_only=True, is_error=False):
    _level = logging.DEBUG
    _level = _level if log_only else logging.INFO
    _level = _level if not is_error else logging.ERROR
    __logger__.log(level=_level, msg=msg)
