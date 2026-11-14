# Adding or updating a plugin

1. Fork this repository and make a folder `plugins/<id>/`. The id is 2 to 40 characters of
   `a-z`, `0-9` and `-`, and it is the folder's name the plugin gets in the game
   (`plugins/<id>/main.lua`).
2. Put the plugin into it: `main.lua` and whatever it `require`s or reads (`.lua`, `.json`,
   `.txt`, `.md`, `.csv`, `.png`, `.jpg`, `.ogg`, `.wav`, `.ttf`, `.otf`; at most 2 MB a file,
   10 MB in all). No programs, libraries or archives.
3. Add `plugins/<id>/plugin.json`:

   ```json
   {
     "id": "my-plugin",
     "name": "My plugin",
     "author": "Your name",
     "version": "1.0.0",
     "description": "One line: what it does for the player.",
     "license": "MIT",
     "tags": ["driving"],
     "homepage": "https://github.com/you/my-plugin",
     "min_game": "0.3.55"
   }
   ```

   `homepage` and `min_game` may be left out. `license` is the SPDX id of an open source
   licence (`tools/build_catalog.py` lists the ones taken): everyone can read and improve what
   runs in their game.
4. Run `python3 tools/build_catalog.py` and commit `catalog.json` with the plugin. Check
   `luac -p plugins/<id>/*.lua` (Lua 5.4).
5. Open a pull request. A maintainer reads the code before it is merged; the checks must pass.

An update is a pull request that changes the files and raises `version`. The launcher offers
it to everyone who installed the plugin; their settings and saved data (`plugins/<id>/data/`)
stay.

## What is not taken

- Code that is hidden (obfuscated, minified, encoded) or downloads code to run.
- Anything that sends the player's data somewhere without saying so in its description.
- Content of OMSI 2 or of other people's mods (textures, sounds, scripts) without their
  permission.
- Plugins that only work with paid add-ons are fine; say so in the description.
