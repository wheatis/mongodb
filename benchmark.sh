#!/usr/bin/env bash
KEY="testkey"
URL="http://127.0.0.1:5000/data/$KEY"

echo "1) Requête cold cache (attente 2 s)…"
time curl -s $URL | jq

echo
echo "2) Requête warm cache (attente quasi nulle)…"
time curl -s $URL | jq
