#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.58
#  License: See LICENSE.txt

from beets.library import Item
from beets.util.confit import Subview
from beetsplug.autofix import common
from beetsplug.autofix.task import Task
from beetsplug.xtractor import XtractorPlugin, XtractorCommand


class XtractorTask(Task):
    plugin = None
    plugin_config: Subview = None

    def __init__(self):
        super(XtractorTask, self).__init__()
        assert common.is_plugin_enabled("xtractor"), "The 'xtractor' plugin is not enabled!"
        self.plugin = XtractorPlugin()
        self.plugin_config = common.get_plugin_config("xtractor")

    def setup(self, config, item: Item):
        self.config = config
        self.item = item

    def run(self):
        if not self._item_needs_processing():
            return

        self._say("Xtracting item: {}".format(self.item), log_only=True)
        cmd: XtractorCommand = self.plugin.commands()[0]
        cmd.cfg_quiet = True
        cmd.run_full_analysis(self.item)

    def _item_needs_processing(self):
        answer = False

        target_maps = ["low_level_targets", "high_level_targets"]

        for map_key in target_maps:
            if answer:
                break
            target_map = self.plugin_config[map_key]
            for fld in target_map:
                if target_map[fld]["required"].exists() and target_map[fld]["required"].get(bool):
                    if not self.item.get(fld):
                        answer = True
                        break

        return answer
