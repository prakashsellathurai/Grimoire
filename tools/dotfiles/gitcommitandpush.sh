#!/bin/bash
commitMessage="Backup Daemon: Auto commit on `date +%Y%m%d%H%M%S`";
# 1. Configure submodules to track the main branch (if not already set)
git submodule foreach --recursive "git config -f .gitmodules submodule.\$name.branch main"

# 2. Parallel fetch and merge everything from origin/main at once
git submodule update --remote --merge --recursive --jobs 8

# 3. Stage changes and commit locally in a single loop pass
git submodule foreach --recursive '
  git add .
  if ! git diff --cached --quiet; then
    git commit -q -m "'"${commitMessage}"'"
  fi
'
git add .
git commit -m "$commitMessage"
git push origin main --recurse-submodules=on-demand
