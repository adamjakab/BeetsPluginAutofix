#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.57
#  License: See LICENSE.txt

from beetsplug.autofix.task import Task

from beetsplug.autofix import common
from beetsplug.lastgenre import LastGenrePlugin

ROSAMERICA_GENRES = {
    "cla": "classical",
    "dan": "dance",
    "hip": "hip-hop",
    "jaz": "jazz",
    "pop": "pop",
    "rhy": "rhythm and blues",
    "roc": "rock",
    "spe": "speech"
}


class GenreFinderTask(Task):
    plugin = None
    found_new_genre = False

    def __init__(self):
        super(GenreFinderTask, self).__init__()
        assert common.is_plugin_enabled("lastgenre"), "The 'lastgenre' plugin is not enabled!"
        self.plugin = LastGenrePlugin()

    def setup(self, config, item):
        self.config = config
        self.item = item
        self.found_new_genre = False

    def run(self):
        if not self._item_needs_processing():
            return

        self._say("Finding genre for: {}".format(self.item), log_only=True)

        # Try Lastgenre plugin
        genre, src = self.plugin._get_genre(self.item)
        if genre:
            self._say("Got Lastfm genre [genre: {}][source: {}] for item: {}"
                      .format(genre, src, self.item), log_only=True)
            self.item.genre = genre
            self.found_new_genre = True

        # Try `genre_rosamerica` value - better than nothing
        if self.item.get("genre") is None or self.item.get("genre") == "":
            genre_rosamerica = self.item.get("genre_rosamerica")
            if genre_rosamerica in ROSAMERICA_GENRES.keys():
                genre = ROSAMERICA_GENRES[genre_rosamerica]
                self._say("Got Genre ROSAMERICA genre [genre: {}] for item: {}"
                          .format(genre, self.item), log_only=True)
                self.item.genre = genre
                self.found_new_genre = True

        if not self.item.get("genre"):
            self._say("Unable to find genre for item: {}").format(self.item, log_only=True)

    def _item_needs_processing(self):
        answer = False

        genre = self.item.get("genre")
        if genre is None or genre == "":
            answer = True

        return answer

    def needs_item_store(self):
        return self.found_new_genre

    def needs_item_write(self):
        return self.found_new_genre
