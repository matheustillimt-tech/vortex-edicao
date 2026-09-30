#!/usr/bin/env python3
"""EXEMPLO: vinheta de 12 s pro SEU canal do YouTube, feita só com código (HyperFrames) + música sintetizada.

  python3 exemplos/vinheta/criar_vinheta.py --canal @seucanal --nome "Seu Nome" --bio "O que o canal ensina" \
          --linha1 "IA APLICADA" --linha2 "A NEGÓCIOS" --chip "4 vídeos por semana" [--marca sua-logo.png]

Baixa as thumbnails e a foto do canal (yt-dlp), gera a música, monta e renderiza em ~/vortex-edicao-projetos/vinheta-<canal>/.
Seções: texto cinético → parede com as thumbnails reais → sua marca com anel de luz → foto + nome + "Inscrever-se" clicado.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, wave
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("--canal", required=True); ap.add_argument("--nome", required=True); ap.add_argument("--bio", default="")
ap.add_argument("--linha1", default="SEU CANAL"); ap.add_argument("--linha2", default="EM 12 SEGUNDOS")
ap.add_argument("--chip", default="Vídeo novo toda semana"); ap.add_argument("--marca", default="")
a = ap.parse_args()
slug = re.sub(r"[^a-z0-9]+", "-", a.canal.lower()).strip("-")
AQUI = Path(os.environ.get("VORTEX_PROJETOS", Path.home() / "vortex-edicao-projetos")) / f"vinheta-{slug}"
(AQUI / "midia/thumbs").mkdir(parents=True, exist_ok=True); (AQUI / "renders").mkdir(exist_ok=True)
for arq in ("estilo.css", "ilustra.py", "ilustra.css", "masterizar.sh"):
    shutil.copy(RAIZ / "modelo" / arq, AQUI / arq)
for pasta in ("fonts", "logos"):
    shutil.copytree(RAIZ / pasta, AQUI / pasta, dirs_exist_ok=True)
shutil.copytree(RAIZ / "sons/kit", AQUI / "sons", dirs_exist_ok=True)
(AQUI / "package.json").write_text(json.dumps({"name": f"vinheta-{slug}", "private": True, "type": "module"}))
sys.path.insert(0, str(AQUI)); import ilustra as il

# thumbnails + foto do canal (yt-dlp)
url = "https://www.youtube.com/" + (a.canal if a.canal.startswith("@") else "@" + a.canal)
ids = subprocess.run(["yt-dlp", "-q", "--flat-playlist", "--playlist-end", "20", "--print", "%(id)s", url + "/videos"],
                     capture_output=True, text=True).stdout.split()
for i in ids:
    dst = AQUI / f"midia/thumbs/{i}.jpg"
    for q in ("maxresdefault", "hqdefault"):
        if not dst.exists() or dst.stat().st_size < 5000:
            subprocess.run(["curl", "-sfL", "-o", str(dst), f"https://i.ytimg.com/vi/{i}/{q}.jpg"])
if not (AQUI / "midia/canal.jpg").exists():
    subprocess.run(["yt-dlp", "-q", "--skip-download", "--write-thumbnail", "--convert-thumbnails", "jpg",
                    "--playlist-items", "0", "-o", str(AQUI / "midia/canal"), url])
if a.marca:
    shutil.copy(a.marca, AQUI / "midia/marca.png")
subprocess.run([sys.executable, str(Path(__file__).parent / "gerar_musica.py"), str(AQUI / "sons/musica.wav")], check=True)
MARCA = "midia/marca.png" if a.marca else "midia/canal.jpg"
DUR = 12.0
class Ctx:
    def __init__(self):
        self.HTML, self.JS, self.AUD, self._id = [], [], [], 0
    def nid(self, p):
        self._id += 1; return f"{p}{self._id}"
    def clip(self, de, ate, conteudo, estilo="", track=5, cls="ov"):
        i = self.nid("c")
        self.HTML.append(f'<div class="clip {cls}" data-start="{de}" data-duration="{round(ate - de, 3)}" data-track-index="{track}" style="{estilo}"><div class="in" id="{i}">{conteudo}</div></div>')
        return i
    def entra(self, sel, t, d=0.55):
        self.JS.append(f'tl.fromTo("#{sel}",{{opacity:0,y:34,scale:.92,rotationX:14,filter:"blur(14px)"}},{{opacity:1,y:0,scale:1,rotationX:0,filter:"blur(0px)",duration:{d},ease:"power3.out"}},{t});')
    def aparece(self, sel, t, d=0.42, y=24, blur=10, sc=0.94):
        self.JS.append(f'tl.fromTo("{sel}",{{opacity:0,y:{y},scale:{sc},filter:"blur({blur}px)"}},{{opacity:1,y:0,scale:1,filter:"blur(0px)",duration:{d},ease:"power3.out"}},{t});')
    def sai(self, sel, ate, n=0.28):
        self.JS.append(f'tl.to("#{sel}",{{opacity:0,scale:1.05,filter:"blur(14px)",duration:{n},ease:"power2.in"}},{round(ate - n, 3)});')
    def sfx(self, nome, t, vol=0.5, dur=None):
        with wave.open(str(AQUI / f"sons/{nome}.wav")) as w:
            d = min(dur or 99, w.getnframes() / w.getframerate())
        i = self.nid("s")
        self.AUD.append(f'<audio id="{i}" src="sons/{nome}.wav" data-start="{round(max(0, t), 3)}" data-duration="{round(d, 3)}" data-track-index="{20 + len(self.AUD)}" data-volume="{vol}"></audio>')

def youtube_tile(px=64):
    d = re.search(r'd="([^"]+)"', (AQUI / "logos/youtube.svg").read_text()).group(1)
    return f'<div class="tile" style="width:{px}px;height:{px}px;border-radius:{px*.24}px;background:#fff;display:flex;align-items:center;justify-content:center"><svg width="{px*.66}" height="{px*.66}" viewBox="0 0 24 24"><path fill="#FF0000" d="{d}"/></svg></div>'

c = Ctx()
J = c.JS.append
# música eletrônica sintetizada (gerar_musica.py), seções casadas com a vinheta
c.AUD.append('<audio id="musica" src="sons/musica.wav" data-start="0" data-duration="12" data-track-index="19" data-volume="0.9"></audio>')

# fundo preto com brilho
c.HTML.append('<div class="clip" data-start="0" data-duration="12" data-track-index="1" style="position:absolute;inset:0;background:radial-gradient(90% 70% at 50% 110%,rgba(255,255,255,.10),transparent 60%),#0a0a0a"></div>')

# ---- S1 (0–2,3 s): rótulo mono + "IA APLICADA / A NEGÓCIOS" + texto correndo ao fundo
linha = "INTELIGÊNCIA ARTIFICIAL · NEGÓCIOS · AUTOMAÇÃO · " * 4
i = c.clip(0.0, 2.35, f'<div class="marq m1">{linha}</div><div class="marq m2">{linha}</div><div class="marq m3">{linha}</div>',
           estilo="left:0;top:0;width:1920px;height:1080px")
J(f'tl.fromTo("#{i} .m1",{{x:0}},{{x:-600,duration:2.4,ease:"none"}},0);tl.fromTo("#{i} .m2",{{x:-700}},{{x:-100,duration:2.4,ease:"none"}},0);tl.fromTo("#{i} .m3",{{x:-200}},{{x:-800,duration:2.4,ease:"none"}},0);')
c.sai(i, 2.35)
i = c.clip(0.15, 2.35, f'<div class="rot-mono"><span class="tt"></span></div><div class="big w1">{a.linha1}</div><div class="big w2">{a.linha2}<i class="subl"></i></div>',
           estilo="left:0;top:330px;width:1920px;text-align:center")
J(f'(function(){{const o={{v:0}},el=document.querySelector("#{i} .tt"),s="{a.canal.upper()}";tl.to(o,{{v:s.length,duration:.55,ease:"none",onUpdate:()=>{{el.textContent=s.slice(0,Math.round(o.v))}}}},.2);tl.set(el,{{textContent:""}},0);}})();')
c.aparece(f"#{i} .w1", 0.75, y=60, blur=18, sc=1)
c.aparece(f"#{i} .w2", 1.3, y=60, blur=18, sc=1)
J(f'tl.fromTo("#{i} .subl",{{scaleX:0}},{{scaleX:1,duration:.45,ease:"power3.out"}},1.65);')
c.sai(i, 2.35)
c.sfx("digitacao_1_5s", 0.2, 0.35, dur=0.6); c.sfx("clique", 0.73, 0.5); c.sfx("clique2", 1.28, 0.5); c.sfx("swish", 1.6, 0.4)

# ---- S2 (2,2–5,7 s): parede com as thumbnails reais do canal + chip "4 vídeos por semana"
thumbs = sorted(glob.glob(str(AQUI / "midia/thumbs/*.jpg")))
imgs = [f"midia/thumbs/{Path(t).name}" for t in thumbs] * 2
i = il.parede(c, 2.2, 5.75, imgs[:20], W=1920, H=1080, colunas=5, gap=20, rot=-7)
J(f'tl.to("#{i} .parede",{{scale:1.35,x:-60,filter:"blur(10px)",duration:.5,ease:"power3.in"}},5.25);')
il.chip(c, 3.3, 5.3, 660, 470, a.chip, "YouTube", logo_html=youtube_tile(62), lado="esq", tam=1.25)

# ---- S3 (5,6–7,7 s): a marca (ou a foto do canal) com anel de luz e reflexo
i = c.clip(5.6, 7.75, f'<div class="simb"><i class="anel"></i><img src="{MARCA}"/><i class="luz"></i></div><div class="simb-rot">{a.nome.upper()}</div>',
           estilo="left:0;top:0;width:1920px;height:1080px")
J(f'tl.fromTo("#{i} .simb img",{{opacity:0,scale:.6,rotation:-40,filter:"blur(20px)"}},{{opacity:1,scale:1,rotation:0,filter:"blur(0px)",duration:.8,ease:"power4.out"}},5.65);'
  f'tl.fromTo("#{i} .anel",{{scale:.4,opacity:.9}},{{scale:2.4,opacity:0,duration:1.1,ease:"power2.out"}},5.75);'
  f'tl.fromTo("#{i} .luz",{{xPercent:-140}},{{xPercent:160,duration:.9,ease:"power2.inOut"}},6.35);'
  f'tl.fromTo("#{i} .simb-rot",{{opacity:0,scaleX:1.35,filter:"blur(8px)"}},{{opacity:1,scaleX:1,filter:"blur(0px)",duration:.7,ease:"power3.out"}},6.1);')
c.sai(i, 7.75, 0.3)
c.sfx("impacto_grave", 5.62, 0.35)

# ---- S4 (7,6–11,3 s): foto do canal + nome + "Inscrever-se" clicado pelo cursor
i = c.clip(7.6, 11.35, f'''<div class="lock">
  <div class="av"><img src="midia/canal.jpg"/></div>
  <div><div class="nome">{a.nome}</div>
  <div class="bio">{a.bio}</div>
  <div class="acoes">{youtube_tile(56)}<div class="btn"><span class="b1">Inscrever-se</span><span class="b2">{il.icone("check", 26, "#0a0a0a", 2.6)} Inscrito</span></div>
  <span class="sino">{il.icone("calendario", 1)}</span></div></div>
  <div class="cur">{il.icone("cursor", 44, "#ffffff", 1.8, "curv")}</div></div>''', estilo="left:0;top:0;width:1920px;height:1080px")
J(f'tl.fromTo("#{i} .av",{{opacity:0,scale:.5,filter:"blur(16px)"}},{{opacity:1,scale:1,filter:"blur(0px)",duration:.7,ease:"back.out(1.5)"}},7.65);')
c.aparece(f"#{i} .nome", 7.95, y=40, blur=16, sc=1)
c.aparece(f"#{i} .bio", 8.25, y=20)
c.aparece(f"#{i} .acoes", 8.5, y=20)
J(f'tl.set("#{i} .b2",{{opacity:0}},0);tl.set("#{i} .cur",{{x:1500,y:900,opacity:0}},0);'
  f'tl.to("#{i} .cur",{{opacity:1,duration:.2}},8.75);tl.to("#{i} .cur",{{x:1012,y:726,duration:.7,ease:"power3.inOut"}},8.85);'
  f'tl.fromTo("#{i} .cur",{{scale:1}},{{scale:.8,duration:.1,yoyo:true,repeat:1}},9.6);'
  f'tl.fromTo("#{i} .btn",{{scale:1}},{{scale:.93,duration:.1,yoyo:true,repeat:1}},9.6);'
  f'tl.to("#{i} .b1",{{opacity:0,y:-18,duration:.2}},9.72);tl.fromTo("#{i} .b2",{{opacity:0,y:18}},{{opacity:1,y:0,duration:.25}},9.78);'
  f'tl.to("#{i} .btn",{{backgroundColor:"rgba(255,255,255,.14)",color:"#fff",duration:.25}},9.75);'
  f'tl.to("#{i} .cur",{{x:1400,y:960,opacity:0,duration:.6,ease:"power2.in"}},10.3);')
c.sai(i, 11.35, 0.35)
c.sfx("whoosh_curto", 7.55, 0.45); c.sfx("clique", 9.58, 0.6); c.sfx("impacto_grave", 9.7, 0.35)

# ---- HUD por cima de tudo
il.hud(c, 0.0, 11.4, 1920, 1080, esq=f"{a.nome.upper()} · VINHETA", dir_="FEITO COM VÓRTEX EDIÇÃO", secao="EXEMPLO")
c.HTML.append('<div class="clip preto" id="preto" data-start="11.4" data-duration="0.6" data-track-index="9"></div>')
J('tl.fromTo("#preto",{opacity:0},{opacity:1,duration:.6,ease:"none"},11.4);')

CSS_EXTRA = """
#root{background:#0a0a0a}
.marq{position:absolute;left:0;white-space:nowrap;font:800 150px/1 "Inter";letter-spacing:-.02em;color:rgba(255,255,255,.045)}
.m1{top:40px}.m2{top:420px}.m3{top:800px}
.rot-mono{font:600 22px/1 ui-monospace,Menlo,monospace;letter-spacing:.3em;color:#a0a0a0;margin-bottom:28px;min-height:22px}
.big{font:800 150px/1 "Inter";letter-spacing:-.04em;color:#fff;text-shadow:0 0 40px rgba(255,255,255,.35),0 0 14px rgba(255,255,255,.2)}
.big.w2{position:relative;display:inline-block;margin-top:10px}
.big .subl{position:absolute;left:6px;right:6px;bottom:-18px;height:10px;border-radius:5px;background:#fff;transform-origin:left;box-shadow:0 0 22px rgba(255,255,255,.7)}
.simb{position:absolute;left:810px;top:300px;width:300px;height:312px;overflow:hidden}
.simb img{width:300px;height:312px;object-fit:contain;border-radius:24px;filter:drop-shadow(0 0 30px rgba(255,255,255,.35))}
.simb .anel{position:absolute;left:0;top:6px;width:300px;height:300px;border-radius:50%;border:3px solid #fff;box-shadow:0 0 30px rgba(255,255,255,.6)}
.simb .luz{position:absolute;inset:0;background:linear-gradient(100deg,transparent 35%,rgba(255,255,255,.55) 50%,transparent 65%);mix-blend-mode:overlay}
.simb-rot{position:absolute;left:0;width:1920px;top:680px;text-align:center;font:700 30px/1 "Inter";letter-spacing:.32em;color:#e6e6e6}
.lock{position:absolute;left:0;top:0;width:1920px;height:1080px;display:flex;align-items:center;justify-content:center;gap:56px}
.av{width:300px;height:300px;border-radius:50%;overflow:hidden;border:3px solid rgba(255,255,255,.85);box-shadow:0 0 50px rgba(255,255,255,.3)}
.av img{width:100%;height:100%;object-fit:cover}
.nome{font:800 110px/1 "Inter";letter-spacing:-.035em;color:#fff;text-shadow:0 0 36px rgba(255,255,255,.3)}
.bio{font:500 38px/1.2 "Inter";color:#a0a0a0;margin-top:14px}
.acoes{display:flex;align-items:center;gap:22px;margin-top:34px}
.btn{position:relative;height:64px;min-width:250px;border-radius:32px;background:#fff;color:#0a0a0a;font:700 28px/64px "Inter";text-align:center;box-shadow:0 0 30px rgba(255,255,255,.35);overflow:hidden}
.btn span{position:absolute;left:0;right:0;top:0;display:flex;align-items:center;justify-content:center;gap:8px}
.btn .b2{color:#fff}
.btn .b2 svg{stroke:#fff}
.sino{display:none}
.cur{position:absolute;left:0;top:0;filter:drop-shadow(0 4px 8px rgba(0,0,0,.6))}
.cur .curv path{fill:#0a0a0a;stroke:#fff}
"""
css = (AQUI / "estilo.css").read_text() + (AQUI / "ilustra.css").read_text() + CSS_EXTRA
fontes = "".join(f'@font-face{{font-family:"Inter";src:url("fonts/inter-{w}.woff2") format("woff2");font-weight:{w}}}' for w in (400, 500, 600, 700, 800))
html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script><style>{fontes}{css}</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1920" data-height="1080">
{chr(10).join(c.HTML)}
{chr(10).join(c.AUD)}
</div>
<script>const tl = gsap.timeline({{paused:true}}); tl.set({{}},{{}},{DUR});
{chr(10).join(c.JS)}
window.__timelines["main"] = tl; tl.seek(0);</script></body></html>'''
(AQUI / "index.html").write_text(html)
print("ok", len(c.HTML), "clips", len(c.AUD), "sons")

subprocess.run(["npx", "-y", "hyperframes", "render", "-o", "renders/_vinheta.mp4", "-w", "4", "--quiet"], cwd=AQUI, check=True,
               env={**os.environ, "HYPERFRAMES_SKIP_SKILLS": "1"})
subprocess.run(["bash", "masterizar.sh", "renders/_vinheta.mp4", "renders/vinheta.mp4"], cwd=AQUI, check=True)
(AQUI / "renders/_vinheta.mp4").unlink()
print("Vinheta:", AQUI / "renders/vinheta.mp4")
