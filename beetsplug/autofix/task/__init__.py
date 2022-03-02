#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/24/20, 10:19 AM
#  License: See LICENSE.txt
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/24/20, 9:52 AM
#  License: See LICENSE.txt

from abc import ABC
from abc import abstractmethod

from beets.library import Item, Library
from beets.util.confit import Subview
from beetsplug.autofix import common


class Task(ABC):
    config: Subview = None
    lib: Library = None
    item: Item = None

    def __init__(self):
        pass

    def set_library(self, lib):
        self.lib = lib

    def _say(self, msg, log_only=False):
        msg = "[{name}]: {msg}".format(name=self.__class__.__name__, msg=msg)
        common.say(msg, log_only)

    @abstractmethod
    def setup(self, config, item):
        raise NotImplementedError("You must implement this method.")

    @abstractmethod
    def run(self):
        raise NotImplementedError("You must implement this method.")

    @staticmethod
    def needs_item_store():
        """Indicates that the library item needs to be stored
        """
        return False

    @staticmethod
    def needs_item_write():
        """Indicates that the library item needs to be written to the media file
        """
        return False

    @staticmethod
    def item_was_removed():
        """Indicates that the library item was removed (so all further tasks should be skipped)
        """
        return False
