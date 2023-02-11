#!/bin/bash

if [ ! -d work ] || [ ! -d work/text_all.src ]; then
  mkdir -p work
  echo 'Put text_all.src/ (and optional text_all.diff/ to diff text_all.src/ with) in work/';
  echo 'After script finishes, there will be final text_all/. Other directories will be unmodified.'
  exit
fi

shopt -s globstar &&

echo Diffing files... &&
if [ -d work/text_all.diff ]; then
  ./diff.py text_all.src text_all.diff work/text_all.src/data/common/text/ja/**/*.cfg.bin > work/diff.json
fi &&

echo Generating map.json... &&
./patcher.py work/map.json '' text_all.src '' work/text_all.src/data/common/text/ja/**/*.cfg.bin &&

echo Translating map.json... &&
./transrun.py work/map.json work/map.json &&

echo Replacing map.json... &&
./replaces.py work/map.json work/map.json &&

echo Patching newly created files... &&
cp -a work/text_all.src work/text_all &&
./patcher.py work/map.json work/diff.json text_all.src text_all work/text_all.src/data/common/text/ja/**/*.cfg.bin &&

echo Updating file sizes... &&
./updateCPKLIST.py data/off/cpk_list.cfg.bin.json work/cpk_list.cfg.bin work/text_all &&

echo Successfully finished.
