#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.58
#  License: See LICENSE.txt

from beets.library import Item
from beetsplug.zero import ZeroPlugin

from beetsplug.autofix import common
from beetsplug.autofix.task import Task


class TagCleanerTask(Task):
    plugin = None

    def __init__(self):
        super(TagCleanerTask, self).__init__()
        assert common.is_plugin_enabled("zero"), "The 'zero' plugin is not enabled!"
        self.plugin = ZeroPlugin()

    def setup(self, config, item):
        self.config = config
        self.item = item

    def run(self):
        if not self._item_needs_processing():
            return

        self._say("Cleaning: {}".format(self.item))
        self.plugin.process_item(self.item)

    def _item_needs_processing(self):
        answer = False

        plg_cfg = common.get_plugin_config("zero")

        if not plg_cfg.exists() or not plg_cfg["fields"].exists():
            answer = True
        else:
            for fld in plg_cfg["fields"].get():
                if len(str(self.item.get(fld))) > 0:
                    answer = True
                    break

        return answer

    @staticmethod
    def needs_item_write():
        return True
