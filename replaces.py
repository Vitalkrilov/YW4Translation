#!/bin/python

# This script makes strings look better (translating, replacing chars, words and etc.). It used to fix already translated map.json using translate.py (Google ignored some entries so I needed to retranslate them...)

# <config>
SOURCELANG = 'ja'
TARGETLANG = 'en'
ignoreList = [
  # It's probably someething like char map? so better not change it...
  '\u00a0!\u00a0?\u00a0:\u00a0%\u00a0\u00ab\u00a0\u00bb \uff5e~<->\u00ad\u00a0\u2190\n\u2191\u2192\u2193\u2606\u2605\u203b\u25b3\u25b2\u25bd\u25bc\n\u25a1\u25a0\u25cb\u25cf\u00b0\u00aa\uff1d\uff0f\u21d4\u21d2\u266a\u266a'
]
charReplaces = {
  '『': '"',
  '』': '"',
  '～': '~',
  '＝': '=',
  '／': '/',
  'ー': '-',
  '！': '!',
  '？': '?',
  '。': '.',
  '【': '[',
  '】': ']',
  '）': ')',
  '・': '·',
  '…': '...',
  ' !': '!',
  ' ?': '?'
}
wordReplaces = {
  'Yo-Kai': 'Yo-kai',
  'Yokai': 'Yo-kai',
  'yokai': 'Yo-kai',
  'Youkai': 'Yo-kai',
  'youkai': 'Yo-kai'
}
# </config>

import sys



def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

def removeNL(s): return s.replace('\n', '\\n')

def hasUnwantedChar(s):
  for e in charReplaces.keys():
    if e in s:
      return True
  return False
def fixUnwantedChars(s):
  global charReplaces
  for e in charReplaces.keys():
    s = s.replace(e, charReplaces[e])
  return s

def hasJPChar(s):
  for c in s:
    if ord(c) > 0x3000:
      return True
  return False
from googletrans import Translator
gtr=Translator()
def translate(s):
  global gtr
  return gtr.translate(s, src=SOURCELANG, dest=TARGETLANG).text

import re
def localize(s):
  global wordReplaces
  for e in wordReplaces.keys():
    if e in s:
      s = re.sub(r'(\W)' + e + r'(\W)', r'\1' + wordReplaces[e] + r'\2', s)
  return s

matcher=re.compile(r'\[(?:(?![\]]).)*?\]')
def fixBrokenSpecials(s):
  global matcher
  for e in matcher.findall(s):
    if e.startswith('[$ '):
      s = s.replace(e, '[$'+e[3:], 1)
  return s

logChanges = True
def modify(s):
  if s in ignoreList: return s
  if hasUnwantedChar(s):
    t = fixUnwantedChars(s)
    if t != s:
      if logChanges: eprint(f'  FUC:"{removeNL(s)}" -> "{removeNL(t)}"')
      s = t
  if hasJPChar(s):
    t = translate(s)
    if t != s:
      if logChanges: eprint(f'  TRA:"{removeNL(s)}" -> "{removeNL(t)}"')
      s = t
    if hasJPChar(s):
      if logChanges: eprint('  TRA: did not help...')
  t = fixBrokenSpecials(s)
  if t != s:
    if logChanges: eprint(f'  FBS:"{removeNL(s)}" -> "{removeNL(t)}"')
    s = t
  t = localize(s)
  if t != s:
    if logChanges: eprint(f'  LOC:"{removeNL(s)}" -> "{removeNL(t)}"')
    s = t
  return s

if __name__ == '__main__':
  if len(sys.argv) != 3:
    eprint(f'Usage: {sys.argv[0]} input_file output_file')
    eprint(f'Examples: {sys.argv[0]} map.json map.json')
    eprint('        or')
    eprint(f'          {sys.argv[0]} map.json mapnew.json')
    exit(1)

  import json
  a = json.loads(open(sys.argv[1]).read())
  k = list(a.keys())
  for i in range(len(k)):
    if k[i] == 'current': continue
    a[k[i]] = modify(a[k[i]])
  f=open(sys.argv[2], 'w')
  f.write(json.dumps(a, indent=2))
  f.close()
