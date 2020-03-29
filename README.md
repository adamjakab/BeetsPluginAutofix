[![Build Status](https://travis-ci.org/adamjakab/BeetsPluginAutofix.svg?branch=devel)](https://travis-ci.org/adamjakab/BeetsPluginAutofix)
[![Coverage Status](https://coveralls.io/repos/github/adamjakab/BeetsPluginAutofix/badge.svg?branch=devel)](https://coveralls.io/github/adamjakab/BeetsPluginAutofix?branch=devel)
[![PyPi](https://img.shields.io/pypi/v/beets-autofix.svg)](https://pypi.org/project/beets-autofix/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)

# Autofix (Beets Plugin)

The *beets-autofix* plugin helps you to automate the tasks that you keep repeating to maintain your library. 

The plugin is a wrapper around the plugins that you already have in beets. It iterates through the items you have in your library and calls the individual plugins to execute their jobs as they are configured by you.


## Installation
The plugin can be installed via:

```shell script
$ pip install beets-autofix
```


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
  genre_finder:
    enabled: no
  xtractor:
    enabled: no
```

You need to override the default configuration and enable the tasks you want to run.

The `max_exec_time` allows you to interrupt the execution after a certain number of seconds. For no limit set it to 0.


## Tasks
The following tasks are available:

### Missing File Checker (task name: missing_file_checker) [related plugin: None]
This task is not related to any plugin. It will iterate through all library items and check if the file indicated by the `path` attribute exists. If it does not exist, it deletes the library item.


### Year Fixer (task name: year_fixer) [related plugin: [year_fixer](https://github.com/adamjakab/BeetsPluginYearFixer)]
The YearFixer plugin will attempt to fix items with missing `year` or `original_year` attributes missing.


### Conversion (task name: audio_conversion) [related plugin: [convert](https://beets.readthedocs.io/en/stable/plugins/convert.html)]
This plugin is based on the `convert` plugin and triggers the conversion in two cases:

- if the format of the item is does not correspond to the `format` specified in the `convert` plugin configuration
- if the bitrate of the item is greater than the `bitrate` specified in the `convert` plugin configuration

In both cases the audio file will be converted according to the `convert` plugin configuration. The converted audio file will be attached to the library item whilst the original audio file will be deleted.

### Tag Cleaner (task name: tag_cleaner) [related plugin: [zero](https://beets.readthedocs.io/en/stable/plugins/zero.html)]
This task works with the `zero` plugin and triggers only if in the configuration you use the `fields` configuration option (it does not work with the `keep_fields` option for now). If any of those fields are found to be non-empty, the item will be passed to the `zero` plugin for processing. 


### Acoustic Brainz Data Fetcher (task name: ab_data_fetcher) [related plugin: [acousticbrainz](https://beets.readthedocs.io/en/stable/plugins/acousticbrainz.html)]




- run acousticbrainz plugin 
- find genre from lastgenre and if it fails use the `genre_rosamerica`
- use the xtractor plugin to extract low/high level audio data





