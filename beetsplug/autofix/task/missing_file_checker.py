#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.58
#  License: See LICENSE.txt
import time
from os import path

from beetsplug.autofix.task import Task


class MissingFileCheckerTask(Task):
    removed = False

    def __init__(self):
        super(MissingFileCheckerTask, self).__init__()

    def setup(self, config, item):
        self.config = config
        self.item = item
        self.removed = False

    def run(self):
        if not path.isfile(self.item.get("path")):
            self._say("Item was deleted: {}...".format(self.item), log_only=True)
            self.item.remove()
            self.removed = True

    def item_was_removed(self):
        return self.removed
