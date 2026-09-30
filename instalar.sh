#!/usr/bin/env bash
# Instala o que a Vórtex Edição precisa (uma vez por máquina). macOS ou Linux.
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; cd "$R"
ok(){ printf "  ✓ %s\n" "$1"; }; falta(){ printf "  ✗ %s — %s\n" "$1" "$2"; FALTOU=1; }
FALTOU=0
echo "Conferindo dependências…"
command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 22 ] && ok "Node $(node -v)" || falta "Node 22+" "instale em nodejs.org ou 'brew install node'"
command -v ffmpeg >/dev/null && ok "ffmpeg" || falta "ffmpeg" "'brew install ffmpeg' (mac) ou 'apt install ffmpeg'"
command -v python3 >/dev/null && ok "Python 3" || falta "Python 3" "python.org"
[ "$FALTOU" = 0 ] || { echo "Instale o que falta e rode de novo."; exit 1; }

echo "Ambiente Python (numpy, scipy, soundfile, pillow)…"
python3 -m venv .venv >/dev/null 2>&1 || true
.venv/bin/pip install -q numpy scipy soundfile pillow && ok "pacotes Python em .venv/"

echo "HyperFrames (motor de render HTML → MP4)…"
npx -y hyperframes --version >/dev/null && ok "hyperframes $(npx -y hyperframes --version 2>/dev/null | tail -1)"
# o HyperFrames baixa o Chrome for Testing no 1º uso; a captura de tela reaproveita esse Chrome
[ -d "$HOME/.cache/puppeteer/chrome" ] || npx -y @puppeteer/browsers install chrome@stable --path "$HOME/.cache/puppeteer" >/dev/null
(cd captura && npm i -s >/dev/null) && ok "captura de tela (puppeteer-core)"

echo "Sons (sintetizados), fontes e logos…"
.venv/bin/python sons/gerar_sons.py sons/kit >/dev/null && ok "kit de sons em sons/kit/"
mkdir -p fonts
for w in 400 500 600 700 800; do
  [ -f fonts/inter-$w.woff2 ] || curl -sL -o fonts/inter-$w.woff2 "https://cdn.jsdelivr.net/npm/@fontsource/inter@5/files/inter-latin-$w-normal.woff2"
done; ok "fonte Inter"
bash scripts/baixar_logos.sh logos >/dev/null && ok "logos"
[ -f .env ] || cp .env.exemplo .env
echo
echo "Pronto. Opcional: coloque sua ELEVENLABS_API_KEY no .env (senão a transcrição usa o Whisper local: pip install openai-whisper)."
