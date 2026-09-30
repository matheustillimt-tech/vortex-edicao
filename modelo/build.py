#!/usr/bin/env python3
"""3º passo: a EDIÇÃO. Gera o index.html do HyperFrames (e o partes.json do render rápido) a partir da fala.

Tudo ACIMA de "LINHA DO TEMPO" são ferramentas prontas; a LINHA DO TEMPO é o que se escreve a cada vídeo,
ancorando cada motion na palavra falada com W("frase").

Ferramentas principais
  W("frase", apos, fim=False)   → segundo (já no vídeo cortado) em que a frase começa (ou termina)
  clip / entra / aparece / sai  → elementos na linha do tempo; TODO elemento sai com animação (sai)
  conta + contador_som          → número contando enquanto é falado
  tile("claude"|"codex"|"instagram"|"youtube"|"tiktok"|"whatsapp") → logo real no formato de ícone
  zoom(de, ate, cx, cy, escala, lento=False) · zoom_seq(...) → zoom na gravação (a câmera volta por cima, sem zoom)
  circulo(de, ate, t_risca, cx, cy, w, h) → círculo limpo em volta de um número/botão da tela
  cena(de, ate)                 → fundo de tela cheia (vidro escuro) com a câmera em janelinha
  il.chip / il.card_midia / il.prompt / il.demo / il.parede / il.objeto / il.hud → motions ILUSTRADOS (ilustra.py)
  sfx(nome, t, vol)             → efeito do kit (sons/): whoosh, whoosh_curto, clique, clique2, swish, impacto_grave...
Coordenadas em px de 1920×1080. Pra achar um ponto da tela:
  ffmpeg -ss T -i media/base.mp4 -frames:v 1 -vf "drawgrid=w=100:h=100:c=red@0.5" grade.png
"""
import json, re, unicodedata
from pathlib import Path
AQUI = Path(__file__).parent
PAL = json.load(open(AQUI / "media/palavras_saida.json"))
# config.json: onde fica a webcam na gravação (px em 1920×1080) — ou "webcam": null se não houver.
CFG = json.load(open(AQUI / "config.json")) if (AQUI / "config.json").exists() else {"webcam": None}
WEBCAM = CFG.get("webcam")            # {"x":1467,"y":324,"w":453,"h":726}
FUNDO_GRAVACAO = CFG.get("fundo_gravacao", "#0a0a0a")   # cor atrás da webcam (tampa durante o zoom)
import subprocess as _sp
DUR = round(float(_sp.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(AQUI / "media/base.mp4")],capture_output=True,text=True).stdout), 3)
FPS = 30

def _n(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))

TOK = [_n(p["w"]) for p in PAL]

def W(frase, apos=0.0, fim=False):
    """Tempo (s, saída) em que a sequência de palavras começa (ou termina, fim=True) depois de `apos`."""
    alvo = [_n(x) for x in frase.split()]
    for i in range(len(PAL)):
        if PAL[i]["t"] < apos - 0.05:
            continue
        if TOK[i:i + len(alvo)] == alvo:
            return PAL[i + len(alvo) - 1]["f"] if fim else PAL[i]["t"]
    raise SystemExit(f"palavra não encontrada: {frase!r} depois de {apos}")

def svgpath(nome):
    return re.search(r'd="([^"]+)"', (AQUI / f"logos/{nome}.svg").read_text()).group(1)

# ---------- logos (tiles no formato de ícone de app) ----------
def tile(nome, px=84):
    r = int(px * 0.24)
    base = f'class="tile" style="width:{px}px;height:{px}px;border-radius:{r}px;'
    g = int(px * 0.58)
    if nome == "claude":
        return f'<div {base}background:#D97757"><svg width="{g}" height="{g}" viewBox="0 0 24 24"><path fill="#fff" d="{svgpath("claude")}"/></svg></div>'
    if nome == "codex":
        return f'<div {base}background:#fff;overflow:hidden"><img src="logos/codex.png" style="width:100%;height:100%"/></div>'
    if nome == "instagram":
        return (f'<div {base}background:radial-gradient(circle at 30% 107%,#fdf497 0%,#fdf497 5%,#fd5949 45%,#d6249f 60%,#285AEB 90%)">'
                f'<svg width="{g}" height="{g}" viewBox="0 0 24 24"><path fill="#fff" d="{svgpath("instagram")}"/></svg></div>')
    if nome == "youtube":
        return f'<div {base}background:#fff"><svg width="{int(px*.66)}" height="{int(px*.66)}" viewBox="0 0 24 24"><path fill="#FF0000" d="{svgpath("youtube")}"/></svg></div>'
    if nome == "tiktok":
        p = svgpath("tiktok")
        return (f'<div {base}background:#000"><svg width="{g}" height="{g}" viewBox="-1 -1 26 26">'
                f'<path fill="#25F4EE" transform="translate(-0.7,-0.5)" d="{p}"/><path fill="#FE2C55" transform="translate(0.7,0.5)" d="{p}"/>'
                f'<path fill="#fff" d="{p}"/></svg></div>')
    if nome == "whatsapp":
        return f'<div {base}background:#25D366"><svg width="{g}" height="{g}" viewBox="0 0 24 24"><path fill="#fff" d="{svgpath("whatsapp")}"/></svg></div>'
    raise KeyError(nome)

# ---------- ícones de linha ----------
IC = {
    "comentario": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    "usuarios": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.6-3.6 3.3-5.5 6.5-5.5s5.9 1.9 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18.5 14.8c1.7.8 2.8 2.5 3 5.2"/>',
    "dinheiro": '<rect x="2.5" y="6" width="19" height="12" rx="2.5"/><circle cx="12" cy="12" r="2.8"/><path d="M6 9.5v5M18 9.5v5"/>',
    "check": '<path d="M5 12.5l4.2 4.2L19 7"/>',
    "sino": '<path d="M6 16V11a6 6 0 1 1 12 0v5l1.6 2H4.4z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
    "cerebro": '<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375M6.003 5.125A3 3 0 0 0 6.401 6.5M3.477 10.896a4 4 0 0 1 .585-.396M19.938 10.5a4 4 0 0 1 .585.396M6 18a4 4 0 0 1-1.967-.516M19.967 17.484A4 4 0 0 1 18 18"/>',
    "agente": '<rect x="5" y="8" width="14" height="11" rx="3.5"/><path d="M12 4.5V8M8.5 20.5v-1.5M15.5 20.5v-1.5"/><circle cx="9.5" cy="13.2" r="1.2"/><circle cx="14.5" cy="13.2" r="1.2"/><path d="M3 12.5v2.5M21 12.5v2.5"/><circle cx="12" cy="3.6" r="1"/>',
    "calendario": '<rect x="3.5" y="5" width="17" height="15.5" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "tarefas": '<rect x="4" y="3.5" width="16" height="17" rx="3"/><path d="M8 9l1.6 1.6L12.5 7.7M8 15l1.6 1.6 2.9-2.9M14.5 9.5H17M14.5 15.5H17"/>',
    "raio": '<path d="M13 2.5L5 13.5h6.2L10.5 21.5l8-11h-6.2z"/>',
    "codigo": '<path d="M8.5 7.5L4 12l4.5 4.5M15.5 7.5L20 12l-4.5 4.5M13.2 5l-2.4 14"/>',
    "tela": '<rect x="3" y="4.5" width="18" height="12" rx="2.2"/><path d="M8.5 20h7M12 16.5V20"/>',
    "video": '<rect x="3" y="6" width="13" height="12" rx="2.5"/><path d="M16 10.5l5-3v9l-5-3z"/>',
    "empresa": '<path d="M4 20.5V8l8-4.5 8 4.5v12.5"/><path d="M9 20.5v-5h6v5M8 11h.01M12 11h.01M16 11h.01"/>',
    "carrossel": '<rect x="6" y="4" width="12" height="16" rx="2"/><path d="M3 7v10M21 7v10"/>',
    "enviar": '<path d="M21 3.5L10.5 14M21 3.5l-6.5 17-4-6.5-6.5-4z"/>',
    "alvo": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1"/>',
}
def ic(nome, px=40, cor="currentColor", sw=1.8):
    return f'<svg class="ic" width="{px}" height="{px}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{IC[nome]}</svg>'

# ---------- montagem ----------
HTML, JS, AUD = [], [], []
_id = [0]
def nid(p):
    _id[0] += 1
    return f"{p}{_id[0]}"

def r3(x): return round(x, 3)

import wave
def _durwav(nome):
    with wave.open(str(AQUI / f"sons/{nome}.wav")) as w:
        return w.getnframes() / w.getframerate()

def sfx(nome, t, vol=0.5, dur=None):
    i = nid("s")
    d = min(dur or 99, _durwav(nome))
    AUD.append(f'<audio id="{i}" src="sons/{nome}.wav" data-start="{r3(max(0, t))}" data-duration="{r3(d)}" data-track-index="{20 + len(AUD)}" data-volume="{vol}"></audio>')

def clip(de, ate, conteudo, cls="ov", estilo="", track=5):
    """Um clip na linha do tempo. Retorna o id do elemento interno (.in), que é o que se anima."""
    i = nid("c")
    HTML.append(f'<div class="clip {cls}" data-start="{r3(de)}" data-duration="{r3(ate - de)}" data-track-index="{track}" style="{estilo}">'
                f'<div class="in" id="{i}">{conteudo}</div></div>')
    return i

def entra(sel, t, tipo="vidro", d=0.55):
    if tipo == "vidro":
        JS.append(f'tl.fromTo("#{sel}",{{opacity:0,y:34,scale:.92,rotationX:14,filter:"blur(14px)"}},{{opacity:1,y:0,scale:1,rotationX:0,filter:"blur(0px)",duration:{d},ease:"power3.out"}},{r3(t)});')
    elif tipo == "fade":
        JS.append(f'tl.fromTo("#{sel}",{{opacity:0,filter:"blur(10px)"}},{{opacity:1,filter:"blur(0px)",duration:{d},ease:"power2.out"}},{r3(t)});')

def sai(sel, ate, n=0.28):
    """Saída animada obrigatória: fade + blur + leve escala, terminando no fim do clip."""
    JS.append(f'tl.to("#{sel}",{{opacity:0,scale:1.05,filter:"blur(14px)",duration:{n},ease:"power2.in"}},{r3(ate - n)});')

def aparece(sel, t, d=0.45, y=24, blur=10, sc=0.94):
    JS.append(f'tl.fromTo("{sel}",{{opacity:0,y:{y},scale:{sc},filter:"blur({blur}px)"}},{{opacity:1,y:0,scale:1,filter:"blur(0px)",duration:{d},ease:"power3.out"}},{r3(t)});')

def conta(sel, t0, t1, a, b, prefixo="", sufixo="", casas=0):
    JS.append(f'(function(){{const o={{v:{a}}},el=document.querySelector("{sel}");'
              f'tl.to(o,{{v:{b},duration:{r3(max(0.3, t1 - t0))},ease:"power2.out",onUpdate:()=>{{el.textContent="{prefixo}"+o.v.toLocaleString("pt-BR",{{minimumFractionDigits:{casas},maximumFractionDigits:{casas}}})+"{sufixo}"}}}},{r3(t0)});'
              f'tl.set(el,{{textContent:"{prefixo}{a:,}{sufixo}".replace(/,/g,".")}},0);}})();')

def contador_som(t0, t1, vol=1.0):
    d = t1 - t0
    arq = "contador_1_5s" if d <= 1.5 else "contador_2_5s" if d <= 2.5 else "contador_3_5s"
    sfx(arq, t0, vol, dur=min(d + 0.05, 3.5))

ZOOMS = []
CAMZ = []   # zooms na câmera cheia (sem PiP) — também contam como trecho com motion
def _alvo(cx, cy, s):
    cx = min(max(cx, 960 / s), 1920 - 960 / s)
    cy = min(max(cy, 540 / s), 1080 - 540 / s)
    return f"scale:{s},x:{r3((960 - cx) * s)},y:{r3((540 - cy) * s)}"

def zoom(de, ate, cx, cy, s, n=0.7, pip=True, lento=False, n_out=None):
    """Zoom no palco em volta de (cx, cy) (px de 1920×1080). lento=True: push-in contínuo até o fim.
    pip=True: a câmera volta por cima, sem zoom (tela gravada). pip=False: trecho de câmera cheia."""
    n_out = n_out or n
    if pip and WEBCAM: ZOOMS.append((de, ate)); tampa(de, ate)
    else: CAMZ.append((de, ate))
    n_in = (ate - de - n_out) if lento else n
    ease = "sine.inOut" if lento else "power3.inOut"
    JS.append(f'tl.fromTo("#palco",{{scale:1,x:0,y:0}},{{{_alvo(cx, cy, s)},duration:{r3(n_in)},ease:"{ease}",immediateRender:false}},{r3(de)});'
              f'tl.to("#palco",{{scale:1,x:0,y:0,duration:{r3(n_out)},ease:"power3.inOut"}},{r3(ate - n_out)});')

def zoom_seq(de, ate, alvos, n=0.7):
    """Zoom que passeia: alvos = [(t, cx, cy, s), ...]; o primeiro entra em `de`."""
    if WEBCAM: ZOOMS.append((de, ate)); tampa(de, ate)
    else: CAMZ.append((de, ate))
    t, cx, cy, s = alvos[0]
    JS.append(f'tl.fromTo("#palco",{{scale:1,x:0,y:0}},{{{_alvo(cx, cy, s)},duration:{n},ease:"power3.inOut",immediateRender:false}},{r3(de)});')
    for t, cx, cy, s in alvos[1:]:
        JS.append(f'tl.to("#palco",{{{_alvo(cx, cy, s)},duration:{n},ease:"power3.inOut"}},{r3(t)});')
    JS.append(f'tl.to("#palco",{{scale:1,x:0,y:0,duration:{n},ease:"power3.inOut"}},{r3(ate - n)});')

PALCO = []
def tampa(de, ate):
    """Cobre a webcam ORIGINAL dentro do palco durante o zoom — senão ela aumenta junto com a tela e aparece duas vezes."""
    PALCO.append(f'<div class="clip tampa" data-start="{r3(de)}" data-duration="{r3(ate - de)}" data-track-index="4"></div>')
def circulo(de, ate, t_risca, cx, cy, w, h, cor="#ffffff"):
    """Círculo limpo (geométrico, não rabisco) em volta de uma informação da TELA. Fica dentro do #palco,
    então acompanha o zoom. Desenha em 0,5 s a partir de t_risca e sai com fade no fim."""
    import math
    i = nid("o"); m = 16
    W_, H_ = w + 2 * m, h + 2 * m
    pts = []
    for k in range(91):
        a = math.radians(-160 + k * 4.1)          # ~370°: fecha passando um pouco do início
        g = 1 + 0.035 * k / 90                     # abre de leve no fim, sem virar espiral
        pts.append(f"{W_/2 + (w/2) * g * math.cos(a):.1f},{H_/2 + (h/2) * g * math.sin(a):.1f}")
    PALCO.append(f'<div class="clip circ" data-start="{r3(de)}" data-duration="{r3(ate - de)}" data-track-index="4" '
                 f'style="left:{r3(cx - W_/2)}px;top:{r3(cy - H_/2)}px;width:{W_}px;height:{H_}px">'
                 f'<svg class="in" id="{i}" width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}"><polyline points="{" ".join(pts)}" pathLength="1" '
                 f'style="stroke:{cor}"/></svg></div>')
    JS.append(f'tl.fromTo("#{i} polyline",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:.5,ease:"power2.inOut"}},{r3(t_risca)});')
    sai(i, ate, 0.3)
    sfx("swish", t_risca - 0.05, 0.55)

CENAS = []
def cena(de, ate):
    """Cena em tela cheia (fundo escuro com brilho). A câmera continua visível em janelinha."""
    CENAS.append((de, ate))
    i = clip(de, ate, '<div class="aro a1"></div><div class="aro a2"></div><div class="grade"></div>', cls="fundo", track=3)
    JS.append(f'tl.fromTo("#{i}",{{opacity:0,scale:1.08,filter:"blur(18px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.45,ease:"power3.out"}},{r3(de)});')
    JS.append(f'tl.fromTo("#{i} .a1",{{rotation:-8}},{{rotation:8,duration:{r3(ate-de)},ease:"none"}},{r3(de)});')
    sai(i, ate, 0.32)
    sfx("whoosh", de - 0.12, 0.55)


# =====================================================================================
# LINHA DO TEMPO — EXEMPLO. Apague e escreva a do SEU vídeo, ancorada na fala com W("frase").
# =====================================================================================
import sys as _sys; _sys.path.insert(0, str(AQUI))
import ilustra as il
from types import SimpleNamespace as _NS
c = _NS(clip=clip, entra=entra, aparece=aparece, sai=sai, sfx=sfx, nid=nid, JS=JS, HTML=HTML)

t0 = PAL[0]["t"] if PAL else 0.3
# pílulas com logo real, uma de cada lado (ex.: quando a pessoa fala "Claude Code" e "Codex":
#   t = W("claude code"); il.chip(c, t - 0.1, t + 3, 60, 260, "Claude Code", "Anthropic", logo_html=tile("claude", 58))
il.chip(c, t0 + 0.2, t0 + 3.2, 60, 260, "Claude Code", "Anthropic", logo_html=tile("claude", 58))
il.chip(c, t0 + 0.6, t0 + 3.2, 1100, 180, "Codex", "OpenAI", logo_html=tile("codex", 58), lado="dir")
# chip com ícone que se desenha
il.chip(c, t0 + 3.6, t0 + 6.4, 60, 300, "Motion design", icone_nome="motion")
# prompt digitando junto com a fala
il.prompt(c, t0 + 6.8, t0 + 10.4, 550, 760, 820, "Edita meu vídeo com motions, prints e sons discretos", t0 + 7.2, t0 + 9.4,
          modelo_html=tile("claude", 30), modelo_nome="Claude")
# push-in lento na gravação
zoom(t0 + 11, min(DUR - 0.5, t0 + 15), 760, 460, 1.25, lento=True)
# card com um print (gere com: node captura/capturar.mjs print <url> midia/print.png)
if (AQUI / "midia/print.png").exists():
    il.card_midia(c, t0 + 15.5, t0 + 19, 60, 160, 620, "midia/print.png", "Print", icone_nome="print")

# ---- PiP da câmera (sem zoom) durante zooms e cenas
for de, ate, k in sorted([(a, b, "c") for a, b in ZOOMS] + [(a, b, "c") for a, b in CENAS]):
    i = nid("pip")
    HTML.append(f'<video id="{i}" class="clip pip {k}" src="media/base.mp4" muted playsinline data-start="{r3(de)}" data-duration="{r3(ate - de)}" data-media-start="{r3(de)}" data-track-index="8"></video>')
for de, ate in sorted(CENAS + ZOOMS):
    i = clip(de, ate, "", cls="moldura", track=9)
    JS.append(f'tl.fromTo("#{i}",{{opacity:0}},{{opacity:1,duration:.4}},{r3(de)});')
    sai(i, ate, 0.3)

# =====================================================================================
if WEBCAM:
    _x, _y, _w, _h = WEBCAM["x"], WEBCAM["y"], WEBCAM["w"], WEBCAM["h"]
    CSS_WEBCAM = (f".pip.c{{clip-path:inset({_y + 6}px {max(0, 1920 - _x - _w) + 20}px {max(0, 1080 - _y - _h) + 6}px {_x + 6}px round 26px)}}"
                  f".moldura>.in{{position:absolute;left:{_x + 6}px;top:{_y + 6}px;width:{_w - 26}px;height:{_h - 12}px;border-radius:26px;border:2px solid rgba(255,255,255,.5);box-shadow:0 0 40px rgba(255,255,255,.28)}}"
                  f".tampa{{position:absolute;left:{_x}px;top:{_y}px;width:{_w}px;height:{_h}px;background:{FUNDO_GRAVACAO};z-index:1}}")
else:
    CSS_WEBCAM = ""
CSS = (AQUI / "estilo.css").read_text() + (AQUI / "ilustra.css").read_text() + CSS_WEBCAM
FONTES = "".join(f'@font-face{{font-family:"Inter";src:url("fonts/inter-{w}.woff2") format("woff2");font-weight:{w};font-style:normal}}' for w in (400, 500, 600, 700, 800))
html = f'''<!doctype html>
<html lang="pt-BR" data-resolution="landscape">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1920, height=1080" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{FONTES}{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1920" data-height="1080">
  <div id="palco"><video id="base" class="clip" src="media/base.mp4" muted playsinline data-start="0" data-duration="{DUR}" data-track-index="0"></video>{chr(10).join(PALCO)}</div>
  {chr(10).join(HTML)}
  <audio id="trilha" src="sons/trilha.wav" data-start="0" data-duration="{DUR}" data-track-index="11" data-volume="0.16"></audio>
  <audio id="voz" src="media/voz.wav" data-start="0" data-duration="{DUR}" data-track-index="10" data-volume="1"></audio>
  {chr(10).join(AUD)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set({{}}, {{}}, {DUR});
tl.set("#palco", {{scale:1,x:0,y:0}}, 0);
{chr(10).join(JS)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>'''
(AQUI / "index.html").write_text(html)
print(f"index.html · {len(HTML)} clips · {len(AUD)} efeitos · {len(ZOOMS)} zooms · {len(CENAS)} cenas")

# ---- partes.json: insumo do render rápido (render_rapido.py) — só re-renderiza os trechos com motion que mudaram
TRILHA = '<audio id="trilha" src="sons/trilha.wav" data-start="0" data-duration="%s" data-track-index="11" data-volume="0.16"></audio>' % DUR
VOZ = '<audio id="voz" src="media/voz.wav" data-start="0" data-duration="%s" data-track-index="10" data-volume="1"></audio>' % DUR
json.dump({"dur": DUR, "fps": FPS, "estilo": FONTES + CSS, "palco": PALCO, "html": HTML, "js": JS,
           "audio": [TRILHA, VOZ] + AUD, "zooms_camera": CAMZ}, open(AQUI / "partes.json", "w"), ensure_ascii=False)
