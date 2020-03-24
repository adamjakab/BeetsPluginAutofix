#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.58
#  License: See LICENSE.txt

from beets.library import Item

from beetsplug.autofix.task import Task

from beetsplug.xtractor import XtractorPlugin, XtractorCommand


class XtractorTask(Task):
    xtractor_plugin = None

    def __init__(self):
        super(XtractorTask, self).__init__()

    def setup(self, config, items, library):
        self.xtractor_plugin = XtractorPlugin()
        self.config = config
        self.library = library
        self.items = self._find_items_to_convert()
        self._say("Checking items({}) to xtract...".format(len(self.items)))

    def run_next(self):
        item: Item = self.items.pop(0)
        self._extract_audio_data_from_item(item)

    def _extract_audio_data_from_item(self, item: Item):
        cmd: XtractorCommand = self.xtractor_plugin.commands()[0]
        cmd.run_full_analysis(item)

    def _find_items_to_convert(self):
        cmd: XtractorCommand = self.xtractor_plugin.commands()[0]
        cmd.query = []
        cmd.lib = self.library
        cmd.find_items_to_analyse()

        return list(cmd.items_to_analyse)
