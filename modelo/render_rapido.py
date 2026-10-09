#!/usr/bin/env python3
"""Render rápido do HyperFrames, com a mesma qualidade.

1. PARALELO: cada trecho renderiza com --workers N (vários Chromes ao mesmo tempo).
2. SÓ ONDE TEM MOTION: os trechos sem nenhum motion saem direto do base.mp4 (ffmpeg), sem passar pelo navegador.
3. CACHE: cada trecho com motion vira um HTML próprio; o hash dele é a chave do cache. Num ajuste, só os trechos
   que mudaram renderizam de novo.
No fim: UMA compressão só (x264 CRF 16, preset slow) juntando tudo + áudio mixado no ffmpeg (mesmos
data-start/data-duration/data-volume do index.html) + master −14 LUFS / −1 dBTP.

Pré-requisito: python3 build.py (gera index.html e partes.json).
Uso:
  python3 render_rapido.py -o renders/final.mp4 [--workers 4]
  python3 render_rapido.py --so-trechos        # só renderiza/atualiza o cache dos trechos com motion
"""
import argparse, hashlib, json, math, os, re, subprocess, sys, time
from pathlib import Path

AQUI = Path(__file__).parent
CACHE = AQUI / "renders" / ".trechos"
RE_T = re.compile(r'data-start="([\d.]+)"\s+data-duration="([\d.]+)"')

def janelas(p, junta, margem):
    iv = []
    for h in p["palco"] + p["html"]:
        m = RE_T.search(h)
        if m:
            a, d = float(m.group(1)), float(m.group(2)); iv.append((a, a + d))
    iv += [tuple(z) for z in p["zooms_camera"]]
    iv.sort(); out = []
    for a, b in iv:
        a, b = max(0.0, a - margem), min(p["dur"], b + margem)
        if out and a - out[-1][1] < junta: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    fps = p["fps"]; tot = round(p["dur"] * fps)
    fr = []
    for a, b in out:
        A, B = max(0, math.floor(a * fps)), min(tot, math.ceil(b * fps))
        if fr and A <= fr[-1][1]: fr[-1][1] = max(fr[-1][1], B)
        else: fr.append([A, B])
    # trecho com no máximo ~90 s: senão o HyperFrames enche o disco com os quadros extraídos da mídia
    MAX = int(90 * fps); sep = []
    for A, B in fr:
        while B - A > MAX:
            sep.append([A, A + MAX]); A += MAX
        sep.append([A, B])
    return sep, tot

def desloca(h, a):
    # Clip que começou ANTES do trecho ganhava data-start negativo, e o HyperFrames o mantinha visível pela
    # duração inteira a partir do 0 (ex.: painel vazio aparecendo fora de hora). Corrige cortando o clip no
    # início do trecho: data-start = 0, duração encurtada e data-media-start avançado no mesmo tanto.
    corte = [0.0]
    def f(m):
        s, d = float(m.group(1)) - a, float(m.group(2))
        if s < 0: corte[0], s, d = -s, 0.0, d + s
        return f'data-start="{round(s, 4)}" data-duration="{round(d, 4)}"'
    h = RE_T.sub(f, h, count=1)
    if corte[0]:
        h = re.sub(r'data-media-start="([\d.]+)"', lambda m: f'data-media-start="{round(float(m.group(1)) + corte[0], 4)}"', h, count=1)
    # +1 ms no início da mídia: o arredondamento do corte (ex. 36,2333 s) fazia pegar o quadro anterior em alguns quadros
    return re.sub(r'data-media-start="([\d.]+)"', lambda m: f'data-media-start="{round(float(m.group(1)) + 0.001, 4)}"', h)

def dentro(h, a, b):
    m = RE_T.search(h)
    if not m: return False
    s, d = float(m.group(1)), float(m.group(2))
    return s < b and s + d > a

def posicoes(linha):
    return [float(x) for x in re.findall(r',(-?[\d.]+)\);', linha)]

def html_trecho(p, A, B):
    fps = p["fps"]; a, b = A / fps, B / fps; dur = round((B - A) / fps, 4)
    palco = [desloca(h, a) for h in p["palco"] if dentro(h, a, b)]
    html = [desloca(h, a) for h in p["html"] if dentro(h, a, b)]
    # entram as animações dentro do trecho E as que começaram antes dele (clip cortado no início ou trecho
    # dividido em 90 s), mas só de elementos que existem no trecho (senão o querySelector volta null e quebra a página)
    ids = set(re.findall(r'id="([^"]+)"', "".join(palco + html)))
    def ok(l):
        ref = re.findall(r'\("#([\w-]+)', l)   # alvo do tween/querySelector (cor "#fff" fica de fora)
        if ref and not all(x in ids or x in ("palco", "base", "root") for x in ref): return False
        ps = posicoes(l)
        return any(a - 1e-3 <= t <= b + 1e-3 for t in ps) or (ref and any(t <= b + 1e-3 for t in ps))
    js = [l for l in p["js"] if ok(l)]
    return f'''<!doctype html>
<html lang="pt-BR" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{p["estilo"]}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1920" data-height="1080">
  <div id="palco"><video id="base" class="clip" src="media/base.mp4" muted playsinline data-start="0" data-duration="{dur}" data-media-start="{round(a + 0.001, 4)}" data-track-index="0"></video>{"".join(palco)}</div>
  {chr(10).join(html)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set({{}}, {{}}, {p["dur"]});
tl.set("#palco", {{scale:1,x:0,y:0}}, 0);
{chr(10).join(js)}
const trecho = gsap.timeline({{ paused: true }});
trecho.add(tl.tweenFromTo({round(a, 4)}, {round(b, 4)}, {{ ease: "none" }}));
window.__timelines["main"] = trecho;
trecho.seek(0);
</script>
</body>
</html>'''

def renderiza_trechos(p, fr, workers):
    CACHE.mkdir(parents=True, exist_ok=True)
    # a versão dos arquivos de mídia e fontes entra no hash (trocou a base ou um logo → renderiza de novo)
    assinatura = "".join(f"{f}:{os.path.getmtime(f)}" for f in sorted(map(str, list(AQUI.glob("media/base.mp4")) + list(AQUI.glob("logos/*")) + list(AQUI.glob("fonts/*")))))
    arquivos, novos = [], 0
    for k, (A, B) in enumerate(fr):
        h = html_trecho(p, A, B)
        chave = hashlib.sha1((h + assinatura).encode()).hexdigest()[:16]
        out = CACHE / f"{A:06d}_{B:06d}_{chave}.mp4"
        arquivos.append(out)
        if out.exists():
            continue
        novos += 1
        tmp = AQUI / f"_trecho_{chave}.html"
        tmp.write_text(h)
        t0 = time.time()
        r = subprocess.run(["npx", "-y", "hyperframes", "render", "-c", tmp.name, "-o", str(out), "-w", str(workers), "--crf", "8", "--quiet"],
                           cwd=AQUI, env={**os.environ, "HYPERFRAMES_SKIP_SKILLS": "1"}, capture_output=True, text=True)
        tmp.unlink(missing_ok=True)
        import glob as _g, shutil as _sh, tempfile as _tf   # cache de quadros extraídos: libera o disco a cada trecho
        for d in _g.glob(os.path.join(_tf.gettempdir(), "hyperframes-extract-cache-*")):
            _sh.rmtree(d, ignore_errors=True)
        if r.returncode != 0 or not out.exists():
            sys.exit(f"falhou no trecho {A}-{B}:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
        n = int(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v", "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.strip())
        if n == B - A + 1:
            # duração em float (ex. 13,0667 s × 30 = 392,001): o HyperFrames arredonda pra cima → tira o quadro extra do fim
            aparado = out.with_suffix(".tmp.mp4")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-map", "0", "-frames:v", str(B - A), "-c", "copy", str(aparado)], check=True)
            aparado.replace(out)
            n = B - A
        if n != B - A:
            out.unlink(); sys.exit(f"trecho {A}-{B}: {n} quadros, esperado {B - A}")
        print(f"  trecho {k + 1}/{len(fr)} ({(B - A) / p['fps']:.1f} s) em {time.time() - t0:.0f} s", flush=True)
    print(f"{novos} trecho(s) renderizado(s), {len(fr) - novos} do cache")
    return arquivos

def mixa_audio(p, saida):
    ins, fil = [], []
    for k, h in enumerate(p["audio"]):
        src = re.search(r'src="([^"]+)"', h).group(1)
        s = float(re.search(r'data-start="([\d.]+)"', h).group(1))
        d = float(re.search(r'data-duration="([\d.]+)"', h).group(1))
        v = float(re.search(r'data-volume="([\d.]+)"', h).group(1))
        ins += ["-i", str(AQUI / src)]
        ms = round(s * 1000)
        ch = int(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=channels", "-of", "csv=p=0", str(AQUI / src)], capture_output=True, text=True).stdout.split()[0])
        # igual ao mixer do HyperFrames (engine/services/audioMixer.ts): mono vai pros 2 canais SEM os −3 dB do rematrix padrão
        estereo = "pan=stereo|c0=c0|c1=c0" if ch == 1 else "aformat=channel_layouts=stereo"
        fil.append(f"[{k}:a]aresample=48000,{estereo},atrim=0:{d},volume={v},adelay={ms}|{ms},apad,asetpts=N/SR/TB,atrim=0:{p['dur']}[a{k}]")
    n = len(p["audio"])
    fil.append("".join(f"[a{k}]" for k in range(n)) + f"amix=inputs={n}:duration=longest:dropout_transition=0,volume={n}[mix]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(fil), "-map", "[mix]", "-c:a", "pcm_s24le", str(saida)], check=True)

def junta(p, fr, tot, arquivos, saida_video):
    pecas, cur = [], 0
    for (A, B), f in zip(fr, arquivos):
        if A > cur: pecas.append(("base", cur, A))
        pecas.append(("trecho", A, B, f)); cur = B
    if cur < tot: pecas.append(("base", cur, tot))
    ins, fil, idx = ["-i", str(AQUI / "media/base.mp4")], [], 1
    for k, pc in enumerate(pecas):
        if pc[0] == "base":
            fil.append(f"[0:v]trim=start_frame={pc[1]}:end_frame={pc[2]},setpts=PTS-STARTPTS[v{k}]")
        else:
            ins += ["-i", str(pc[3])]; fil.append(f"[{idx}:v]setpts=PTS-STARTPTS[v{k}]"); idx += 1
    fil.append("".join(f"[v{k}]" for k in range(len(pecas))) + f"concat=n={len(pecas)}:v=1:a=0,fps={p['fps']}[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(fil), "-map", "[v]",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(saida_video)], check=True)
    base = sum(pc[2] - pc[1] for pc in pecas if pc[0] == "base")
    print(f"{len(pecas)} peças · {base / tot * 100:.0f}% do vídeo saiu direto da base (sem navegador)")

def master(video, audio, saida):
    J = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(audio), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    d = json.loads(J[J.rindex("{"):J.rindex("}") + 1])
    af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
          f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", af, "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(saida)], check=True)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--saida", default="renders/final.mp4")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--junta", type=float, default=2.0, help="junta trechos com motion separados por menos de X s")
    ap.add_argument("--margem", type=float, default=0.2)
    ap.add_argument("--so-trechos", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    p = json.load(open(AQUI / "partes.json"))
    fr, tot = janelas(p, a.junta, a.margem)
    mot = sum(B - A for A, B in fr)
    print(f"{len(fr)} trechos com motion = {mot / tot * 100:.0f}% do vídeo ({mot / p['fps']:.0f} s de {tot / p['fps']:.0f} s)")
    arquivos = renderiza_trechos(p, fr, a.workers)
    if a.so_trechos: sys.exit(0)
    (AQUI / "renders").mkdir(exist_ok=True)
    vid, aud = AQUI / "renders" / "_video.mp4", AQUI / "renders" / "_audio.wav"
    junta(p, fr, tot, arquivos, vid)
    mixa_audio(p, aud)
    master(vid, aud, AQUI / a.saida)
    vid.unlink(); aud.unlink()
    print(f"Final: {AQUI / a.saida} · {time.time() - t0:.0f} s no total")
