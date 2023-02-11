#!/bin/python

# This script diffs two folders. And outputs difference in JSON format to stdout.

# <config>
DIFFING002TRANSLATION = True # if True then it will fix corrupted files from YW4 translation 0.0.2
ADAPTATE002TRANSLATION = True # if True then it will also fix broken newlines too
APPLY_REPLACES_IMPROVEMENT = True # if True then it will use replaces.py in order to make some changes (like translation) to right-side(values) strings
# </config>

from L5BTFile import L5BTFile
import sys
import json



def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
  if len(sys.argv) < 4:
    eprint(f'Usage: {sys.argv[0]} input_source_files_dirname input_secondary_files_dirname input_source_files...')
    eprint(f'Warning: every input_source_file should use $input_source_files_dirname (and $input_secondary_files_dirname for input secondary files) as root directory and these two directories should be in same directory')
    eprint(f'Examples: {sys.argv[0]} text_all.src text_all text_all.src/data/common/text/ja/**/*.cfg.bin')
    eprint('         or')
    eprint(f'          {sys.argv[0]} text_all.src text_all ./some/path/text_all.src/data/common/text/ja/**/*.cfg.bin')
    exit(1)

  diff = dict()

  for fname in sys.argv[3:]:
    if ')/////(' in fname:
      eprint(f'{sys.argv[0]}: error: wrong path ["{fname}"]')
      continue
    tmpCnt = ('/' + fname).count(f'/{sys.argv[1]}/')
    if tmpCnt != 1:
      if tmpCnt == 0:
        eprint(f'{sys.argv[0]}: error: $input_source_files_dirname is not in input_source_file\'s path')
      else:
        eprint(f'{sys.argv[0]}: error: please do not use $input_source_files_dirname which already is in the path before target dir')
      exit(1)
    fname = ('/' + fname).replace(f'/{sys.argv[1]}/', '/)/////(/')[1:] # to be able to use shell's globstar
    l5bt_file = L5BTFile(fname.replace(')/////(', sys.argv[2]))
    l5bt_file.load()
    l5bt_file_src = L5BTFile(fname.replace(')/////(', sys.argv[1]))
    l5bt_file_src.load()
    fname = fname[fname.find(')/////(/')+len(')/////(/'):]

    data = json.loads(l5bt_file.toJSON())

    if DIFFING002TRANSLATION:
      # Manually corrected files corrupted by translators team. All other files have same entries and strings structure. Signatures will be fixed automatically.
      if fname == 'data/common/text/ja/chara_nickname_text.cfg.bin':
        data['strings'] = data['strings'][:1] + data['strings'][2:] # remove unneeded(most-likely, I guess?) entry
      elif fname == 'data/common/text/ja/event/ev01_7500.cfg.bin':
        data['strings'] = data['strings'][:1] + ["Nyaaa, I feel\ndesperate too !"]
      elif fname == 'data/common/text/ja/event/ev20_4810.cfg.bin':
        data['strings'] = data['strings'][:1] + ["I'm not going to let you get away\nwith it, for Manami's sake!"]
      elif fname == 'data/common/text/ja/battle_text.cfg.bin':
        data['strings'] = [' enemy wants to fight!', ' enemies want to fight!','<CMD_STOP_WATCHING_SELECT_PARTY_UP|3>Switch Leader\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_SELECT_ENEMY_UP|3>Switch enemy\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_OVER_LOOK|3>Zoom\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1|4>[CP]Back[C]','<CMD_STOP_WATCHING_GIVEUP>Run Away','<CMD_STOP_WATCHING_SELECT_PARTY_UP|3>Switch Leader\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_SELECT_ENEMY_UP|3>Switch enemy\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_OVER_LOOK|3>Minify\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1|4>[CP]Back[C]','[$gaiji_bt01_s010]Zoom\u3000\u3000\u3000\u3000\u3000[$gaiji_bt10_s020][CP]Return[C]','<CMD_STOP_WATCHING_DECIDE>Select\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1>Back','<CMD_STOP_WATCHING_DECIDE>Use\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1>Back','<CMD_STOP_WATCHING_DECIDE>Select\u3000\u3000\u3000\u3000\u3000<CMD_STOP_WATCHING_RETURN_1>Back','<CMD_AUTO_BATTLE>','<CMD_STOP_WATCHING>','<CMD_CHAT>Chat\u3000\u3000\u3000<CMD_SETTING_RETIRE>Menu','<CMD_VACUUM>', '<CMD_SKILL>', 'Goriki', 'Onnen', 'Mononoke', 'Tsukumono', 'Uwanosora', 'Omamori', 'Mikakunin', 'Mikado', 'Izana', 'Demon', 'Kaima', 'Strange', 'None', 'Fire', 'Water', 'Thunder', 'Ground', 'Ice', 'Wind', 'Light', 'Dark', 'Average', 'Very Slow', 'Slow', 'Fast', 'Very Fast', 'Irritable', 'Rowdy', 'Calm', 'Indecent', 'Reliable', 'Show-off', 'Kind', 'Dedicated', 'Sloppy', 'Selfish', 'Blunt', 'Serious', '<CMD_SKILL_SELECT|0>', '<CMD_SKILL_SELECT|2>', '<CMD_SKILL_SELECT|1>', '<CMD_SKILL|0>', '<CMD_SKILL|2>', '<CMD_SKILL|1>', '<CMD_PIN_THROW|0>', '<CMD_PIN_THROW|2>', '<CMD_PIN_THROW|1>', '<CMD_AIM|0>', '<CMD_AIM|2>', '<CMD_AIM|1>', '<CMD_NORMAL_ATTACK|0>', '<CMD_NORMAL_ATTACK|2>', '<CMD_NORMAL_ATTACK|1>', '<CMD_VACUUM|0>', '<CMD_VACUUM|2>', '<CMD_VACUUM|1>', '<CMD_REPEAT_SPECIAL_ATTACK_RIGHT|7>', '<CMD_REPEAT_SPECIAL_ATTACK_RIGHT|6>', '<CMD_REPEAT_SPECIAL_ATTACK_DOWN|7>', '<CMD_REPEAT_SPECIAL_ATTACK_DOWN|6>', '<CMD_REPEAT_SPECIAL_ATTACK_UP|7>', '<CMD_REPEAT_SPECIAL_ATTACK_UP|6>', '<CMD_REPEAT_SPECIAL_ATTACK_LEFT|7>', '<CMD_REPEAT_SPECIAL_ATTACK_LEFT|6>', '<CMD_TIMING_SPECIAL_ATTACK_RIGHT|7>', '<CMD_TIMING_SPECIAL_ATTACK_RIGHT|6>', '<CMD_TIMING_SPECIAL_ATTACK_DOWN|7>', '<CMD_TIMING_SPECIAL_ATTACK_DOWN|6>', '<CMD_TIMING_SPECIAL_ATTACK_UP|7>', '<CMD_TIMING_SPECIAL_ATTACK_UP|6>', '<CMD_TIMING_SPECIAL_ATTACK_LEFT|7>', '<CMD_TIMING_SPECIAL_ATTACK_LEFT|6>', '<CMD_ENTER>', '<CMD_ENTER|1>']
      if ADAPTATE002TRANSLATION:
        # Fixing newlines broken by translators
        for i in range(len(data['strings'])):
          data['strings'][i] = data['strings'][i].replace('\\N', '\n').replace('\\ N', '\n').replace('\\ n', '\n').replace('\\', '\n')

    dataSrc = json.loads(l5bt_file_src.toJSON())

    if APPLY_REPLACES_IMPROVEMENT:
      import replaces
    for i in range(len(data['strings'])):
      if data['strings'][i] != dataSrc['strings'][i]:
        if fname not in diff.keys():
          diff[fname] = dict()

        # Using our tool to correct string further
        if APPLY_REPLACES_IMPROVEMENT:
          data['strings'][i] = replaces.modify(data['strings'][i])

        diff[fname][i] = {dataSrc['strings'][i]: data['strings'][i]}

  print(json.dumps(diff, indent=2))
