#!/bin/python

# <config>
defaultTranslation = [ "google", "ja", "en", None, None ]
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

from myutils import eprint, removeNL, hasJPChars
import os
import sys
import json
import re
import time
import argparse



quadTagsMatcher=re.compile(r'\[(?:(?![\]]).)*?\]')
triangleTagsMatcher=re.compile(r'<(?:(?![>]).)*?>')

def replaceSpecialTags(method, translatePack):
  if method == 'none': return (translatePack, dict(), [])
  if method not in [ 'numbers', 'xml' ]:
    eprint(f'{sys.argv[0]}: error: ignoring unknown method {method}')
    return (translatePack, dict(), [])
  res = []
  tagsMap = dict()
  tagsList = []
  for e in translatePack:
    tagsList.append([])
    foundTags = quadTagsMatcher.findall(e) + triangleTagsMatcher.findall(e)
    for t in foundTags:
      if t not in tagsMap:
        if method == 'numbers':
          tagsMap[t] = '[' + str(len(tagsMap)) + ']'
        else: # 'xml'
          tagsMap[t] = '<h' + str(len(tagsMap)) + '/>'
      e = e.replace(t, tagsMap[t], 1)
      tagsList[-1].append(tagsMap[t])
    res.append(e)
  return (res, tagsMap, tagsList)

def unreplaceSpecialTags(method, translatePack, tagsMap, tagsList):
  if method == 'none': return translatePack
  if method not in [ 'numbers', 'xml' ]:
    eprint(f'{sys.argv[0]}: error: ignoring unknown method {method}')
    return translatePack

  tagsMapSwapped = dict()
  for e in tagsMap:
    tagsMapSwapped[tagsMap[e]] = e

  for i in range(len(translatePack)):
    foundTags = quadTagsMatcher.findall(translatePack[i]) + triangleTagsMatcher.findall(translatePack[i])
    if len(tagsList[i]) != len(foundTags) or set(tagsList[i]) != set(foundTags):
      eprint(f'{sys.argv[0]}: error: tags differ: before ({tagsList[i]}), after ({foundTags})')
      return translatePack
    for t in foundTags:
      translatePack[i] = translatePack[i].replace(t, tagsMapSwapped[t], 1)
  return translatePack

def getTranslationUtilByName(translator):
  if translator == 'google':
    from googletrans import Translator
    return Translator()
  elif translator == 'yandex':
    import requests
    return requests

# Returns as much elements as it could safely translate
# 'google': $util is googletrans.Translator()
# 'yandex': $util is requests
# Providing $util is highly recommended for best performance
def translate(translator, source_lang, target_lang, translatePack, util=None):
  if util == None: util = getTranslationUtilByName(translator)
  res = []
  if translator == 'google':
    tData = util.translate(translatePack, src=source_lang, dest=target_lang)
    if len(tData) != len(translatePack):
      tmpStr = ", ".join(["\""+e.text+"\"" for e in tData])
      eprint(f'{sys.argv[0]}: error: got wrong length of result {len(tData)}; result strings are [{removeNL(tmpStr)}]')
      return res
    for j in range(len(translatePack)):
      if tData[j].src != source_lang:
        eprint(f'{sys.argv[0]}: warning: got wrong lang code {tData[j].src} ("{removeNL(translatePack[j])}" -> "{removeNL(tData[j].text)}")')
      res.append(tData[j].text)
  elif translator == 'yandex':
    rUploadData = {'sourceLanguageCode': source_lang, 'targetLanguageCode': target_lang, 'texts': translatePack}
    r = util.post('https://cloud.yandex.ru/api/translate/translate', json=rUploadData)
    if r.status_code != 200:
        eprint(f'{sys.argv[0]}: error: got status code {r.status_code}, response is \'{removeNL(r.text)}\'')
        return res
    rDownloadData = json.loads(r.text)['translations']
    if len(rDownloadData) != len(translatePack):
        eprint(f'{sys.argv[0]}: error: got wrong size {len(rDownloadData)}, response is \'{removeNL(r.text)}\'')
        return res
    for j in range(len(translatePack)):
        if rDownloadData[j]['detectedLanguageCode'] != target_lang:
            eprint(f'{sys.argv[0]}: warning: got wrong lang code {rDownloadData[j]["detectedLanguageCode"]} ("{removeNL(translatePack[j])}" -> "{removeNL(rDownloadData[j]["text"])}")')
        res.append(rDownloadData[j]['text'])
  return res



# Replaces '[a/b]' to 'a'
purifyMatcher = re.compile(r'\[(?:(?![\]/]).)*?/(?:(?![\]]).)*?\]')
def purify(text):
  global purifyMatcher
  for e in purifyMatcher.findall(text):
    text = text.replace(e, e[1:-1].split('/')[0], 1)
  return text

# Used to replace Japanese character to their ASCII equivalent if translator did not
def hasUnwantedChar(s):
  global charReplaces
  for e in charReplaces.keys():
    if e in s:
      return True
  return False
def fixUnwantedChars(s):
  global charReplaces
  for e in charReplaces.keys():
    s = s.replace(e, charReplaces[e])
  return s

# Used to replace translated words which was misunderstood by translator
def localize(s):
  global wordReplaces
  for e in wordReplaces.keys():
    if e in s:
      s = re.sub(r'(\b)' + e + r'(\b)', r'\1' + wordReplaces[e] + r'\2', s)
  return s


# Used to fix codes like '[$ something]' to '[$something]'
def fixBrokenSpecials(s):
  global quadTagsMatcher
  for e in quadTagsMatcher.findall(s):
    if e.startswith('[$ '):
      s = s.replace(e, '[$'+e[3:], 1)
  return s

# All tweaks in one. Notice: you better translate text before calling this function, because these fixes... it's kinda last resort
defaultUtil = None
def tryToModify(s, enabledPRF=False, enabledFUC=False, translation=False, enabledFBS=False, enabledLOC=False, logChanges=True):
  if translation != False:
    if type(translation) != list or len(translation) != 5:
      translation = defaultTranslation
    translation[3] = [s]
    if translation[-1] == None:
      global defaultUtil
      if defaultUtil == None:
        defaultUtil = getTranslationUtilByName("google")
      translation[-1] = defaultUtil

  if s in ignoreList: return s
  if enabledPRF:
    t = purify(s)
    if t != s:
      if logChanges: eprint(f'  PRF:"{removeNL(s)}" -> "{removeNL(t)}"')
      s = t
  if enabledFUC:
    if hasUnwantedChar(s):
      t = fixUnwantedChars(s)
      if t != s:
        if logChanges: eprint(f'  FUC:"{removeNL(s)}" -> "{removeNL(t)}"')
        s = t
  if translation != False:
    if hasJPChars(s) != False:
      translation[3], tagsMap, tagsList = replaceSpecialTags('numbers', translation[3])
      t = translate(*translation)
      t = unreplaceSpecialTags('numbers', t, tagsMap, tagsList)
      if len(t) != 1: eprint('  TRA: error')
      else:
        modified = t != s
        if modified:
          if logChanges: eprint(f'  TRA:"{removeNL(s)}" -> "{removeNL(t)}"')
          s = t
        if not modified or hasJPChars(s) != False:
          if logChanges: eprint('  TRA: did not help...')
  if enabledFBS:
    t = fixBrokenSpecials(s)
    if t != s:
      if logChanges: eprint(f'  FBS:"{removeNL(s)}" -> "{removeNL(t)}"')
      s = t
  if enabledLOC:
    t = localize(s)
    if t != s:
      if logChanges: eprint(f'  LOC:"{removeNL(s)}" -> "{removeNL(t)}"')
      s = t
  return s



alerted = False
def checkStatus(path):
  global alerted
  if path == '' or not os.path.isfile(path): # No pause support then...
    if not alerted:
      if path != '':
        eprint(f'{sys.argv[0]}: file not found, so pause is not supported')
      alerted = True
    return True
  with open(path) as f:
    b=f.read()[0]
  return b == '1'

def main(args):
  progName = args[0]
  parser = argparse.ArgumentParser(prog=progName, description='''This script localizes provided map.json.

If you run it on regular Linux (or maybe other supported OS), then you will be able to start / pause translation by hitting NumLock (if you have led on it). If you want to use a file as switch / use another led, then you can override it.
When translation is done, paused or autosave point is reached, it will be saved and you will be able to safely close it (by hitting "^C" xD). After next launch it will continue from position where it was saved.''',
epilog=f'''examples:
 $  {progName} -vpubr map.json newmap.json          #COMMENT: translate given "map.json", save to "newmap.json", apply PRF, FUC, FBS, LOC tweaks; show progress as soon as script can tell
 $  {progName} -b map.json newmap.json -s en -t fr  #COMMENT: translate from "en" lang to "fr" lang given "map.json" and save to "newmap.json", apply only FBS tweak (because PRF and FUC mostly needed when translating from original Japanese; LOC mostly used when target lang is "en"; but FBS helps to fix tags if they\'re becoming broken after translation)''', formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('file', help='path to translation map file to read from (example: "map.json")')
  parser.add_argument('file_out_override', help='path to translation map file to write to (example: "map.json"). if you don\'t provide it, then $file will be updated instead', nargs='?')
  parser.add_argument('-l', '--switcher', default='/sys/class/leds/input5::numlock/brightness', help='path to switcher file: if first symbol inside is \'1\', then translation will work, else it saves and pauses (default: "/sys/class/leds/input5::numlock/brightness"); use \'\' (empty argument) to disable this feature')
  parser.add_argument('-a', '--auto-save', default=500, type=int, help='set how much entries should be translated before autosave triggers (default: 500)')
  parser.add_argument('-m', '--translator', default='google', choices=['google', 'yandex'], help='choose what translator to use (default: "google")')
  parser.add_argument('-s', '--source-lang', default='ja', help='choose from what language to translate (default: "ja")')
  parser.add_argument('-t', '--target-lang', default='en', help='choose to what language to translate (default: "en")')
  parser.add_argument('-c', '--texts-per-request', default=25, type=int, help='set how much entries should be translated per request (default: 25); for "google" I used 25, for "yandex" -- 10 (due to less max symbols count in its API)')
  parser.add_argument('-v', '--more-verbose', action='store_true', default=False, help='output status every translation request (default: only on autosaves)')
  parser.add_argument('-p', '--purify', action='store_true', default=False, help='(abbr:PRF) purify text entries before translation (just replacing these "[a/b]" sequences to "a" which used in Japanese texts)')
  parser.add_argument('-u', '--fix-unwanted-chars', action='store_true', default=False, help='(abbr:FUC) replace Japanese characters to their ASCII version')
  parser.add_argument('-b', '--fix-broken-specials', action='store_true', default=False, help='(abbr:FBS) fix broken game special tags (just replacing "[$ keyword]" to [$keyword])')
  parser.add_argument('-r', '--apply-replaces', action='store_true', default=False, help='(abbr:LOC) replace some "misspelled" by translator words to their right form')
  args = parser.parse_args(args[1:])

  googleLanguageCodes = ['am', 'ar', 'eu', 'bn', 'en-GB', 'pt-BR', 'bg', 'ca', 'chr', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fil', 'fi', 'fr', 'de', 'el', 'gu', 'iw', 'hi', 'hu', 'is', 'id', 'it', 'ja', 'kn', 'ko', 'lv', 'lt', 'ms', 'ml', 'mr', 'no', 'pl', 'pt-PT', 'ro', 'ru', 'sr', 'zh-CN', 'sk', 'sl', 'es', 'sw', 'sv', 'ta', 'te', 'th', 'zh-TW', 'tr', 'ur', 'uk', 'vi', 'cy']
  errCode = ''
  if args.source_lang not in googleLanguageCodes:
    errCode = args.source_lang
  if args.target_lang not in googleLanguageCodes:
    errCode = args.target_lang
  if errCode:
    eprint(f'{progName}: "{errCode}": unsupported language code')
    codes = ', '.join(sorted(['"'+e+'"' for e in googleLanguageCodes]))
    eprint(f'Available language codes: {codes}.')
    exit(1)

  if args.file_out_override == None:
    args.file_out_override = args.file

  util = getTranslationUtilByName(args.translator)

  with open(args.file) as f:
    data = json.loads(f.read())
    if '$transrun.py/current$' in data.keys():
      current = data['$transrun.py/current$']
      del data['$transrun.py/current$']
    else:
      current = 0

  keys = list(data.keys())
  i = current
  while True:
    if not checkStatus(args.switcher) or ((i - current) % args.auto_save) == 0 or i >= len(keys):
      data['$transrun.py/current$'] = i
      f=open(args.file_out_override, 'w')
      f.write(json.dumps(data, indent=2, ensure_ascii=False))
      f.close()
      eprint(f'{progName}: save completed, progress [{i}/{len(keys)}]')
      del data['$transrun.py/current$']
      if i >= len(keys): break

    while True:
      if checkStatus(args.switcher): break
      time.sleep(0.1)

    # Every iteration: translating few text entries
    cnt = min(args.texts_per_request, len(keys)-i)
    neededToTranslatePack = []
    for e in keys[i:i+cnt]:
      e = data[e]
      if args.purify: e = purify(e)
      neededToTranslatePack.append(e)
    neededToTranslatePack, tagsMap, tagsList = replaceSpecialTags('numbers', neededToTranslatePack)
    translatedPack = translate(args.translator, args.source_lang, args.target_lang, neededToTranslatePack, util)
    translatedPack = unreplaceSpecialTags('numbers', translatedPack, tagsMap, tagsList)
    for j in range(len(translatedPack)):
      if data[keys[i+j]] not in ignoreList:
        data[keys[i+j]] = tryToModify(translatedPack[j], enabledFUC=args.fix_unwanted_chars, enabledFBS=args.fix_broken_specials, enabledLOC=args.apply_replaces)
        if hasJPChars(data[keys[i+j]]) != False:
          eprint(f'{progName}: warning: probably non-translated string (even after fixes): "{removeNL(data[keys[i+j]])}"')
    i += len(translatedPack)
    if args.more_verbose:
      eprint(f'{progName}: progress [{i}/{len(keys)}]')

if __name__ == '__main__':
  exit(main(sys.argv))
