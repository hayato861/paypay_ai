#!/bin/bash

# コミットメッセージがない場合
if [ -z "$1" ]; then
    echo "使い方:"
    echo '  ./release.sh "コミットメッセージ"'
    exit 1
fi

echo ""
echo "=============================="
echo "   PayPay AI Release Tool"
echo "=============================="
echo ""

# Git管理下か確認
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Gitリポジトリではありません。"
    exit 1
fi

echo "📋 現在の変更内容"
git status
echo ""

# 変更があるか確認
if git diff --quiet && git diff --cached --quiet; then
    echo "✅ 変更はありません。"
    exit 0
fi

read -p "この内容でコミット＆Pushしますか？ (y/n): " answer

if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
    echo "キャンセルしました。"
    exit 0
fi

echo ""
echo "📦 Git Add..."
git add .

echo "📝 Commit..."
git commit -m "$1"

echo "🚀 Push..."
git push

echo ""
echo "🎉 完了しました！"