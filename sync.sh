#!/usr/bin/env bash
# Quick sync script to commit and push changes in persian-writing-skills
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

MSG="${1:-update persian writing skills and tools}"

echo "==> Checking git status in $DIR..."
git status -s

if [ -z "$(git status --porcelain)" ]; then
    echo "No changes to commit. Working tree clean."
    exit 0
fi

echo "==> Staging all changes..."
git add -A

echo "==> Committing with message: '$MSG'..."
git commit -m "$MSG"

echo "==> Pushing to origin main..."
git push origin main

echo "✓ Successfully synced to GitHub!"
