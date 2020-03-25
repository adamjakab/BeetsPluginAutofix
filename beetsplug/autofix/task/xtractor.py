#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.58
#  License: See LICENSE.txt

from beets.library import Item

from beetsplug.autofix.task import Task

from beetsplug.autofix import common
from beetsplug.xtractor import XtractorPlugin, XtractorCommand


class XtractorTask(Task):
    plugin = None

    def __init__(self):
        super(XtractorTask, self).__init__()
        assert common.is_plugin_enabled("xtractor"), "The 'xtractor' plugin is not enabled!"
        self.plugin = XtractorPlugin()

    def setup(self, config, item):
        self.config = config
        self.item = item

    def run(self):
        cmd: XtractorCommand = self.plugin.commands()[0]
        cmd.run_full_analysis(self.item)

    def _item_needs_processing(self):
        answer = False

        return answer
