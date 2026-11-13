#!/usr/bin/env bash
# Builds ./shopfront-ui: main with the base docs, and two branches that regenerate the docs.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
git_c() { git -c user.name=dev -c user.email=dev@example.invalid -c commit.gpgsign=false "$@"; }
mkdir -p shopfront-ui
cp -R "$here/files/repo-base/." shopfront-ui/
cd shopfront-ui
git init -q -b main
git_c add -A
git_c commit -q -m "Add shopfront-ui with agent docs"
for model in opus sonnet; do
  git checkout -q -b "docs/regen-$model" main
  cp -R "$here/files/regen-$model/." .
  git_c add -A
  git_c commit -q -m "Regenerate agent docs with knowledge-foundation ($model)"
done
git checkout -q main
