#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/25/20, 3:44 PM
#  License: See LICENSE.txt

from beets.util.confit import Subview

from beetsplug.autofix import common
from beetsplug.autofix.task import Task

from beetsplug.acousticbrainz import AcousticPlugin

target_map = {
    'average_loudness': {
        'path': 'lowlevel.average_loudness',
        'type': float,
    },
    'bpm': {
        'path': 'rhythm.bpm',
        'type': int,
    },
    'danceable': {
        'path': 'highlevel.danceability.all.danceable',
        'type': float,
    },
    'gender': {
        'path': 'highlevel.gender.value',
        'type': str,
    },
    'genre_rosamerica': {
        'path': 'highlevel.genre_rosamerica.value',
        'type': str,
    },
    'voice_instrumental': {
        'path': 'highlevel.voice_instrumental.value',
        'type': str,
    },
    'mood_acoustic': {
        'path': 'highlevel.mood_acoustic.all.acoustic',
        'type': float,
    },
    'mood_aggressive': {
        'path': 'highlevel.mood_aggressive.all.aggressive',
        'type': float,
    },
    'mood_electronic': {
        'path': 'highlevel.mood_electronic.all.electronic',
        'type': float,
    },
    'mood_happy': {
        'path': 'highlevel.mood_happy.all.happy',
        'type': float,
    },
    'mood_party': {
        'path': 'highlevel.mood_party.all.party',
        'type': float,
    },
    'mood_relaxed': {
        'path': 'highlevel.mood_relaxed.all.relaxed',
        'type': float,
    },
    'mood_sad': {
        'path': 'highlevel.mood_sad.all.sad',
        'type': float,
    }

    # 'chords_changes_rate': types.Float(6),
    # 'chords_key': types.STRING,
    # 'chords_number_rate': types.Float(6),
    # 'chords_scale': types.STRING,
    # 'initial_key': types.STRING,
    # 'key_strength': types.Float(6),
    # 'rhythm': types.Float(6),
    # 'tonal': types.Float(6),
}


class ABDataFetcherTask(Task):
    plugin = None
    plugin_config: Subview = None
    has_new_data = False

    def __init__(self):
        super(ABDataFetcherTask, self).__init__()
        assert common.is_plugin_enabled("acousticbrainz"), \
            "The 'acousticbrainz' plugin is not enabled!"
        self.plugin = AcousticPlugin()
        self.plugin_config = common.get_plugin_config("acousticbrainz")

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
        for attr in audiodata.keys():
            if (audiodata.get(attr) and not self.item.get(attr)) or \
                    self.plugin_config["force"].get(bool):
                setattr(self.item, attr, audiodata.get(attr))
                self.has_new_data = True

    def _extract_from_abdata(self, abdata):
        """extracts data from the low level json file as mapped out in the
        `low_level_targets` configuration key
        """
        data = {}
        for key in target_map.keys():
            try:
                val = self._extract_value_from_abdata(abdata,
                                                      target_map[key])
            except AttributeError:
                val = None

            data[key] = val

        return data

    @staticmethod
    def _extract_value_from_abdata(abdata, target_map_item: Subview):
        path: str = target_map_item["path"]
        value_type = target_map_item["type"]
        path_parts = path.split(".")

        for part in path_parts:
            if not part in abdata:
                raise AttributeError(
                    "No path '{}' found in abdata".format(path))
            abdata = abdata[part]

        return value_type(abdata)

    def _item_needs_processing(self):
        answer = False

        if not self.item.mb_trackid:
            self._say("Item does not have `mb_trackid`. Cannot proceed.",
                      log_only=True)
            return False

        if self.plugin_config["force"].get(bool):
            return True

        # Check attributes listed in the AB plugin
        for fld in target_map.keys():
            if not self.item.get(fld):
                answer = True
                break

        return answer

    def needs_item_store(self):
        return self.has_new_data

    def needs_item_write(self):
        return self.has_new_data
