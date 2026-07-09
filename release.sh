#!/bin/bash

if [ -z "$1" ]; then
    echo "使い方: ./release.sh \"コミットメッセージ\""
    exit 1
fi

git add .

git commit -m "$1"

git push