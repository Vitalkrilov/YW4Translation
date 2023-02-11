#!/bin/python

# This script updates file sizes and creates new cpk_list.cfg.bin file then

# <config>
recalculateDirs = [ 'data/common/text/ja' ]
# </config>

import os
import sys



def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

def calcSizes(paths, ignorePrefix):
  sizes=dict()
  dirsToCheck = [(ignorePrefix + e) for e in paths]

  while len(dirsToCheck):
    curDir = dirsToCheck[0]
    del dirsToCheck[0]
    for e in os.listdir(curDir):
      filename = curDir + '/' + e
      if os.path.isfile(filename):
        sizes[filename[len(ignorePrefix):]] = os.path.getsize(filename)
      else:
        dirsToCheck.append(filename)
  return sizes

if __name__ == '__main__':
  if len(sys.argv) != 4:
    eprint(f'Usage: {sys.argv[0]} cpk_list_json_input cpk_list_output directory_to_check')
    eprint(f'Note: directory_to_check is a root directory which must contain data/common/text/ja')
    eprint(f'Example: {sys.argv[0]} cpk_list.cfg.bin.off.json cpk_list.cfg.bin text_all/')
    exit(1)

  if sys.argv[3][-1] != '/': sys.argv[3] += '/'

  sizes = calcSizes(recalculateDirs, sys.argv[3])

  from L5BTFile import L5BTFile

  l5bt_file = L5BTFile(sys.argv[2])
  l5bt_file.fromJSON(open(sys.argv[1]).read())

  m=dict()
  for i in range(len(l5bt_file.labels)):
    m[l5bt_file.labels[i].relOffset] = i

  for e in l5bt_file.entries:
    if len(e.data) == 3 and e.data[0].bType == 0 and e.data[1].bType == 0 and e.data[2].bType == 1:
      if e.data[0].value in m.keys() and e.data[1].value in m.keys() and l5bt_file.labels[m[e.data[1].value]].text == 'data/common/text/text_all.cpk':
        filename = l5bt_file.labels[m[e.data[0].value]].text
        if filename in sizes.keys():
          e.data[2].value = sizes[filename]

  l5bt_file.save()
