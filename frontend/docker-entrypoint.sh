#!/bin/sh
set -e

sync_deps() {
  STAMP=node_modules/.deps-lock-stamp
  NEED_INSTALL=false

  if [ ! -d node_modules ] || [ ! -d node_modules/@vite-pwa/nuxt ]; then
    NEED_INSTALL=true
  elif [ ! -f "$STAMP" ] || [ package-lock.json -nt "$STAMP" ]; then
    NEED_INSTALL=true
  fi

  if [ "$NEED_INSTALL" = true ]; then
    echo "Syncing npm dependencies..."
    npm install
    touch "$STAMP"
  fi
}

sync_deps

if [ ! -f .nuxt/nuxt.d.ts ]; then
  echo "Preparing Nuxt..."
  npx nuxt prepare
fi

exec npm run dev
