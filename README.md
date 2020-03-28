[![Build Status](https://travis-ci.org/adamjakab/BeetsPluginAutofix.svg?branch=master)](https://travis-ci.org/adamjakab/BeetsPluginAutofix)
[![Coverage Status](https://coveralls.io/repos/github/adamjakab/BeetsPluginAutofix/badge.svg?branch=master)](https://coveralls.io/github/adamjakab/BeetsPluginAutofix?branch=master)
[![PyPi](https://img.shields.io/pypi/v/beets-autofix.svg)](https://pypi.org/project/beets-autofix/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.txt)

# Autofix (Beets Plugin)

The *beets-autofix* plugin helps you to automate the tasks that you keep repeating to maintain your library. 

It executes the following tasks:
- check missing files and remove them from the library
- run the convert plugin
- run the zero plugin
- run acousticbrainz plugin 
- find genre from lastgenre and if it fails use the `genre_rosamerica`
- use the xtractor plugin to extract low/high level audio data

*NOTE: This plugin is highly unstable and not at all documented! Use it at your own risk*


## Installation
The plugin can be installed via:

```shell script
$ pip install beets-autofix
```

