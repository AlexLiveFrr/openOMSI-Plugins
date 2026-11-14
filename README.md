# openOMSI Plugins

[![Check plugins](https://github.com/openOMSI-org/openOMSI-Plugins/actions/workflows/check.yml/badge.svg)](https://github.com/openOMSI-org/openOMSI-Plugins/actions/workflows/check.yml)

The catalog of Lua plugins for [openOMSI](https://github.com/openOMSI-org/openOMSI). Every
plugin here is open source and read by a maintainer before it is merged, so anyone can see
what runs in their game.

[Install a plugin](#install-a-plugin) | [Publish a plugin](CONTRIBUTING.md) |
[Plugin API](https://github.com/openOMSI-org/openOMSI/blob/main/docs/PLUGINS.md)

## Install a plugin

1. Open the launcher and go to **Content**, then **Plugins**, then **Browse**.
2. Pick a plugin and install it with one click. It goes into the game's `plugins` folder.

The launcher offers an update when the plugin's version in this catalog goes up.

## Publish a plugin

Plugins come in through pull requests. [CONTRIBUTING.md](CONTRIBUTING.md) describes the folder
layout, `plugin.json`, the checks and what is not taken. To learn how to write one, read
[docs/PLUGINS.md](https://github.com/openOMSI-org/openOMSI/blob/main/docs/PLUGINS.md) in the
game's repository, or start from [speed-warning](plugins/speed-warning), a small example with
settings.

## Repository layout

| Path | Contents |
| --- | --- |
| `plugins/<id>/` | One plugin: `main.lua`, its other files and `plugin.json` |
| `catalog.json` | Every plugin with the size and SHA-256 of each of its files |
| `tools/build_catalog.py` | Checks the plugins and writes `catalog.json` |

## How it works

- `catalog.json` is made by `python3 tools/build_catalog.py`. The checks fail when it is out
  of date.
- The launcher reads `catalog.json` from the `main` branch, downloads a plugin's files from the
  same branch, and installs them only when every size and SHA-256 matches.
- Plugins are installed into `plugins/<id>/` of the game's content folder. An update keeps
  `plugins/<id>/data/`, the plugin's settings and saved data.

## Licence

The tools and the files of this repository are AGPL-3.0-only ([LICENSE](LICENSE)). Each plugin
has the licence its `plugin.json` names.
