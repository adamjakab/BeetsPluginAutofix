#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.58
#  License: See LICENSE.txt

from beets.library import Item

from beetsplug.autofix.task import Task


class XtractorTask(Task):
    def __init__(self):
        super(XtractorTask, self).__init__()

    def setup(self, config, items):
        self.config = config
        self.items = list(items)
        self._say("Checking items({}) to xtract...".format(len(self.items)))

    def run_next(self):
        item: Item = self.items.pop(0)




