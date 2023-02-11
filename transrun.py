#!/bin/python

# This script translates provided map.json. If you run it on normal Linux (or maybe other supported OS) then you will be able to start/pause translation by hitting NumLock (if you have led on it :) ), if you have led but it not working => change path var in checkStatus(). When translation is done or paused or autosave point is reached, it will be saved and you will be able to safely close it. After next launch it will continue from where it saved.
# WARNING: might not translate something from first attempt (fixed in replace.py)

# <config>
AUTOSAVEEVERYCOUNT = 500
USETRANSLATOR = 'g' # 'g': Google, 'y': Yandex
SOURCELANG = 'ja'
TARGETLANG = 'en'
TEXTSPERTIME = 25 # For Google I used 25, For Yandex -- 10 (due to less symbols in api)
# </config>

import json
import os
import sys
import time
from googletrans import Translator



def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

def removeNL(s): return s.replace('\n', '\\n')
def hasJPChar(s):
  for c in s:
    if ord(c) > 0x3000:
      return True
  return False

newlineRequired=''
alerted = False
def checkStatus():
  path = '/sys/class/leds/input5::numlock/brightness'
  if not os.path.exists(path): # No pause support then...
    eprint(f'{newlineRequired}{sys.argv[0]}: led of numlock not found so pause is not supported')
    return True
  f=open(path)
  b=f.read()[0]
  f.close()
  if b == '1':
    return True
  return False

if __name__ == '__main__':
  if len(sys.argv) != 3:
    eprint(f'Usage: {sys.argv[0]} input_file output_file')
    eprint(f'Examples: {sys.argv[0]} map.json gtrwork.json')
    eprint('        or')
    eprint(f'          {sys.argv[0]} gtrwork.json gtrwork.json')
    exit(1)

  f=open(sys.argv[1])
  data=json.loads(f.read())
  if 'current' in data.keys():
    current = data['current']
    del data['current']
  else:
    current = 0
  f.close()

  keys = list(data.keys())
  i = current
  t=Translator()
  while i <= len(keys):
    if not checkStatus() or ((i - current) % AUTOSAVEEVERYCOUNT) == 0 or i == len(keys):
      f=open(sys.argv[2],'w')
      data['current'] = i+1
      f.write(json.dumps(data, indent=2))
      f.close()
      eprint(f'{newlineRequired}{sys.argv[0]}: save completed, progress [{i}/{len(keys)}]')
      if i == len(keys): break

    while True:
      if checkStatus(): break
      time.sleep(0.1)

    cnt = min(TEXTSPERTIME, len(keys)-i)
    if USETRANSLATOR == 'g':
      tData = t.translate(keys[i:i+cnt], src=SOURCELANG, dest=TARGETLANG)
      if len(tData) != cnt:
        eprint(f'{newlineRequired}{sys.argv[0]}: error: got wrong length of result {len(tData)}, retrying...')
        continue
      for j in range(cnt):
        if tData[j].src != SOURCELANG:
          eprint(f'{newlineRequired}{sys.argv[0]}: warning: got wrong lang code {tData[j].src}, index is {i+j}')
        if hasJPChar(tData[j].text):
          eprint(f'{newlineRequired}{sys.argv[0]}: error: probably non-translated string "{removeNL(tData[j].origin)}" -> "{removeNL(tData[j].text)}", index is {i+j}, retrying...')
          break
        data[keys[i+j]] = tData[j].text
        eprint('|', end='')
        sys.stdout.flush()
        newlineRequired ='\n'
        i += 1
    elif USETRANSLATOR == 'y':
      rUploadData = {'sourceLanguageCode': SOURCELANG, 'targetLanguageCode': TARGETLANG, 'texts': keys[i:i+cnt]}
      r = requests.post('https://cloud.yandex.ru/api/translate/translate', json=rUploadData)
      if r.status_code != 200:
          eprint(f'{newlineRequired}{sys.argv[0]}: error: got status code {r.status_code}, response is \'{r.text}\', retrying...')
          continue
      rDownloadData = json.loads(r.text)['translations']
      if len(rDownloadData) != cnt:
          eprint(f'{newlineRequired}{sys.argv[0]}: error: got wrong size {len(rDownloadData)}, response is \'{r.text}\': retrying...')
          break
      for j in range(cnt):
          if rDownloadData[j]['detectedLanguageCode'] != 'ja':
              eprint(f'{newlineRequired}{sys.argv[0]}: warning: got wrong lang code {rDownloadData[j]["detectedLanguageCode"]}, index is {i+j}')
          data[keys[i+j]] = rDownloadData[j]['text']
      eprint('|'*cnt, end='')
      sys.stdout.flush()
      newlineRequired ='\n'
      i += cnt
    else:
      eprint(f'{sys.argv[0]}: error: unknown translator code: "{USETRANSLATOR}"')
      exit(1)
