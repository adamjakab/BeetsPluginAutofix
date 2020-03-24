#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/24/20, 9:53 AM
#  License: See LICENSE.txt

from os import path

from beets.library import Item

from beetsplug.autofix.task import Task


class MissingFileChecker(Task):
    number_of_items_deleted = 0

    def __init__(self):
        super(MissingFileChecker, self).__init__()

    def setup(self, config, items):
        self.config = config
        self.items = list(items)
        self._say("Checking deleted items({})...".format(len(self.items)))

    def run_next(self):
        item: Item = self.items.pop(0)
        if not path.isfile(item.get("path")):
            item.remove()
            self.number_of_items_deleted += 1

    def needs_items_reload(self):
        return self.number_of_items_deleted > 0
