#!/bin/python

# This script generates $map_file on first run. When everything else is done, you should use it to patch $diff_file and $map_file to original files.

from L5BTFile import L5BTFile
import sys
import os
import re
import json



def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

if __name__ == '__main__':
  if len(sys.argv) < 6:
    eprint(f'Usage: {sys.argv[0]} map_file diff_file input_files_dirname output_files_dirname input_files...')
    eprint(f'Warning: every input_file should use $input_files_dirname (and $output_files_dirname for output files) as root directory and these two directories should be in same directory')
    eprint(f'Note: if you don\'t want to provide $diff_file, then just use \'\' as an argument')
    eprint(f'Note: if you want to generate $map_file and don\'t want to write to output file, then use \'\' in $output_files_dirname')
    eprint(f'Examples: {sys.argv[0]} map.json diff.json text_all.src text_all text_all.src/data/common/text/ja/**/*.cfg.bin')
    eprint(f'         or')
    eprint(f'          {sys.argv[0]} map.json \'\' text_all text_all ./some/path/text_all/data/common/text/ja/**/*.cfg.bin')
    eprint(f'         or')
    eprint(f'          {sys.argv[0]} map.json \'\' text_all \'\' some/path/text_all/data/common/text/ja/**/*.cfg.bin')
    exit(1)

  # Replaces '[a/b]' to 'a'
  matcher = re.compile(r'\[(?:(?![\]/]).)*?/(?:(?![\]]).)*?\]')
  def purify(text):
    global matcher
    for e in matcher.findall(text):
      text = text.replace(e, e[1:-1].split('/')[0], 1)
    return text

  # NOTE: 0x3000 symbol is ignored but you might want to get rid of it to (if so then just use replaces.py where you will need to add {'\u3000': ' '})
  def hasJPChars(text):
    for c in text:
      if ord(c) > 0x3000:
        return c
    return False

  if os.path.isfile(sys.argv[1]):
    d = json.loads(open(sys.argv[1]).read())
    translErrorLog = []
    registerTranslationErrors = True
  else:
    d = dict()
    registerTranslationErrors = False

  if sys.argv[2] != '' and os.path.isfile(sys.argv[2]):
    diff = json.loads(open(sys.argv[2]).read())
  else:
    diff = dict()

  loglevel = 0b000 # only basic info | additional info | debug info
  for fname in sys.argv[5:]:
    if ')/////(' in fname:
      eprint(f'{sys.argv[0]}: error: wrong path ["{fname}"]')
      continue
    tmpCnt = ('/' + fname).count(f'/{sys.argv[3]}/')
    if tmpCnt != 1:
      if tmpCnt == 0:
        eprint(f'{sys.argv[0]}: error: $input_files_dirname is not in input_file\'s path')
      else:
        eprint(f'{sys.argv[0]}: error: please do not use $input_files_dirname which already is in the path before target dir')
      exit(1)
    fname = ('/' + fname).replace(f'/{sys.argv[3]}/', '/)/////(/')[1:] # to be able to use shell's globstar
    l5bt_file = L5BTFile(fname.replace(')/////(', sys.argv[3]))
    if loglevel & 0b100: print(f'{sys.argv[0]}: provided file "{l5bt_file.filename}"')
    if loglevel & 0b010: print(f'{sys.argv[0]}: loading file...', end='')
    l5bt_file.load()
    if loglevel & 0b010: print(' Done!')
    l5bt_file.filename = fname.replace(')/////(', sys.argv[4])
    fname = fname[fname.find(')/////(/')+len(')/////(/'):]

    # Patching file using provided diff.json
    if fname in diff.keys():
      for k in diff[fname].keys():
        if l5bt_file.labels[int(k)].text != list(diff[fname][k].keys())[0]:
          eprint(f'{sys.argv[0]}: warning: failed to patch {fname}:{k} (strings are different)')
          continue
        l5bt_file.labels[int(k)].text = list(diff[fname][k].values())[0]
        if loglevel & 0b001: print(f'{sys.argv[0]}: patched {fname}:{k}')

    # Applying/generating map.json if we need to do this
    hasJapaneseCharacters = False
    for e in l5bt_file.labels:
      c = hasJPChars(e.text)
      if c != False:
        if loglevel & 0b001: print(f'{sys.argv[0]}: Japanese character detected (reason: \'{c}\')')
        hasJapaneseCharacters = True
        break
    if hasJapaneseCharacters:
      if loglevel & 0b010: print(f'{sys.argv[0]}: modifying texts...', end='')

      if loglevel & 0b001: print(f'{sys.argv[0]}: texts in Japanese:')
      for i in range(len(l5bt_file.labels)):
        s = l5bt_file.labels[i].text
        if hasJPChars(s) != False:
          # All modifications should be done here:
          if purify(s) in d.keys():
            l5bt_file.labels[i].text = d[purify(s)]
          else:
            if registerTranslationErrors:
              if loglevel & 0b001:
                transErrTxt = f'{sys.argv[0]}: error translating: "' + s.replace('\n', '\\n') + '"'
                eprint(transErrTxt)
              translErrorLog.append(transErrTxt+'\n')
            d[purify(s)] = purify(s)

          if loglevel & 0b001:
            if s != l5bt_file.labels[i].text:
              print(' + "' + s.replace('\n', '\\n') + '" -> "' + l5bt_file.labels[i].text.replace('\n', '\\n') + '"')

      if loglevel & 0b010: print(' Done!')

    if sys.argv[4] != '':
      if loglevel & 0b010: print(f'{sys.argv[0]}: saving file...', end='')
      l5bt_file.save()
      if loglevel & 0b010: print(' Done!')

  f=open(sys.argv[1], 'w')
  f.write(json.dumps(d, indent=2))
  f.close()

  if registerTranslationErrors and len(translErrorLog):
    eprint('Translation errors:')
    for e in translErrorLog:
      eprint(' - ' + e)
