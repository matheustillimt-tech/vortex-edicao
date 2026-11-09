#!/usr/bin/env bash
# Etapa 1 · Referência: baixa um vídeo do YouTube e deixa tudo pronto pro Claude analisar.
# Uso: bash scripts/referencia.sh <url-do-youtube> [pasta-de-saida]
# Gera: info.txt (título, canal, views, score), capitulos.txt, transcricao.txt,
#       folha-abertura.jpg (1 quadro a cada 2 s no 1º minuto) e folha-NN.jpg (1 quadro a cada 6 s no resto).
set -euo pipefail
URL="${1:?uso: bash scripts/referencia.sh <url-do-youtube> [pasta]}"
command -v yt-dlp >/dev/null || { echo "Falta o yt-dlp: 'brew install yt-dlp' (mac) ou 'pip install yt-dlp'"; exit 1; }
command -v ffmpeg >/dev/null || { echo "Falta o ffmpeg: 'brew install ffmpeg' (mac) ou 'apt install ffmpeg'"; exit 1; }
ID=$(yt-dlp --get-id "$URL")
OUT="${2:-${VORTEX_PROJETOS:-$HOME/vortex-edicao-projetos}/_referencias/$ID}"
mkdir -p "$OUT"; cd "$OUT"

echo "→ dados do vídeo"
yt-dlp --skip-download -j "$URL" > info.json
echo "→ legenda (a do autor ou a automática)"
yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "pt.*,en.*" --sub-format vtt -o ref "$URL" >/dev/null 2>&1 || true
echo "→ vídeo em 720p (só pra tirar os quadros)"
yt-dlp -q -f "bv*[height<=720]+ba/b[height<=720]" --merge-output-format mp4 -o ref.mp4 "$URL"

python3 -I - <<'PY'
import json, re, glob
d = json.load(open("info.json"))
ins = d.get("channel_follower_count") or 0
views = d.get("view_count") or 0
score = f"{views/ins:.1f}×" if ins else "?"
open("info.txt", "w").write(
    f"Título: {d['title']}\nCanal: {d.get('channel')} ({ins} inscritos)\nViews: {views}\n"
    f"Score (views ÷ inscritos): {score}\nDuração: {d['duration']//60}:{d['duration']%60:02d}\n"
    f"Publicado: {d.get('upload_date')}\n\nDescrição:\n{d.get('description','')}\n")
open("capitulos.txt", "w").write("\n".join(
    f"{int(c['start_time'])//60:02d}:{int(c['start_time'])%60:02d} {c['title']}" for c in d.get("chapters") or []))
subs = sorted(glob.glob("ref*.vtt"), key=lambda p: ("pt" not in p, p))
linhas, ultima = [], ""
if subs:
    for b in open(subs[0]).read().split("\n\n"):
        m = re.search(r"(\d\d):(\d\d):(\d\d)\.\d+ -->", b)
        if not m: continue
        t = re.sub(r"<[^>]+>|&nbsp;", "", " ".join(l for l in b.split("\n") if "-->" not in l)).strip()
        if t and t != ultima:
            s = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])
            linhas.append(f"[{s//60:02d}:{s%60:02d}] {t}"); ultima = t
open("transcricao.txt", "w").write("\n".join(linhas) or "(o vídeo não tem legenda: transcreva o ref.mp4 com o transcrever.py)")
print(f"score {score} · {len(linhas)} linhas de transcrição")
PY

echo "→ folhas de quadros"
ffmpeg -loglevel error -y -t 60 -i ref.mp4 -vf "fps=1/2,scale=320:-1,tile=6x5" -frames:v 1 folha-abertura.jpg
ffmpeg -loglevel error -y -ss 60 -i ref.mp4 -vf "fps=1/6,scale=320:-1,tile=6x4" folha-%02d.jpg
echo "Pronto: $OUT"
echo "Próximo passo: o Claude lê info.txt, capitulos.txt e transcricao.txt, OLHA as folhas e escreve REFERENCIA.md (guia/REFERENCIA.md)."
