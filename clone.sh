#!/usr/bin/env bash

git clone $1 $2 --recursive
cd $2
for branch in $(git branch --all | grep '^\s*remotes' | egrep --invert-match '(:?HEAD|master)$'); do
    git branch --track "${branch##*/}" "$branch"
done
git pull --all