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

from beets.library import Library
from beets.util.confit import Subview

from beetsplug.autofix import common


class Task(ABC):
    config: Subview = None
    items: list = None
    library: Library = None

    def __init__(self):
        pass

    @staticmethod
    def _say(msg, log_only=False):
        common.say(msg, log_only)

    @abstractmethod
    def setup(self, config, items, library):
        raise NotImplementedError("You must implement this method.")

    @abstractmethod
    def run_next(self):
        raise NotImplementedError("You must implement this method.")

    def is_finished(self):
        return len(self.items) == 0

    @staticmethod
    def needs_items_reload():
        """Indicates if the library items should be reloaded (like in the case of removing missing elements)
        """
        return False

