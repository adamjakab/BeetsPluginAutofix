#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.58
#  License: See LICENSE.txt

from beetsplug.autofix import common
from beetsplug.autofix.task import Task
from beetsplug.zero import ZeroPlugin


class TagCleanerTask(Task):
    plugin = None
    plugin_config = None
    plugin_fields = None
    is_cleaned = False

    def __init__(self):
        super(TagCleanerTask, self).__init__()
        assert common.is_plugin_enabled("zero"), "The 'zero' plugin is not enabled!"
        self.plugin = ZeroPlugin()
        self.plugin_config = common.get_plugin_config("zero")
        self.plugin_fields = self.plugin_config["fields"].get() \
            if self.plugin_config.exists() and self.plugin_config["fields"].exists() else []

    def setup(self, config, item):
        self.config = config
        self.item = item
        self.is_cleaned = False

    def run(self):
        if not self._item_needs_processing():
            return

        self._say("Cleaning tags: {}".format(self.item), log_only=True)
        self.plugin.process_item(self.item)
        self.is_cleaned = True

    def _item_needs_processing(self):
        answer = False

        for fld in self.plugin_fields:
            if self.item.get(fld):
                answer = True
                break

        return answer

    def needs_item_store(self):
        answer = False

        if self.is_cleaned:
            if (self.plugin_config["update_database"].exists()
                and not self.plugin_config["update_database"].get(bool)) \
                    or not self.plugin_config["update_database"].exists():
                answer = True

        return answer
