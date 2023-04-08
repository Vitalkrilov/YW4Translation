#!/bin/python

import os
import sys
import pathlib
import argparse



def calcSizes(homeDirStr, dirsToCheckStrs):
  homeDir = pathlib.PurePath(homeDirStr)
  dirsToCheck = [homeDir.joinpath(e) for e in dirsToCheckStrs]
  sizes=dict()

  while len(dirsToCheck):
    curDir = dirsToCheck[0]
    del dirsToCheck[0]
    for e in os.listdir(curDir):
      filename = curDir.joinpath(e)
      if os.path.isfile(filename):
        fname = pathlib.PurePath()
        for e in filename.parts[len(homeDir.parts):]:
          fname = fname.joinpath(e)
        sizes[str(pathlib.PurePosixPath(fname))] = os.path.getsize(filename)
      else:
        dirsToCheck.append(filename)
  return sizes

def main(args):
  progName = args[0]
  parser = argparse.ArgumentParser(prog=progName, description='This script updates file sizes and creates new cpk_list.cfg.bin file.',
epilog=f'''examples:
 $  {progName} cpk_list.cfg.bin.off cpk_list.cfg.bin text_all
 $  {progName} cpk_list.cfg.bin.off.json cpk_list.cfg.bin text_all data/common/text/ja data/common/text/en''', formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('cpk_list_input', help='path from where cpk_list.cfg.bin/cpk_list.cfg.bin.json should be read (if it ends with ".json", then it will be interpreted as JSON file). Due to really slow loading of cpk_list.cfg.bin, it\'s highly recommended to use JSON version (if you don\'t want to use the file which was converted from original and provided in my repo, you can convert to it using L5BTFile.py: just load .cfg.bin and export to JSON)')
  parser.add_argument('cpk_list_output', help='path to where cpk_list.cfg.bin will be saved')
  parser.add_argument('directory_to_check', help='path to text_all\'s root directory where all *.cfg.bin files stored')
  parser.add_argument('calculate_dirs', default=['data/common/text/ja'], help='override relative directories where to calculate sizes (default: ["data/common/text/ja"])', nargs='*')
  args = parser.parse_args(args[1:])

  sizes = calcSizes(args.directory_to_check, args.calculate_dirs)

  from L5BTFile import L5BTFile

  l5bt_file = L5BTFile(args.cpk_list_output)
  if args.cpk_list_input.endswith('.json'):
    l5bt_file.fromJSON(open(args.cpk_list_input).read())
  else:
    l5bt_file.filename = cpk_list_input
    l5bt_file.load()
    l5bt_file.filename = cpk_list_output

  m=dict()
  for i in range(len(l5bt_file.labels)):
    m[l5bt_file.labels[i].relOffset] = i

  for e in l5bt_file.entries:
    if len(e.data) == 3 and e.data[0].bType == 0 and e.data[1].bType == 0 and e.data[2].bType == 1: # validating data's types in entry
      if e.data[0].value in m.keys() and e.data[1].value in m.keys() and l5bt_file.labels[m[e.data[1].value]].text == 'data/common/text/text_all.cpk': # validating that entry has filename and that this entry belongs to text_all.cpk
        filename = l5bt_file.labels[m[e.data[0].value]].text
        if filename in sizes.keys():
          e.data[2].value = sizes[filename]

  l5bt_file.save()

if __name__ == '__main__':
  exit(main(sys.argv))
