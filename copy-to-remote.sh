#!/bin/zsh

rsync -av \
  --exclude=.venv \
  --exclude=.idea \
  --exclude=.git \
  --exclude=target \
  --exclude=.env \
  . \
  ivadmy@troi.aau.at:~/vul-detection11/
