#!/bin/python

from L5BTFile import L5BTFile
from myutils import eprint, hasJPChars, getFiles
import os
import sys
import json
import argparse
import pathlib



def main(args):
  progName = args[0]
  parser = argparse.ArgumentParser(prog=progName, description='This script is used to generate map.json or to patch translation files with map.json and diff.json.',
epilog=f'''examples:
 $  {progName} -i text_all.src -m map.json -d diff.json -o text_all  #COMMENT: use "map.json" and "diff.json" to patch data from "text_all.src" and save to "text_all"
 $  {progName} -f -i text_all -m map.json -M map.json -o text_all       #COMMENT: use "map.json" to patch data in "text_all" (modifying it) and update "map.json" (if there is something not inside)
 $  {progName} -f -i text_all -M map.json data/common/text/ja           #COMMENT: use data of "text_all" to generate "map.json", explicitly defining $input
 $  {progName} -i text_all                                           #COMMENT: dry run to check if files are not corrupted (because L5BTFile.py cares about it)
 $  {progName} -i text_all -d diff.json -o text_all                  #COMMENT: apply "diff.json" to "text_all" (if you want to translate manually by editing diff.json)''', formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('input', default=['data/common/text/ja'], help='relative path to files/directories (recursive search) where we should search for files (default: ["data/common/text/ja"])', nargs='*')
  parser.add_argument('-i', '--input-root', required=True, help='path to text_all\'s root directory where all *.cfg.bin files stored (example: "text_all.src")')
  parser.add_argument('-o', '--output-root', help='path to text_all\'s root directory where we should save patched files (example: "text_all")')
  parser.add_argument('-m', '--input-map', help='path to translation map file to read from (example: "map.json"), you can use "-" to read json from stdin')
  parser.add_argument('-M', '--output-map', help='path to translation map file to write to (example: "map.json"), you can use "-" to output generated json to stdout')
  parser.add_argument('-d', '--diff-file', help='path to translation diff file (example: "diff.json")')
  parser.add_argument('-c', '--current-name', default='$transrun.py/current$', help='a keyword to use in translation map to save translation progress (default: "$transrun.py/current$")')
  parser.add_argument('-f', '--fix-original-files', action='store_true', default=False, help='fix original Japanese files during generating translation map (especially for adding missing \']\'...)')
  parser.add_argument('-l', '--log-basic', action='store_true', default=False, help='output minimal info (default: only errors will be shown)')
  parser.add_argument('-L', '--log-additional', action='store_true', default=False, help='output additional info (default: only errors will be shown)')
  parser.add_argument('-D', '--log-debug', action='store_true', default=False, help='output debug info (default: only errors will be shown)')
  args = parser.parse_args(args[1:])

  inputRootPath = pathlib.PurePath(args.input_root)
  if not os.path.isdir(inputRootPath):
    eprint(f'{progName}: error: provided $input-root is not a directory')
    return 1
  for e in args.input:
    if not os.path.exists(inputRootPath.joinpath(e)):
      eprint(f'{progName}: error: $input-root does not contain one of $input values ("{e}")')
      return 1

  if args.input_map == None:
    translationMap = dict()
    registerTranslationErrors = False
  else:
    if args.input_map != '-' and not os.path.isfile(args.input_map):
      eprint(f'{progName}: error: provided $input-map is not a file')
      return 1
    if args.input_map == '-':
      content = sys.stdin.read()
    else:
      with open(args.input_map) as f:
        content = f.read()
    translationMap = json.loads(content)
    translErrorLog = []
    registerTranslationErrors = True

  if args.output_map != None and args.output_map != '-':
    if os.path.isfile(args.output_map):
      if not os.access(args.output_map, os.W_OK):
        eprint(f'{progName}: error: provided $output-map is non-writable (must be a path to existing file or its directory should be able to store it)')
        return 1
    else:
      sParent = str(pathlib.PurePath(args.output_map).parent)
      if not os.path.isdir(sParent) or not os.access(sParent, os.W_OK | os.X_OK):
        eprint(f'{progName}: error: can\'t create a file at $output-map (must be a path to existing file or its directory should be able to store it)')
        return 1

  if args.diff_file != None:
    if os.path.isfile(args.diff_file):
      with open(args.diff_file) as f:
        diff = json.loads(f.read())
    else:
      eprint(f'{progName}: error: provided $diff-file is not a file')
      return 1
  else:
    diff = dict()

  if args.output_root != None:
    outputRootPath = pathlib.PurePath(args.output_root)
    if not os.path.isdir(outputRootPath):
      eprint(f'{progName}: error: provided $output-root is not a directory')
      return 1
    for e in args.input:
      if not os.path.exists(outputRootPath.joinpath(e)):
        eprint(f'{progName}: error: $output-root does not contain one of $input values ("{e}")')
        return 1

  inputFiles = getFiles(args.input_root, args.input, '.cfg.bin')

  for fnameInput in inputFiles:
    # Getting relative filename
    fname = pathlib.PurePath()
    for e in fnameInput.parts[len(inputRootPath.parts):]:
      fname = fname.joinpath(e)

    l5bt_file = L5BTFile(str(fnameInput))
    if args.log_basic: eprint(f'{progName}: provided file "{l5bt_file.filename}"')
    if args.log_additional: eprint(f'{progName}: loading file...', end='')
    l5bt_file.load()
    if args.log_additional: eprint(' Done!')
    if args.output_root != None:
      l5bt_file.filename = str(outputRootPath.joinpath(fname))

    # Because diff.json uses posix path, yes.
    fname = str(pathlib.PurePosixPath(fname))

    # Patching file using provided diff.json
    if fname in diff.keys():
      for k in diff[fname].keys():
        if l5bt_file.labels[int(k)].text != list(diff[fname][k].keys())[0]:
          eprint(f'{progName}: warning: failed to patch {fname}:{k} (strings are different)')
          continue
        l5bt_file.labels[int(k)].text = list(diff[fname][k].values())[0]
        if args.log_debug: eprint(f'{progName}: patched {fname}:{k}')

    # Applying/generating map.json if we need to do this
    hasJapaneseCharacters = False
    for e in l5bt_file.labels:
      c = hasJPChars(e.text)
      if c != False:
        if args.log_debug: eprint(f'{progName}: Japanese character detected (reason: \'{c}\')')
        hasJapaneseCharacters = True
        break
    if hasJapaneseCharacters:
      if args.log_additional: eprint(f'{progName}: modifying texts...', end='')

      if args.log_debug: eprint(f'{progName}: texts in Japanese:')
      for i in range(len(l5bt_file.labels)):
        s = l5bt_file.labels[i].text
        if s == args.current_name:
          eprint(f'{progName}: critical: there is a left-value named \"{s}\", which is used to be a counter of translated strings (you must assign another keyword, run with "--help" argument for more info)')
          return 1
        if hasJPChars(s) != False:
          # All modifications should be done here:
          if s in translationMap.keys():
            l5bt_file.labels[i].text = translationMap[s]
          else:
            if registerTranslationErrors:
              transErrTxt = f'{progName}: error translating: "' + s.replace('\n', '\\n') + '"'
              if args.log_debug:
                eprint(transErrTxt)
              translErrorLog.append(transErrTxt+'\n')
            if args.output_map != None:
              if args.fix_original_files:
                if s == '\u30df\u30f3\u30ca\u30d8\u30f3\u30b2\u3010[\u5b88/\u30ac\u30fc\u30c9\u3011': s += ']'
              translationMap[s] = s

          if args.log_debug:
            if s != l5bt_file.labels[i].text:
              eprint(' + "' + s.replace('\n', '\\n') + '" -> "' + l5bt_file.labels[i].text.replace('\n', '\\n') + '"')

      if args.log_additional: eprint(' Done!')

    if args.output_root != None:
      if args.log_additional: eprint(f'{progName}: saving file...', end='')
      l5bt_file.save()
      if args.log_additional: eprint(' Done!')

  if args.output_map != None:
    mapOutput = json.dumps(translationMap, indent=2, ensure_ascii=False)
    if args.output_map == '-':
      print(mapOutput)
    else:
      with open(args.output_map, 'w') as f:
        f.write(mapOutput)

  if registerTranslationErrors and len(translErrorLog):
    eprint('Translation errors:')
    for e in translErrorLog:
      eprint(' - ' + e)

if __name__ == '__main__':
  exit(main(sys.argv))
