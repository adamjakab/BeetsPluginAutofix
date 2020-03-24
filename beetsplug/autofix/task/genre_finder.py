#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 24/03/2020, 15.57
#  License: See LICENSE.txt

from beets.library import Item

from beetsplug.autofix.task import Task

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
    lastgenre_plugin = None

    def __init__(self):
        super(GenreFinderTask, self).__init__()

    def setup(self, config, items, library):
        self.config = config
        self.items = self._find_items_to_convert(items)
        self.library = library
        self.lastgenre_plugin = LastGenrePlugin()
        self._say("Checking items({}) without genre...".format(len(self.items)))

    def run_next(self):
        item: Item = self.items.pop(0)
        self._set_genre_for_item(item)

    def _set_genre_for_item(self, item: Item):
        # Try Lastgenre plugin
        genre, src = self.lastgenre_plugin._get_genre(item)
        if genre:
            self._say("Got Lastfm genre [genre: {}][source: {}] for item: {}"
                      .format(genre, src, item.evaluate_template('$path')), log_only=True)
            item.genre = genre

        # Try `genre_rosamerica` value - better than nothing
        if item.get("genre") is None or item.get("genre") == "":
            genre_rosamerica = item.get("genre_rosamerica")
            if genre_rosamerica in ROSAMERICA_GENRES.keys():
                genre = ROSAMERICA_GENRES[genre_rosamerica]
                self._say("Got Genre ROSAMERICA genre [genre: {}] for item: {}"
                          .format(genre, item.evaluate_template('$path')), log_only=True)
                item.genre = genre

        if item.get("genre"):
            item.store()
            item.write()
        else:
            self._say("Unable to figure out genre for item: {}").format(item.evaluate_template('$path'), log_only=True)

    @staticmethod
    def _find_items_to_convert(library_items):
        items = []
        for item in library_items:
            item: Item
            genre = item.get("genre")
            if genre is None or genre == "":
                items.append(item)

        return items
