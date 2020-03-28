#  Copyright: Copyright (c) 2020., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 3/26/20, 8:14 PM
#  License: See LICENSE.txt

import time

from beetsplug.autofix.task import Task

from beetsplug.autofix import common
import requests
from urllib.parse import quote, quote_plus

MB_BASE = "https://musicbrainz.org/ws/2/"


class YearFixerTask(Task):
    plugin = None
    year_fixed = False

    def __init__(self):
        super(YearFixerTask, self).__init__()

    def setup(self, config, item):
        self.config = config
        self.item = item
        self.year_fixed = False

    def run(self):
        if not self._item_needs_processing():
            return

        self._say("Finding year for: {}".format(self.item), log_only=True)

        year = self.item.get("year")
        original_year = self.item.get("original_year")

        if not original_year:
            data = self._get_data()
            if data:
                original_year = self._extract_original_year_from_mbdata(data)
                self._say("Got original year:{}".format(original_year), log_only=True)
                setattr(self.item, "original_year", original_year)
                self.year_fixed = True

        if original_year and not year:
            setattr(self.item, "year", original_year)
            self.year_fixed = True

        if year and not original_year:
            setattr(self.item, "original_year", year)
            self.year_fixed = True

        if not year and not original_year:
            self._say("Cannot find year info", log_only=True)

    def _extract_original_year_from_mbdata(self, data):
        answer = None

        if "recordings" in data.keys():
            for recording in data["recordings"]:
                if "releases" in recording.keys():
                    for release in recording["releases"]:
                        if "date" in release.keys():
                            try:
                                rel_year = int(release["date"][:4])
                            except ValueError:
                                continue
                            except AttributeError:
                                continue
                            answer = rel_year if not answer or rel_year < answer else answer

        return answer

    def _get_data(self):
        data = {}

        url = self._get_search_url()
        if not url:
            self._say(u'Cannot generate request url', log_only=True)
            return data

        self._say(u'fetching URL: {}'.format(url), log_only=True)

        try:
            headers = {
                'User-Agent': 'BeetsPluginAutofix/0.0.2 ( https://github.com/adamjakab/BeetsPluginAutofix )',
            }
            res = requests.get(url, headers=headers)
        except requests.RequestException as err:
            self._say(u'request error: {}'.format(err), log_only=True)
            return data

        if res.status_code == 503:
            # we hit the query limit - https://musicbrainz.org/doc/XML_Web_Service/Rate_Limiting
            time.sleep(1)
            # todo: must re-request (do this better)
            try:
                res = requests.get(url)
            except requests.RequestException as err:
                self._say(u'request error: {}'.format(err), log_only=True)
                return data

        if res.status_code == 404:
            self._say(u'Not found', log_only=True)
            return data

        try:
            data = res.json()
        except ValueError:
            self._say(u'Invalid Response: {}'.format(res.text), log_only=True)

        return data

    def _get_search_url(self):
        url = ""

        mb_artistid = self.item.get("mb_artistid")
        title = self.item.get("title")

        if mb_artistid and title:
            query = 'arid:{arid} AND recording:"{title}"'.format(arid=mb_artistid, title=title)
            url = "{base}recording/?query={qry}&fmt={fmt}".format(base=MB_BASE, qry=query, fmt="json")

        return quote_plus(url, safe=':/&?=')

    def _item_needs_processing(self):
        answer = False

        if not self.item.get("year") or not self.item.get("original_year"):
            answer = True

        return answer

    def needs_item_store(self):
        return self.year_fixed

    def needs_item_write(self):
        return self.year_fixed
