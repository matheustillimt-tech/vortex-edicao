#!/usr/bin/env bash
# Masteriza o áudio do render do HyperFrames em -14 LUFS / -1 dBTP (2 passadas) sem recodificar o vídeo.
# Uso: bash masterizar.sh renders/video.mp4 renders/video_final.mp4
set -euo pipefail
IN="$1"; OUT="$2"
J=$(ffmpeg -hide_banner -i "$IN" -vn -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
read -r I TP LRA TH OFF <<<"$(echo "$J" | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")"
ffmpeg -y -loglevel error -i "$IN" -map 0:v -map 0:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true" \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart "$OUT"
echo "Final: $OUT"
