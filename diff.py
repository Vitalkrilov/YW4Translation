#!/bin/python

from L5BTFile import L5BTFile
from myutils import eprint, getFiles
import os
import sys
import json
import pathlib
import argparse



def main(args):
  progName = args[0]
  parser = argparse.ArgumentParser(prog=progName, description='This script diffs two directories and outputs difference in JSON format to stdout.',
epilog=f'''examples:
 $  {progName} -1c -s text_all.src -a text_all data/common/text/ja  #COMMENT: generate diff between "text_all.src" and "text_all" by scanning everything in "data/common/text/ja"
 $  {progName} -c -s ./some/path/text_all.src                       #COMMENT: diff "..text_all.src" with *nothing* => outputs everything that provided files have. so you will be able to translate them manually if you prefer it. just pass edited diff.py to patcher.py script''', formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('input', default=['data/common/text/ja'], help='relative path to file or directory (recursive search) which should be diffed (default: ["data/common/text/ja"])', nargs='*')
  parser.add_argument('-s', '--src-dir', required=True, help='source files that script will use as base: path to text_all\'s root directory where all *.cfg.bin files stored (example: "text_all.src")')
  parser.add_argument('-a', '--alt-dir', help='alternate files that script will compare with base: path to text_all\'s root directory where all *.cfg.bin files stored (example: "text_all")')
  parser.add_argument('-o', '--output', default='-', help='path where we should save diff file (example: "map.json"), you can use "-" to output generated json to stdout (default: stdout)')
  parser.add_argument('-1', '--apply-002-fixes', action='store_true', default=False, help='fix broken files (it works only with Yo-kai Watch 4 v0.0.2 English Translation)')
  parser.add_argument('-c', '--correct-strings', default='00000', help='use *default* (specially for ja2en translation) localize.py tweaks in order to make some changes (like translation) to right-side values (strings); form: 0=disable, 1=enable; sequence: PRF, FUC, Translate, FBS, LOC (check localize.py\'s help for abbr\'s meanings); example: "00010" (default: "00000")')
  args = parser.parse_args(args[1:])

  srcPath = pathlib.PurePath(args.src_dir)
  if not os.path.isdir(srcPath):
    eprint(f'{progName}: error: provided $src-dir is not a directory')
    return 1
  for e in args.input:
    if not os.path.exists(srcPath.joinpath(e)):
      eprint(f'{progName}: error: $src-dir does not contain one of $input values ("{e}")')
      return 1

  if args.alt_dir != None:
    altPath = pathlib.PurePath(args.alt_dir)
    if not os.path.isdir(altPath):
      eprint(f'{progName}: error: provided $alt-dir is not a directory')
      return 1
    for e in args.input:
      if not os.path.exists(altPath.joinpath(e)):
        eprint(f'{progName}: error: $alt-dir does not contain one of $input values ("{e}")')
        return 1

  if args.output != '-':
    if os.path.isfile(args.output):
      if not os.access(args.output, os.W_OK):
        eprint(f'{progName}: error: provided $output is non-writable (must be a path to existing file or its directory should be able to store it)')
        return 1
    else:
      sParent = str(pathlib.PurePath(args.output).parent)
      if not os.path.isdir(sParent) or not os.access(sParent, os.W_OK | os.X_OK):
        eprint(f'{progName}: error: can\'t create a file at $output (must be a path to existing file or its directory should be able to store it)')
        return 1

  if len(args.correct_strings) != 5 or set(args.correct_strings+'01') != {'0', '1'}:
    eprint(f'{progName}: error: given $correct-strings is wrong; check "--help" for more info about this argument')
    return 1

  inputFiles = getFiles(args.src_dir, args.input, '.cfg.bin')

  diff = dict()
  for fnameInput in inputFiles:
    # Getting relative filename
    fname = pathlib.PurePath()
    for e in fnameInput.parts[len(srcPath.parts):]:
      fname = fname.joinpath(e)

    l5bt_file_src = L5BTFile(str(fnameInput))
    l5bt_file_src.load()
    if args.alt_dir != None:
      l5bt_file = L5BTFile(str(altPath.joinpath(fname)))
      l5bt_file.load()

    # Because diff.json uses posix path, yes.
    fname = str(pathlib.PurePosixPath(fname))

    if args.alt_dir != None:
      data = json.loads(l5bt_file.toJSON())
      if args.apply_002_fixes:
        # Manually corrected files corrupted by translators team. All other files have same entries and strings structure. Signatures will be fixed automatically.
        if fname == 'data/common/text/ja/chara_nickname_text.cfg.bin':
          data['strings'] = data['strings'][:1] + data['strings'][2:] # remove unneeded(most-likely, I guess?) entry
        elif fname == 'data/common/text/ja/event/ev01_7500.cfg.bin':
          data['strings'] = data['strings'][:1] + ["Nyaaa, I feel\ndesperate too !"]
        elif fname == 'data/common/text/ja/event/ev20_4810.cfg.bin':
          data['strings'] = data['strings'][:1] + ["I'm not going to let you get away\nwith it, for Manami's sake!"]
        elif fname == 'data/common/text/ja/battle_text.cfg.bin':
          data['strings'] = [' enemy wants to fight!', ' enemies want to fight!','<CMD_STOP_WATCHING_SELECT_PARTY_UP|3>Switch Leader\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_SELECT_ENEMY_UP|3>Switch enemy\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_OVER_LOOK|3>Zoom\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1|4>[CP]Back[C]','<CMD_STOP_WATCHING_GIVEUP>Run Away','<CMD_STOP_WATCHING_SELECT_PARTY_UP|3>Switch Leader\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_SELECT_ENEMY_UP|3>Switch enemy\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_OVER_LOOK|3>Minify\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1|4>[CP]Back[C]','[$gaiji_bt01_s010]Zoom\u3000\u3000\u3000\u3000\u3000[$gaiji_bt10_s020][CP]Return[C]','<CMD_STOP_WATCHING_DECIDE>Select\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1>Back','<CMD_STOP_WATCHING_DECIDE>Use\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1>Back','<CMD_STOP_WATCHING_DECIDE>Select\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1>Back','<CMD_AUTO_BATTLE>','<CMD_STOP_WATCHING>','<CMD_CHAT>Chat\u3000\u3000\u3000<CMD_SETTING_RETIRE>Menu','<CMD_VACUUM>', '<CMD_SKILL>', 'Goriki', 'Onnen', 'Mononoke', 'Tsukumono', 'Uwanosora', 'Omamori', 'Mikakunin', 'Mikado', 'Izana', 'Demon', 'Kaima', 'Strange', 'None', 'Fire', 'Water', 'Thunder', 'Ground', 'Ice', 'Wind', 'Light', 'Dark', 'Average', 'Very Slow', 'Slow', 'Fast', 'Very Fast', 'Irritable', 'Rowdy', 'Calm', 'Indecent', 'Reliable', 'Show-off', 'Kind', 'Dedicated', 'Sloppy', 'Selfish', 'Blunt', 'Serious', '<CMD_SKILL_SELECT|0>', '<CMD_SKILL_SELECT|2>', '<CMD_SKILL_SELECT|1>', '<CMD_SKILL|0>', '<CMD_SKILL|2>', '<CMD_SKILL|1>', '<CMD_PIN_THROW|0>', '<CMD_PIN_THROW|2>', '<CMD_PIN_THROW|1>', '<CMD_AIM|0>', '<CMD_AIM|2>', '<CMD_AIM|1>', '<CMD_NORMAL_ATTACK|0>', '<CMD_NORMAL_ATTACK|2>', '<CMD_NORMAL_ATTACK|1>', '<CMD_VACUUM|0>', '<CMD_VACUUM|2>', '<CMD_VACUUM|1>', '<CMD_REPEAT_SPECIAL_ATTACK_RIGHT|7>', '<CMD_REPEAT_SPECIAL_ATTACK_RIGHT|6>', '<CMD_REPEAT_SPECIAL_ATTACK_DOWN|7>', '<CMD_REPEAT_SPECIAL_ATTACK_DOWN|6>', '<CMD_REPEAT_SPECIAL_ATTACK_UP|7>', '<CMD_REPEAT_SPECIAL_ATTACK_UP|6>', '<CMD_REPEAT_SPECIAL_ATTACK_LEFT|7>', '<CMD_REPEAT_SPECIAL_ATTACK_LEFT|6>', '<CMD_TIMING_SPECIAL_ATTACK_RIGHT|7>', '<CMD_TIMING_SPECIAL_ATTACK_RIGHT|6>', '<CMD_TIMING_SPECIAL_ATTACK_DOWN|7>', '<CMD_TIMING_SPECIAL_ATTACK_DOWN|6>', '<CMD_TIMING_SPECIAL_ATTACK_UP|7>', '<CMD_TIMING_SPECIAL_ATTACK_UP|6>', '<CMD_TIMING_SPECIAL_ATTACK_LEFT|7>', '<CMD_TIMING_SPECIAL_ATTACK_LEFT|6>', '<CMD_ENTER>', '<CMD_ENTER|1>']
        elif fname == 'data/common/text/ja/system_text.cfg.bin': # fix typo (dunno why, but let it be fixed lol)
          for i in range(len(data['strings'])):
            if data['strings'][i] == 'Increase your favourit people':
              data['strings'][i] = 'Increase your favourite people'
              break
        # Fixing newlines broken by translators
        for i in range(len(data['strings'])):
          data['strings'][i] = data['strings'][i].replace('\\N', '\n').replace('\\ N', '\n').replace('\\ n', '\n').replace('\\', '\n').replace('/n', '\n')

    dataSrc = json.loads(l5bt_file_src.toJSON())
    if args.alt_dir == None:
      data = dataSrc

    if args.correct_strings:
      import localize
    for i in range(len(dataSrc['strings'])):
      if dataSrc['strings'][i] != data['strings'][i] or args.alt_dir == None:
        if fname not in diff.keys():
          diff[fname] = dict()

        if args.correct_strings: # Using our tool to correct string further
          s = localize.tryToModify(data['strings'][i], enabledPRF=(args.correct_strings[0]=='1'), enabledFUC=(args.correct_strings[1]=='1'), translation=(args.correct_strings[2]=='1'), enabledFBS=(args.correct_strings[3]=='1'), enabledLOC=(args.correct_strings[4]=='1')) # FUC will be done before TRA because it most-likely could be already translated, yes?..
        else:
          s = data['strings'][i]

        diff[fname][i] = {dataSrc['strings'][i]: s}

  diffOutput = json.dumps(diff, indent=2, ensure_ascii=False)
  if args.output == '-':
    print(diffOutput)
  else:
    with open(args.output, 'w') as f:
      f.write(diffOutput)

if __name__ == '__main__':
  exit(main(sys.argv))
