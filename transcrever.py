#!/usr/bin/env python3
"""1º passo: prepara a gravação e transcreve palavra a palavra.

Uso:  python3 transcrever.py <gravacao.mp4> <pasta_do_projeto>
Gera em <projeto>/fonte/:
  video.mp4      a gravação inteira em 1920×1080, 30 fps constante
  voz.wav        a voz normalizada em -18 LUFS (mono, 48 kHz)
  palavras.json  [{"w": palavra, "t": início, "f": fim}, ...] no tempo da gravação
  roteiro.txt    a fala com tempo, frase por frase — é o que se LÊ pra achar erros e repetições

Transcrição: ElevenLabs Scribe se houver ELEVENLABS_API_KEY (no ambiente ou no .env da raiz do repositório);
senão, Whisper local (pip install openai-whisper). Idioma padrão pt (mude com --idioma en, es...).
"""
import argparse, json, os, shutil, subprocess, sys, urllib.request, uuid
from pathlib import Path

RAIZ = Path(__file__).parent

def sh(cmd):
    subprocess.run(cmd, check=True)

def chave_elevenlabs():
    k = os.environ.get("ELEVENLABS_API_KEY")
    env = RAIZ / ".env"
    if not k and env.exists():
        for l in env.read_text().splitlines():
            if l.startswith("ELEVENLABS_API_KEY="):
                k = l.split("=", 1)[1].strip().strip('"')
    return k

def normaliza_voz(src, dst):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-vn", "-af", "loudnorm=I=-18:TP=-2:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"): r.stderr.rfind("}") + 1])
    af = (f"highpass=f=70,loudnorm=I=-18:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vn", "-af", af, "-ar", "48000", "-ac", "1", str(dst)])

def palavras(bruto):
    d = json.load(open(bruto)); out = []
    if isinstance(d, dict) and "words" in d:            # ElevenLabs
        out = [{"w": w["text"].strip(), "t": w["start"], "f": w["end"]} for w in d["words"] if w.get("type", "word") == "word"]
    elif isinstance(d, dict) and "segments" in d:       # Whisper
        out = [{"w": w["word"].strip(), "t": w["start"], "f": w["end"]} for s in d["segments"] for w in s.get("words", [])]
    return [dict(p, t=round(p["t"], 3), f=round(p["f"], 3)) for p in out if p["w"]]

def transcreve(voz, pasta, idioma):
    k = chave_elevenlabs()
    if k:
        print("Transcrevendo com ElevenLabs Scribe…")
        lim = "----" + uuid.uuid4().hex; corpo = b""
        cod = {"pt": "por", "en": "eng", "es": "spa"}.get(idioma, idioma)
        for a, v in {"model_id": "scribe_v1", "language_code": cod, "timestamps_granularity": "word", "tag_audio_events": "false"}.items():
            corpo += f"--{lim}\r\nContent-Disposition: form-data; name=\"{a}\"\r\n\r\n{v}\r\n".encode()
        corpo += (f"--{lim}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"voz.wav\"\r\nContent-Type: audio/wav\r\n\r\n".encode()
                  + Path(voz).read_bytes() + f"\r\n--{lim}--\r\n".encode())
        req = urllib.request.Request("https://api.elevenlabs.io/v1/speech-to-text", data=corpo,
                                     headers={"xi-api-key": k, "Content-Type": f"multipart/form-data; boundary={lim}"})
        (pasta / "transcricao_bruta.json").write_bytes(urllib.request.urlopen(req, timeout=1800).read())
        return palavras(pasta / "transcricao_bruta.json")
    if shutil.which("whisper"):
        print("Transcrevendo com Whisper local (modelo small)…")
        sh(["whisper", str(voz), "--model", "small", "--language", idioma, "--word_timestamps", "True",
            "--output_format", "json", "--output_dir", str(pasta)])
        return palavras(pasta / (Path(voz).stem + ".json"))
    sys.exit("Sem ELEVENLABS_API_KEY e sem Whisper. Crie o .env ou rode: pip install openai-whisper")

def roteiro(pal):
    linhas, cur = [], []
    for i, p in enumerate(pal):
        cur.append(p)
        pausa = pal[i + 1]["t"] - p["f"] if i + 1 < len(pal) else 9
        if p["w"][-1:] in ".?!" or pausa > 0.6:
            linhas.append(f'[{cur[0]["t"]:8.2f} – {cur[-1]["f"]:8.2f}]  ' + " ".join(x["w"] for x in cur)); cur = []
    return "\n".join(linhas) + "\n"

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("gravacao"); ap.add_argument("projeto"); ap.add_argument("--idioma", default="pt")
    a = ap.parse_args()
    fonte = Path(a.projeto) / "fonte"; fonte.mkdir(parents=True, exist_ok=True)
    print("Vídeo em 1080p/30 fps…")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", a.gravacao, "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30",
        "-an", "-c:v", "libx264", "-crf", "16", "-g", "15", "-pix_fmt", "yuv420p", str(fonte / "video.mp4")])
    print("Voz em -18 LUFS…"); normaliza_voz(a.gravacao, fonte / "voz.wav")
    pal = transcreve(fonte / "voz.wav", fonte, a.idioma)
    json.dump(pal, open(fonte / "palavras.json", "w"), ensure_ascii=False)
    (fonte / "roteiro.txt").write_text(roteiro(pal))
    print(f"Pronto: {len(pal)} palavras. Leia {fonte / 'roteiro.txt'} e anote os trechos a remover (erros, repetições).")
