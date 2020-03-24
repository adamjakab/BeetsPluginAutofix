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
    zero_plugin = None

    def __init__(self):
        super(TagCleanerTask, self).__init__()

    def setup(self, config, items, library):
        self.config = config
        self.items = self._find_items_to_convert(items)
        self.library = library
        self.zero_plugin = ZeroPlugin()
        self._say("Checking items({}) to clean...".format(len(self.items)))

    def run_next(self):
        item: Item = self.items.pop(0)
        self._zero_item(item)

    def _zero_item(self, item):
        self.zero_plugin.process_item(item)

    def _find_items_to_convert(self, library_items):
        items = []
        plg_cfg = common.get_plugin_config("zero")
        if not plg_cfg or not plg_cfg["fields"].exists():
            self._say("No Zero plugin field config found. Scanning entire library.", log_only=True)
            items = library_items
        else:
            id_reg = []
            for item in library_items:
                item: Item
                if item.id not in id_reg:
                    for fld in plg_cfg["fields"].get():
                        if len(str(item.get(fld))) > 0:
                            id_reg.append(item.id)
                            items.append(item)
                            break

        return items
