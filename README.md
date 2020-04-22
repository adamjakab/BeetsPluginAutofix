[![Build Status](https://travis-ci.org/adamjakab/BeetsPluginAutofix.svg?branch=master)](https://travis-ci.org/adamjakab/BeetsPluginAutofix)
[![Coverage Status](https://coveralls.io/repos/github/adamjakab/BeetsPluginAutofix/badge.svg?branch=master)](https://coveralls.io/github/adamjakab/BeetsPluginAutofix?branch=master)
[![PyPi](https://img.shields.io/pypi/v/beets-autofix.svg)](https://pypi.org/project/beets-autofix/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/beets-autofix.svg)](https://pypi.org/project/beets-autofix/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)

# Autofix (Beets Plugin)

The *beets-autofix* plugin helps you to automate the tasks that you keep repeating to maintain your library. 

The plugin is a wrapper around the plugins that you already have in beets. It iterates through the items you have in your library and calls the individual plugins to execute their jobs as they are configured by you.


## Installation
The plugin can be installed via:

```shell script
$ pip install beets-autofix
```


## Usage

Invoke the plugin as:

    $ beet autofix [options] [QUERY...]


The following command line options are available:

**--max_exec_time=MAX_EXEC_TIME [-m MAX_EXEC_TIME]**: Interrupt the execution after this number of seconds.

**--version [-v]**: Display the version number of the plugin. Useful when you need to report some issue and you have to state the version of the plugin you are using.


## Configuration
By default all tasks are disabled:

```yaml
max_exec_time: 0
tasks:
  missing_file_checker:
    enabled: no
  year_fixer:
    enabled: no
  audio_conversion:
    enabled: no
  tag_cleaner:
    enabled: no
  ab_data_fetcher:
    enabled: no
  xtractor:
    enabled: no
  genre_finder:
    enabled: no
```

You need to override the default configuration and enable the tasks you want to run.

The `max_exec_time` allows you to interrupt the execution after a certain number of seconds. For no limit set it to 0.


## Tasks
The following tasks are available:

### Missing File Checker (task name: missing_file_checker) [related plugin: None]
This task is not related to any plugin. It will iterate through all library items and check if the file indicated by the `path` attribute exists. If it does not exist, it deletes the library item.


### Year Fixer (task name: year_fixer) [related plugin: [yearfixer](https://github.com/adamjakab/BeetsPluginYearFixer)]
The YearFixer plugin will attempt to fix items with missing `year` or `original_year` attributes missing. The particularity of the `yearfixer` plugin is that given a specific release, to look for the `original_year` attribute, it will search for all recordings of the same title (by the same artist) in the MB database and chose the earliest year that song has been released.


### Conversion (task name: audio_conversion) [related plugin: [convert](https://beets.readthedocs.io/en/stable/plugins/convert.html)]
This plugin is based on the `convert` plugin and triggers the conversion in two cases:

- if the format of the item is does not correspond to the `format` specified in the `convert` plugin configuration
- if the bitrate of the item is greater than the `bitrate` specified in the `convert` plugin configuration

In both cases the audio file will be converted according to the `convert` plugin configuration. The converted audio file will be attached to the library item whilst the original audio file will be deleted.

### Tag Cleaner (task name: tag_cleaner) [related plugin: [zero](https://beets.readthedocs.io/en/stable/plugins/zero.html)]
This task works with the `zero` plugin and triggers only if in the configuration you use the `fields` configuration option (it does not work with the `keep_fields` option for now). If any of those fields are found to be non-empty, the item will be passed to the `zero` plugin for processing. 


### AcousticBrainz Data Fetcher (task name: ab_data_fetcher) [related plugin: [acousticbrainz](https://beets.readthedocs.io/en/stable/plugins/acousticbrainz.html)]
This task will check if any of the following attributes are missing from the library item and will call the acousticbrainz plugin to fetch such data from the acousticbrainz database. The task will then set the values for the missing attributes. If the `force` configuration option is set to `yes` in the configuration of the `acousticbrainz` plugin then all attributes will be set. 

The attributes checked and set are: `average_loudness`, `bpm`, `danceable`, `gender`, `genre_rosamerica`, `voice_instrumental`, `mood_acoustic`, `mood_aggressive`, `mood_electronic`, `mood_happy`, `mood_party`, `mood_relaxed`, `mood_sad` (some more to come soon)


### Xtractor(task name: xtractor) [related plugin: [xtractor](https://github.com/adamjakab/BeetsPluginXtractor)]
This task and the related plugin works on exactly the same attributes as the ones listed in the AcousticBrainz Data Fetcher task. The difference is that the `xtractor` plugin does not rely on external databases but uses the Essentia extractor binaries to extract such data from your audio files. 


### Genre Finder (task name: genre_finder) [related plugin: [lastgenre](https://beets.readthedocs.io/en/stable/plugins/lastgenre.html)]
This task will call the `lastgenre` plugin to find out the genre of a specific song. If that fails, it will fall back to the `genre_rosamerica` attribute estimated by the Essentia high level extractor and map the genre based on this table:

```text
    "cla" -> "classical"
    "dan" -> "dance"
    "hip" -> "hip-hop"
    "jaz" -> "jazz"
    "pop" -> "pop"
    "rhy" -> "rhythm and blues"
    "roc" -> "rock"
    "spe" -> "speech"
```

## Issues
- If something is not working as expected please use the Issue tracker.
- If the documentation is not clear please use the Issue tracker.
- If you have a feature request please use the Issue tracker.
- In any other situation please use the Issue tracker.


## Other plugins by the same author

- [beets-goingrunning](https://github.com/adamjakab/BeetsPluginGoingRunning)
- [beets-xtractor](https://github.com/adamjakab/BeetsPluginXtractor)
- [beets-yearfixer](https://github.com/adamjakab/BeetsPluginYearFixer)
- [beets-autofix](https://github.com/adamjakab/BeetsPluginAutofix)
- [beets-describe](https://github.com/adamjakab/BeetsPluginDescribe)
- [beets-bpmanalyser](https://github.com/adamjakab/BeetsPluginBpmAnalyser)
- [beets-template](https://github.com/adamjakab/BeetsPluginTemplate)


## Final Remarks
Enjoy!
