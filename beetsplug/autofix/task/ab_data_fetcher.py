#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/25/20, 3:44 PM
#  License: See LICENSE.txt

from beets.util.confit import Subview

from beetsplug.autofix import common
from beetsplug.autofix.task import Task

from beetsplug.acousticbrainz import AcousticPlugin


class ABDataFetcherTask(Task):
    plugin = None
    plugin_config = None
    has_new_data = False

    def __init__(self):
        super(ABDataFetcherTask, self).__init__()
        assert common.is_plugin_enabled("acousticbrainz"), "The 'acousticbrainz' plugin is not enabled!"
        self.plugin = AcousticPlugin()
        self.plugin_config = common.get_plugin_config("xtractor")

    def setup(self, config, item):
        self.config = config
        self.item = item
        self.has_new_data = False

    def run(self):
        if not self._item_needs_processing():
            return

        self._say("Getting AB data: {}".format(self.item), log_only=True)

        abdata = self.plugin._get_data(self.item.mb_trackid)
        if not abdata:
            return

        audiodata = self._extract_from_abdata(abdata)
        if not audiodata:
            return

        self._say("Got clean AB data: {}".format(audiodata), log_only=True)
        self.has_new_data = True
        for attr in audiodata.keys():
            if audiodata.get(attr):
                setattr(self.item, attr, audiodata.get(attr))

    def _extract_from_abdata(self, abdata):
        """extracts data from the low level json file as mapped out in the `low_level_targets` configuration key
        """
        data = {}

        target_maps = ["low_level_targets", "high_level_targets"]
        for map_key in target_maps:
            target_map = self.plugin_config[map_key]
            for key in target_map.keys():
                try:
                    val = self._extract_value_from_abdata(abdata, target_map[key])
                except AttributeError:
                    val = None

                data[key] = val

        return data

    @staticmethod
    def _extract_value_from_abdata(abdata, target_map_item: Subview):
        path: str = target_map_item["path"].as_str()
        value_type = target_map_item["type"].as_str()
        path_parts = path.split(".")
        for part in path_parts:
            if not part in abdata:
                raise AttributeError("No path '{}' found in abdata".format(path))
            abdata = abdata[part]

        if value_type == "string":
            value = str(abdata)
        elif value_type == "float":
            value = float(abdata)
        elif value_type == "integer":
            value = int(round(float(abdata)))
        else:
            value = abdata

        return value

    def _item_needs_processing(self):
        answer = False

        if not self.item.mb_trackid:
            return False

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

    def needs_item_store(self):
        return self.has_new_data

    def needs_item_write(self):
        return self.has_new_data
