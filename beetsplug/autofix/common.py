#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/21/20, 11:28 AM
#  License: See LICENSE.txt

import logging

from beets import config

__logger__ = logging.getLogger('beets.autofix')


def is_plugin_enabled(plugin_name):
    enabled_plugins = config["plugins"].get() if config["plugins"].exists() else []
    return plugin_name in enabled_plugins


def get_plugin_config(plugin_name):
    cfg = None
    if config[plugin_name].exists():
        cfg = config[plugin_name]
    return cfg


def say(msg, log_only=False):
    if log_only:
        __logger__.debug(msg)
    else:
        __logger__.info(msg)
