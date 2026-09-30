#!/usr/bin/env bash
# Cria a pasta de um vídeo novo com tudo que a edição precisa.  Uso: bash novo_projeto.sh <nome> [gravacao.mp4]
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; N="$1"; P="${VORTEX_PROJETOS:-$HOME/vortex-edicao-projetos}/$N"
mkdir -p "$P/midia" "$P/renders"
cp "$R"/modelo/{build.py,estilo.css,ilustra.py,ilustra.css,render_rapido.py,masterizar.sh} "$P/"
[ -f "$P/config.json" ] || cp "$R/config.exemplo.json" "$P/config.json"
cp -R "$R/fonts" "$R/logos" "$P/"
mkdir -p "$P/sons"; cp "$R"/sons/kit/*.wav "$P/sons/"          # cópia (o HyperFrames não serve link simbólico de mídia)
cat > "$P/package.json" <<J
{ "name": "$N", "private": true, "type": "module" }
J
echo '{ "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json" }' > "$P/hyperframes.json"
echo "Projeto: $P"
if [ -n "${2:-}" ]; then
  "$R/.venv/bin/python" "$R/transcrever.py" "$2" "$P"
  echo "Agora leia $P/fonte/roteiro.txt e rode: python3 $R/cortar.py $P --remover <trechos com erro>"
fi
