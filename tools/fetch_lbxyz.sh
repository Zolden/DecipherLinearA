#!/bin/bash
# Fetch the pinned Linear B corpus file from mwenge/linearb.xyz into the
# gitignored local cache .lbxyz_cache.js (used by parse_lbxyz.py).
# We do not redistribute this file; this script obtains it from origin.
set -e
cd "$(dirname "$0")/.."
PIN=84e0b00e
TMP=.fetch_linearb
rm -rf "$TMP"
git clone --filter=blob:none --no-checkout https://github.com/mwenge/linearb.xyz.git "$TMP"
git -C "$TMP" -c core.protectNTFS=false show "$PIN:LinearBInscriptions.js" > .lbxyz_cache.js
rm -rf "$TMP"
echo "fetched: .lbxyz_cache.js (pinned $PIN, $(wc -c < .lbxyz_cache.js) bytes)"
