# Yo-kai Watch 4++ Full Text Translation

This repository contains **finished mod** and my scripts (if you want to do it manually). Translated all strings (not sprites).

Releases work on latest version (v2.2.0 YW4++). You can manually build this mod if you have different game version (check Guides below).

# [!] DISCLAIMER [!]

This project is **not** associated with any companies related to this game, etc.

Translation sometimes may contain uncensored words or have slightly different from original meanings. But it's just issue of translation software.

## How to install translation:

[My Telegram channel](https://t.me/vitalkrylov) contains the video of mod installation on Ryujinx.

Download latest release from [***releases***](https://github.com/Vitalkrilov/YW4Translation/releases/). [Link of latest release (if not working, find manually there)](https://github.com/Vitalkrilov/YW4Translation/releases/download/v1.0/yw4_translation_en-1.0.zip).

### Ryujinx:

In Ryujinx data directory (`/home/{USERNAME}/.config/Ryujinx/` on Linux; `C:\Users\{USERNAME}\AppData\Roaming\Ryujinx\` on Windows):

Most likely you need to put `romfs` directory from archive in `{...Ryujinx}/mods/contents/010086c00af7c000/`

### Yuzu:

As I've seen on Reddit, someone tested, so my mod works on it. Obviously, installation is very similar to Ryujinx (just check any video guide about installing mods on this emulator(s)).

### Modded switch:

You should have CFW switch (modded). I found this random video about installing mods: https://www.youtube.com/watch?v=ffxw7QJokxk

You can download any mod. Unpack it, rename {titleID} (main folder in archive) to Yo-kai Watch 4 titleID. And you will need to replace that mod's files with my mod's files. Then pack it back. And install. It's simple, I think (just look on mod's structure of directories and you will find out).

### Others:

Probably should be done same as with Ryujinx. In provided archive there is just `romfs` directory. If you need, you can download Yo-kai Watch 4 English Translation Mod Release 0.0.2 and check guides there, find difference and replace files (it is easy...).

## LICENSE

Check `LICENSE` file

TL;DR. Do everything you want but do not forget to also mention original creator of this project with a link to this github repo (and, if you use 0.0.2 part, Yo-kai Watch 4 English Translation Mod Team too).

## Authors

This repo's scripts, provided baked data, fully translated texts (except manual translation part [optional; check after])

- Vitaliy K. (GH: [@Vitalkrilov](https://github.com/Vitalkrilov))

Manually translated part which I got from mod (why not to have some truly correct translation if it's exists):

- Yo-kai Watch 4 English Translation Mod Team (check [gbatemp.net page](https://gbatemp.net/threads/wip-yo-kai-watch-4-switch-english-translation-project.580560/))

## Is there something which could be also done?

Yep, like:

- Translating with removed newlines, add them after translation (translation will be more correct);

  Problem: we can't know whether newline is a separator of some sentence or not.

- Fix some markup of texts (colors). It's not easy because translation software does not allow to add some tags, etc.;

  Possible solution: use DeepL, it can recognize some tags which will not break meaning of a sentence.

- Retranslating via DeepL api (I don't have access to it; 2 api keys is required to fully translate in a few hours or 1 api key but with delay in 1 month);

  It could improve translation (at least, I hope so).

- Translating to any other language

  Probably, with 1.1+ version it can be done by just specifying language when you run scripts on your own.

- *Somehow* understand when line ends so make a newline (if available).

  Because, currently, text may be out of dialogue box' bounds.

- *Somehow* replace game's tags to something which will save sentence's meaning during translation.

  Example: "[$player] entered the room." -> "[1] entered the room." -> (translation with "[1]" inside which is not noun) -> ... | This will break true meaning of needed sentence...

They are not critical at all (I tested it (currently, prebuilt 1.0 tested) for being playable without problems). Maybe I will do some of them later if I will have free time.

## Just some notes about how to do something or for what some files is needed:

### Some guides:

#### Requirements

- Tool to (un)pack .CPK-files. (check a guide which is ~~two blocks down~~ below).

##### Python-related

If you need to use Google translator, then install `googletrans` python module:

`$ pip install googletrans`

If you need to use Yandex translator, then install `requests` python module:

`$ pip install requests`

#### Pack / unpack `text_all.cpk` examples

After v1.0 I used [YACpkTool v1.1b from GitHub](https://github.com/Brolijah/YACpkTool/releases/tag/v1.1b). So better you use it instead of the tool in `data/misc` of v1.0 tag (if official repo's tool can't help you, then try it...).

Unpack:

`$ YACpkTool.exe -X -o work/text_all.src -i data/origs/text_all.cpk`

Pack:

`$ YACpkTool.exe -P --codec LAYLA --align 2048 -i work/text_all -o work/text_all.cpk`

#### Easy quick-to-use:

**1**) Unpack official CPK-file using YaCpkTool (or something else) to `text_all`;

**2**) Copy all content also to `text_all.src`;

**3---N-3**) Check shell script (`scriptedThing.sh`), you can run commands manually and edit them if you need;

**N-2**) Use files `work/cpk_list.cfg.bin` and `work/text_all.cpk` (do not forget to pack it back from `work/text_all`);

**N-1**) ???

**N**) PROFIT

#### Hints about rebuilding for other versions

If you need to get this mod working on your version, you will need to unpack your game files. Get `text_all.cpk` from it, get `cpk_list.cfg.bin` from it.

You can run `patcher.py` plainly (like `scriptedThing.sh` does firstly). This will add strings which differ from my mod's game version's strings. So after this you will need to translate only them using script (script will find last translated string so it would not translate from the beginning).

Then you'll need to update `cpk_list.cfg.bin`. Since my script-updater supports json version, you will need to load .cfg.bin-version (using L5TBFile.py) and export it to json.

### Files:

- `data/origs`: contains original files, got from my copy of Yo-kai Watch 4++ and 11 DLC using Ryujinx 1.1.0-ldn3.0.1;

- `data/origs/cpk_list.cfg.bin.json`: contains sizes (converted to json);

- `data/origs/text_all.cpk`: contains all translation files;

- `data/diffs/diff002.json`: diff (only directory of Japanese language) between original translation files and Yo-kai Watch 4 English Translation Mod Release 0.0.2 (I guess it was on this link: [gbatemp.net page](https://gbatemp.net/threads/wip-yo-kai-watch-4-switch-english-translation-project.580560/)). During diff it was fixed (check code if you really need to know what) but it was checked manually for correctness;

- `data/transmaps`: different finished/unfinished translations:

For example:

- `data/transmaps/english/google/full_release.map.json`: it's a google translation I used as final `map.json` for assembling into my translation (uses original files, patched with `Yo-kai Watch 4 English Translation Mod Release 0.0.2` fixed by me, all other texts translated using Google Translate, some global fixes);

By the way, map.json is an **ordered** dictionary (mostly, because I use last translated position in it; it can be done by other way, but I think it's okay how it works now).

Purpose of every python script is stated in it's help (you can run them without arguments to get usage info or run with "--help" argument in order to get help). Also you can (yeah...) just open `scriptedThing.sh` and check in which order they should be called, what they use, it's a practical explanation, I guess.
