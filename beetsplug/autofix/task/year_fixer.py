#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/26/20, 8:14 PM
#  License: See LICENSE.txt

from beetsplug.autofix import common
from beetsplug.autofix.task import Task
from beetsplug.yearfixer import YearFixerPlugin, YearFixerCommand


class YearFixerTask(Task):
    plugin = None
    plugin_config = None
    year_fixed = False

    def __init__(self):
        super(YearFixerTask, self).__init__()
        assert common.is_plugin_enabled("yearfixer"), "The 'yearfixer' plugin is not enabled!"
        self.plugin = YearFixerPlugin()
        self.plugin_config = common.get_plugin_config("yearfixer")

    def setup(self, config, item):
        self.config = config
        self.item = item
        self.year_fixed = False

    def run(self):
        if not self._item_needs_processing():
            return

        cmd: YearFixerCommand = self.plugin.commands()[0]
        cmd.lib = self.lib

        orig_year = self.item.get("year")
        orig_original_year = self.item.get("original_year")
        self._say("Calling yearfixer plugin for item: {}".format(self.item), log_only=True)
        cmd.process_item(self.item)
        if orig_year != self.item.get("year") or orig_original_year != self.item.get("original_year"):
            self.year_fixed = True

    def _item_needs_processing(self):
        answer = False

        if not self.item.get("year") or not self.item.get("original_year"):
            answer = True

        return answer

    def needs_item_store(self):
        return self.year_fixed

    def needs_item_write(self):
        return self.year_fixed
