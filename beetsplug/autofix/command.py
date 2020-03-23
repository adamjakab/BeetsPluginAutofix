#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/21/20, 11:28 AM
#  License: See LICENSE.txt
import os
import subprocess
import tempfile
import time
from optparse import OptionParser

from beets import util
from beets.dbcore.db import Results
from beets.library import Library, Item, parse_query_parts
from beets.ui import Subcommand, decargs
from beets.util.confit import Subview

from beetsplug.autofix import common

from beetsplug.zero import ZeroPlugin

from beetsplug.lastgenre import LastGenrePlugin

from beetsplug.xtractor import XtractorPlugin, XtractorCommand

# The plugin
__PLUGIN_NAME__ = u'autofix'
__PLUGIN_SHORT_DESCRIPTION__ = u'fix your library with little effort'


class AutofixCommand(Subcommand):
    config: Subview = None
    lib: Library = None
    query = None
    parser: OptionParser = None

    items: Results = None

    cfg_max_exec_time = None

    exec_time_start = None
    temp_path = None

    def __init__(self, config):
        self.config = config

        cfg = self.config.flatten()
        self.cfg_max_exec_time = cfg.get("max_exec_time")

        # todo_ this should be class-wide
        self.temp_path = os.path.join(tempfile.gettempdir(), __PLUGIN_NAME__)
        if not os.path.isdir(self.temp_path):
            os.mkdir(self.temp_path)

        self.parser = OptionParser(usage='beet autofix [options] [QUERY...]')

        self.parser.add_option(
            '-m', '--max_exec_time',
            action='store', dest='max_exec_time', type='int',
            default=self.cfg_max_exec_time,
            help=u'[default: {}] the number of seconds the execution can run'.format(
                self.cfg_max_exec_time)
        )

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

        self.cfg_max_exec_time = options.max_exec_time

        if options.version:
            self.show_version_information()
            return

        self.handle_main_task()

    def handle_main_task(self):
        self.exec_time_start = int(time.time())
        try:
            self.items = self._retrieve_library_items()
            self._say("Total number of items in library: {}".format(len(self.items)))
            self.check_nonexistent_files()
            self.convert_non_mp3_files()
            self.convert_high_bitrate_files()
            self.zero_unwanted_tags()
            self.set_genre()
            self.extract_audio_data()
        except TimeoutError:
            self._say("Time is up! {} seconds have passed.".format(self.cfg_max_exec_time))

    def extract_audio_data(self):
        plg = XtractorPlugin()
        cmd: XtractorCommand = plg.commands()[0]
        cmd.query = []
        cmd.lib = self.lib
        cmd.find_items_to_analyse()
        items = cmd.items_to_analyse

        self._say("Xtracting data from items({})...".format(len(items)))
        for item in items:
            self.check_timer()
            item: Item
            cmd.run_full_analysis(item)

    def set_genre(self):
        items = []
        plg = LastGenrePlugin()
        for item in self.items:
            item: Item
            genre = item.get("genre")
            if genre is None or genre == "":
                items.append(item)

        self._say("Checking missing genre for items({})...".format(len(items)))
        for item in items:
            self.check_timer()
            item: Item
            genre = item.get("genre")
            if genre is None or genre == "":
                genre, src = plg._get_genre(item)
                if genre:
                    self._say("Got Lastfm genre [genre: {}][source: {}] for item: {}"
                              .format(genre, src, item.evaluate_template('$path')))
                    item.genre = genre
                    item.store()
                    item.write()
                    continue

                # Use `genre_rosamerica` - better than nothing
                genre_rosamerica = item.get("genre_rosamerica")
                if genre_rosamerica in common.ROSAMERICA_GENRES.keys():
                    genre = common.ROSAMERICA_GENRES[genre_rosamerica]
                    self._say("Got Genre ROSAMERICA genre [genre: {}] for item: {}"
                              .format(genre, item.evaluate_template('$path')))
                    item.genre = genre
                    item.store()
                    item.write()
                    continue

                # if we are still here then there is no way of knowing the genre
                self._say("Unable to figure out genre for item: {}").format(item.evaluate_template('$path'))

    def zero_unwanted_tags(self):
        items = []
        plg = ZeroPlugin()
        plg_cfg = common.get_plugin_config("zero")
        if not plg_cfg or not plg_cfg["fields"].exists():
            self._say("No Zero plugin field config found. Scanning entire library.")
            items = self.items
        else:
            id_reg = []
            for fld in plg_cfg["fields"].get():
                for item in self.items:
                    item: Item
                    if item.id not in id_reg:
                        if len(str(item.get(fld))) > 0:
                            id_reg.append(item.id)
                            items.append(item)

        self._say("Checking non-zeroed items({})...".format(len(items)))
        for item in items:
            self.check_timer()
            item: Item
            self._say("Zeroing Item: {}".format(item.evaluate_template('$path')))
            plg.process_item(item)

    def convert_high_bitrate_files(self):
        items = []
        for item in self.items:
            item: Item
            bitrate = int(item.get("bitrate"))
            if bitrate > 182000:
                items.append(item)

        self._say("Converting high bitrate items({})...".format(len(items)))
        for item in items:
            self.check_timer()
            item: Item
            bitrate = int(item.get("bitrate"))
            self._say("Converting high bitrate ({}) to lower: {}".format(bitrate, item.get("path")))
            common.convert_item(item, self.temp_path)

    def convert_non_mp3_files(self):
        items = []
        for item in self.items:
            item: Item
            fmt = item.get("format").lower()
            if fmt != "mp3":
                items.append(item)

        self._say("Converting non-mp3 items({})...".format(len(items)))
        for item in items:
            self.check_timer()
            item: Item
            self._say("Converting to mp3: {}".format(item.get("path")))
            common.convert_item(item, self.temp_path)

    def check_nonexistent_files(self):
        self._say("Checking deleted items({})...".format(len(self.items)))
        remove_count = 0
        for item in self.items:
            self.check_timer()
            item: Item
            filepath = item.get("path")
            if not os.path.isfile(filepath):
                remove_count += 1
                item.remove()

        if remove_count > 0:
            self._say("Removed missing items: {}".format(remove_count))
            self.items = self._retrieve_library_items()

    def _retrieve_library_items(self, query=None, model_cls=Item):
        query = [] if query is None else query
        parsed_query = parse_query_parts(query, model_cls)[0]
        self._say("Selection query[{}]: {}".format(query, parsed_query), log_only=True)

        return self.lib.items(parsed_query)

    def show_version_information(self):
        from beetsplug.autofix.version import __version__
        self._say("Plot(beets-{}) plugin for Beets: v{}".format(__PLUGIN_NAME__, __version__))

    def check_timer(self):
        current_time = int(time.time())
        if self.cfg_max_exec_time != 0 and current_time - self.exec_time_start > self.cfg_max_exec_time:
            raise TimeoutError("Time up!")

    def _say(self, msg, log_only=False):
        common.say(msg, log_only)
