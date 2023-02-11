# Yo-kai Watch 4++ Full Text Translation

This repository contains **finished mod** and my scripts (if you want to do it manually). Translated all strings (not sprites).

# [!] DISCLAIMER [!]

This project is **not** associated with any companies related to this game, etc.

Translation sometimes may contain uncensored words or have slightly different from original meanings. But it's just issue of translation software.

## How to install translation:

Download latest release from [***releases***](https://github.com/Vitalkrilov/YW4Translation/releases/). [Link of latest release (if not working, find manually there)](https://github.com/Vitalkrilov/YW4Translation/releases/download/v1.0/yw4_translation_en-1.0.zip).

### Ryujinx:

In Ryujinx data directory (`/home/{USERNAME}/.config/Ryujinx/` on Linux; `C:\Users\{USERNAME}\AppData\Roaming\Ryujinx\` on Windows):

Most likely you need to put `romfs` directory from archive in `{...Ryujinx}/mods/contents/010086c00af7c000/`

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

- Adding extra newlines to avoid rendering issues (game can draw text outside boxes);

- Fix some story markers (I hope it's just names?) in text (translation software breaks some of them);

- Somehow (currently have no idea how...) fix some markup of texts (colors). It's not easy because translation software does not allow to add some tags, etc.;

- Retranslating via DeepL api (I don't have access to it; 2 api keys is required to fully translate in a few hours or 1 api key but with delay in 1 month);

- Translating to any other language?

They are not critical at all (I tested it for being playable without problems). Maybe I will do some of them later if I will have free time.

## Just some notes about how to do something or for what some files is needed:

### Some guides:

Install `googletrans` python module:

`$ pip install googletrans`

This tool is designed to be used on Linux (or other OSes which have bash-like shells and python (tested on 3.10).

You should enable globstar to use `**` in paths:

`$ shopt -s globstar`

**1**) Unpack official CPK-file using YaCpkTool (or something else) to `text_all`;

**2**) Copy all content also to `text_all.src`;

**3---N-3**) Check bash script (scriptedThing.sh), you can run commands manually and edit them if you need;

**N-2**) Use files `work/cpk_list.cfg.bin` and `work/text_all.cpk` (do not forget to pack it back from `work/text_all`);

**N-1**) ???

**N**) PROFIT

### Files:

- `data/off`: contains original files, got from my copy of Yo-kai Watch 4++ and 11 DLC using Ryujinx 1.1.0-ldn3.0.1;

- `data/off/cpk_list.cfg.bin.json`: contains sizes (converted to json);

- `data/off/text_all.cpk`: contains all translation files;

- `data/diff002.json`: diff (only directory of Japanese language) between original translation files and Yo-kai Watch 4 English Translation Mod Release 0.0.2 (I guess it was on this link: [gbatemp.net page](https://gbatemp.net/threads/wip-yo-kai-watch-4-switch-english-translation-project.580560/)). During diff it was fixed (check code if you really need to know what) but it was checked manually for correctness;

- `data/trwork (*).json`: different finished/unfinished translations. google translation is almost finished and can be finished just by passing it to my tool (I've already done this and created final `map.json`);

- `data/map.json`: final `map.json` used to assemble into my translation (uses original files, patched with fixed Yo-kai Watch 4 English Translation Mod Release 0.0.2, all other translated using Google Translate, some global fixes);

- `data/misc/YACpkTool (from discord).zip`: program I used to pack/unpack .cpk-files. I found it on discord channel of Yo-kai Watch 4 English Translation Project.

***WARNING***: I stored it here just because it works and it still will be here if original will be deleted but **I don't know if it contains virus / etc.**, so if you need program  -- better go to official YACpkTool github repo.

Purpose of every script is stated in it's beginning.
