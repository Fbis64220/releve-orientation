#!/usr/bin/env sh
# Assemble la page autonome index.html à partir de src/app.html.
set -e
cd "$(dirname "$0")"
{
  printf '<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  printf '<style>[hidden]{display:none!important}body{margin:0}</style>\n</head>\n<body>\n'
  cat src/app.html
  printf '\n</body>\n</html>\n'
} > index.html
echo "index.html généré."
