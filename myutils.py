# Basic utils needed in my scripts

import os
import sys
import pathlib

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# NOTE: 0x3000 symbol is ignored but you might want to get rid of it to (if so then just use localize.py where you will need to add {'\u3000': ' '})
def hasJPChars(text):
  for c in text:
    if ord(c) > 0x3000:
      return c
  return False

# Please do not ask me why the hell it's here
def removeNL(s): return s.replace('\n', '\\n')

def getFiles(homeDirStr, pathsToCheckStrs, extension=''):
  homeDir = pathlib.PurePath(homeDirStr)
  dirsToCheck = []
  res=[]
  for e in pathsToCheckStrs:
    filename = homeDir.joinpath(e)
    if os.path.isfile(filename):
      res.append(filename)
    else:
      dirsToCheck.append(filename)

  while len(dirsToCheck):
    curDir = dirsToCheck[0]
    del dirsToCheck[0]
    for e in os.listdir(curDir):
      filename = curDir.joinpath(e)
      if os.path.isfile(filename):
        if filename.name.endswith(extension):
          res.append(filename)
      else:
        dirsToCheck.append(filename)
  return res
