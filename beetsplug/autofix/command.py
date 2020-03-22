#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/21/20, 11:28 AM
#  License: See LICENSE.txt
import os
import subprocess
import tempfile
from optparse import OptionParser

from beets import util
from beets.library import Library, Item, parse_query_parts
from beets.ui import Subcommand, decargs
from beets.util.confit import Subview

from beetsplug.autofix import common
from beetsplug import convert
from beetsplug.convert import ConvertPlugin

# The plugin
__PLUGIN_NAME__ = u'autofix'
__PLUGIN_SHORT_DESCRIPTION__ = u'fix your library with little effort'


class AutofixCommand(Subcommand):
    config: Subview = None
    lib: Library = None
    query = None
    parser: OptionParser = None

    temp_path = None

    def __init__(self, cfg):
        self.config = cfg

        # todo_ this should be class-wide
        self.temp_path = os.path.join(tempfile.gettempdir(), __PLUGIN_NAME__)
        if not os.path.isdir(self.temp_path):
            os.mkdir(self.temp_path)

        self.parser = OptionParser(usage='beet autofix [options] [QUERY...]')

        self.parser.add_option(
            '-v', '--version',
            action='store_true', dest='version', default=False,
            help=u'show plugin version'
        )

        # Keep this at the end
        super(AutofixCommand, self).__init__(
            parser=self.parser,
            name=__PLUGIN_NAME__,
            help=__PLUGIN_SHORT_DESCRIPTION__
        )

    def func(self, lib: Library, options, arguments):
        self.lib = lib
        self.query = decargs(arguments)

        if options.version:
            self.show_version_information()
            return

        self.handle_main_task()

    def handle_main_task(self):
        self.check_nonexistent_files()
        self.convert_non_mp3_files()
        self.convert_high_bitrate_files()

    def convert_high_bitrate_files(self):
        items = self._retrieve_library_items()
        self._say("Checking high bitrate items({})...".format(len(items)))
        for item in items:
            item: Item
            bitrate = int(item.get("bitrate"))
            if bitrate > 182000:
                self._say("Converting high bitrate ({}) to lower: {}".format(bitrate, item.get("path")))
                common.convert_item(item, self.temp_path)

    def convert_non_mp3_files(self):
        items = self._retrieve_library_items()
        self._say("Checking non-mp3 items({})...".format(len(items)))

        for item in items:
            item: Item
            fmt = item.get("format").lower()
            if fmt != "mp3":
                self._say("Converting {} to mp3: {}".format(fmt, item.get("path")))
                common.convert_item(item, self.temp_path)

    def check_nonexistent_files(self):
        items = self._retrieve_library_items()
        self._say("Checking nonexistent items({})...".format(len(items)))
        for item in items:
            item: Item
            filepath = item.get("path")
            if not os.path.isfile(filepath):
                self._say("Removing item for missing file: {}".format(filepath))
                item.remove()

    def _retrieve_library_items(self, query=None, model_cls=Item):
        query = [] if query is None else query
        parsed_query = parse_query_parts(query, model_cls)[0]
        self._say("Selection query[{}]: {}".format(query, parsed_query), log_only=True)

        return self.lib.items(parsed_query)

    def show_version_information(self):
        from beetsplug.autofix.version import __version__
        self._say("Plot(beets-{}) plugin for Beets: v{}".format(__PLUGIN_NAME__, __version__))

    def _say(self, msg, log_only=False):
        common.say(msg, log_only)
