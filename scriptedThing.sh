#!/bin/bash

if [ ! -d work ] || [ ! -d work/text_all.src ]; then
  mkdir -p work
  echo 'Put "text_all.src/" (and optional "text_all.diff/" to diff "text_all.src/" with) in "work/"';
  echo 'After script finishes, there will be final "text_all/". Other directories will be unmodified.'
  exit
fi

if [ -d work/text_all.diff ]; then
  echo Diffing files... &&
  ./diff.py -1 -c 11111 -s work/text_all.src -a work/text_all.diff -o work/diff.json
fi &&

echo Generating map.json... &&
./patcher.py -f -i work/text_all.src -M work/map.json &&

echo Localizing map.json... &&
./localize.py work/map.json work/map.json &&

echo Patching newly created files... &&
cp -a work/text_all.src work/text_all &&
if [ -f work/diff.json ]; then
  DIFFJSON='-d work/diff.json'
else
  DIFFJSON=''
fi &&
./patcher.py -i work/text_all.src -m work/map.json "$DIFFJSON" -o work/text_all &&

echo Updating file sizes... &&
./updateCPKLIST.py data/origs/cpk_list.cfg.bin.json work/cpk_list.cfg.bin work/text_all &&

echo Successfully finished.
