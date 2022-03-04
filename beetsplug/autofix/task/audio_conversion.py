#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 16.00
#  License: See LICENSE.txt

import os
import subprocess
import tempfile

from beets import util
from beetsplug import convert
from beetsplug.convert import ConvertPlugin

from beetsplug.autofix import common
from beetsplug.autofix.task import Task


class AudioConversionTask(Task):
    temp_path = None
    plugin = None

    def __init__(self):
        super(AudioConversionTask, self).__init__()
        assert common.is_plugin_enabled("convert"), "The 'convert' plugin is not enabled!"
        self.plugin = ConvertPlugin()

    def setup(self, config, item):
        self.config = config
        self.item = item

        self.temp_path = os.path.join(tempfile.gettempdir(), self.__class__.__name__)
        if not os.path.isdir(self.temp_path):
            os.mkdir(self.temp_path)

    def run(self):
        if not self._item_needs_processing():
            return

        self._say("Converting: {}".format(self.item.evaluate_template("[$format][$bitrate]: $path")), log_only=True)
        orig_path = self.item.get("path")

        command, ext = convert.get_format()
        fd, dest_path = tempfile.mkstemp(util.py3_path(b'.' + ext), dir=self.temp_path)
        os.close(fd)
        dest_path = util.bytestring_path(dest_path)

        try:
            self.plugin.encode(command, orig_path, dest_path)
        except subprocess.CalledProcessError as err:
            self._say("Conversion error: {}".format(err))
            return

        # Must handle item storage and write differently from autofix
        self.item.path = dest_path
        self.item.write()
        self.item.read()
        os.unlink(orig_path)
        self.item.move()
        self.item.store()

    def _item_needs_processing(self):
        answer = False

        plg_cfg = common.get_plugin_config("convert")

        if plg_cfg["format"].exists():
            fmt = plg_cfg["format"].as_str().lower()
            if self.item.get("format").lower() != fmt:
                answer = True

        if plg_cfg["max_bitrate"].exists():
            max_bitrate = plg_cfg["max_bitrate"].as_number() * 1000
            if int(self.item.get("bitrate")) > max_bitrate:
                answer = True

        return answer
