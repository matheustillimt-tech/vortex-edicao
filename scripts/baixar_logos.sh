#!/usr/bin/env bash
# Baixa logos reais pros motions. Regra: toda empresa/rede citada no vídeo entra com a LOGO REAL
# (site oficial ou Simple Icons) — nunca desenhe "parecido". Uso: bash scripts/baixar_logos.sh <pasta>
set -euo pipefail
D="${1:-logos}"; mkdir -p "$D"
for i in claude openai anthropic instagram youtube tiktok whatsapp x linkedin google gmail notion github stripe; do
  [ -f "$D/$i.svg" ] || curl -sfL -o "$D/$i.svg" "https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/$i.svg" || true
done
# Codex: ícone oficial da página openai.com/codex
[ -f "$D/codex.png" ] || curl -sL -o "$D/codex.png" "https://images.ctfassets.net/kftzwdyauwt9/77tJ5U1tgxHMZflZ5m4Z24/ace4d8b6ad200d87ebcb69c466344343/Blossom_4k_Icon_1.png?w=800" || true
echo "logos em $D"
