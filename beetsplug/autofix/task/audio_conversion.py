#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 16.00
#  License: See LICENSE.txt

import os
import subprocess
import tempfile

from beets.library import Item
from beets import util
from beetsplug import convert
from beetsplug.convert import ConvertPlugin

from beetsplug.autofix.task import Task


class AudioConversionTask(Task):
    temp_path = None

    def __init__(self):
        super(AudioConversionTask, self).__init__()

    def setup(self, config, items, library):
        self.config = config
        self.items = self._find_items_to_convert(items)
        self.library = library

        self.temp_path = os.path.join(tempfile.gettempdir(), self.__class__.__name__)
        if not os.path.isdir(self.temp_path):
            os.mkdir(self.temp_path)

        self._say("Converting items({})...".format(len(self.items)))

    def run_next(self):
        item: Item = self.items.pop(0)
        self._convert_item(item)

    def _convert_item(self, item: Item):
        orig_path = item.get("path")

        command, ext = convert.get_format()
        fd, dest_path = tempfile.mkstemp(util.py3_path(b'.' + ext), dir=self.temp_path)
        os.close(fd)
        dest_path = util.bytestring_path(dest_path)

        try:
            plg = ConvertPlugin()
            plg.encode(command, orig_path, dest_path)
        except subprocess.CalledProcessError:
            self._say("There was an error.")

        item.path = dest_path
        item.write()
        item.read()
        os.unlink(orig_path)
        item.move()
        item.store()

    def _find_items_to_convert(self, library_items):
        items = []

        for item in library_items:
            item: Item
            if item.get("format").lower() != self.config["format"].as_str():
                items.append(item)
                continue
            if int(item.get("bitrate")) > self.config["max_bitrate"].as_number():
                items.append(item)
                continue

        return items

