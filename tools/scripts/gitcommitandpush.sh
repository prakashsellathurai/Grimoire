#!/bin/bash
commitMessage="Backup Daemon: Auto commit on `date +%Y%m%d%H%M%S`";
# 1. Fetch and pull all submodules simultaneously in the background
git submodule update --remote --recursive --jobs 8

# 2. Stage, check, and commit locally in one pass
git submodule foreach --recursive '
  git add .
  if ! git diff --cached --quiet; then
    git commit -q -m "'"${commitMessage}"'"
  fi
'
git add .
git commit -m "$commitMessage"
git push origin main --recurse-submodules=on-demand
