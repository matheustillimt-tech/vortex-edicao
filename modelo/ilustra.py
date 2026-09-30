"""Motions ILUSTRADOS — imagem, ícone animado, print, gravação de tela e demonstração (30/09/2026).

Princípio: motion bom mostra, não só escreve. A maioria dos motions leva LOGO real, PRINT, GRAVAÇÃO de tela,
imagem gerada ou ÍCONE que se desenha — texto sozinho só no gancho e em número.
  pílula de vidro com a logo + nome; card de mídia com prévia real (print, gravação, imagem ou vídeo gerado);
  chip com ícone animado; caixa de prompt digitando; cursor clicando num print; parede de imagens; objeto em
  destaque com reflexo; moldura HUD pros trechos cinematográficos.

Serve pros dois formatos (16:9 do YouTube e 9:16 dos Reels). Coordenadas em px do quadro.
`c` = o contexto do projeto:
  • build.py: c = SimpleNamespace(clip=clip, entra=entra, aparece=aparece, sai=sai, sfx=sfx, nid=nid, JS=JS, HTML=HTML)
CSS: `ilustra.css` entra no <style> (o build.py já inclui).
Regras: toda saída é animada (sai), todo som vem do kit seco (sons/), paleta preto + branco brilhante; cor só na logo/mídia real.
"""
from pathlib import Path

def r(x):
    return round(x, 3)

# ---------- ícones de linha que SE DESENHAM (pathLength=1 → traço anima de 0 a 1) ----------
ICONES = {
    "motion": '<path d="M3 17c3-8 6-12 9-12s4 6 9 6"/><circle cx="3" cy="17" r="1.6"/><circle cx="21" cy="11" r="1.6"/>',
    "som": '<path d="M4 10v4M8 7v10M12 4v16M16 8v8M20 11v2"/>',
    "tela": '<rect x="3" y="4.5" width="18" height="12" rx="2.2"/><path d="M8.5 20h7M12 16.5V20"/>',
    "print": '<path d="M4 8V5.5A1.5 1.5 0 0 1 5.5 4H8M16 4h2.5A1.5 1.5 0 0 1 20 5.5V8M20 16v2.5a1.5 1.5 0 0 1-1.5 1.5H16M8 20H5.5A1.5 1.5 0 0 1 4 18.5V16"/>',
    "gravacao": '<rect x="3" y="6" width="13" height="12" rx="2.5"/><path d="M16 10.5l5-3v9l-5-3z"/><circle cx="7.5" cy="10" r="1.4"/>',
    "imagem": '<rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/><circle cx="9" cy="10" r="1.8"/><path d="M20.5 16l-5-5-9 8.5"/>',
    "brilho": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 16l.8 2.2 2.2.8-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z"/>',
    "check": '<path d="M5 12.5l4.2 4.2L19 7"/>',
    "raio": '<path d="M13 2.5L5 13.5h6.2L10.5 21.5l8-11h-6.2z"/>',
    "engrenagem": '<circle cx="12" cy="12" r="3.2"/><path d="M12 2.8v2.4M12 18.8v2.4M21.2 12h-2.4M5.2 12H2.8M18.5 5.5l-1.7 1.7M7.2 16.8l-1.7 1.7M18.5 18.5l-1.7-1.7M7.2 7.2L5.5 5.5"/>',
    "cursor": '<path d="M5 3l14 8-6.3 1.6L9.4 19z"/>',
    "robo": '<rect x="5" y="8" width="14" height="11" rx="3.5"/><path d="M12 4.5V8M8.5 20.5v-1.5M15.5 20.5v-1.5"/><circle cx="9.5" cy="13.2" r="1.2"/><circle cx="14.5" cy="13.2" r="1.2"/>',
    "grafico": '<path d="M4 19h16"/><path d="M6 15l4-4 3 3 5-6"/><path d="M15 8h3v3"/>',
    "dinheiro": '<rect x="2.5" y="6" width="19" height="12" rx="2.5"/><circle cx="12" cy="12" r="2.8"/>',
    "usuarios": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.6-3.6 3.3-5.5 6.5-5.5s5.9 1.9 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18.5 14.8c1.7.8 2.8 2.5 3 5.2"/>',
    "pasta": '<path d="M3 7.5A1.5 1.5 0 0 1 4.5 6H9l2 2.2h8.5A1.5 1.5 0 0 1 21 9.7v8.8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z"/>',
    "mensagem": '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/>',
    "calendario": '<rect x="3.5" y="5" width="17" height="15.5" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "seta": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "enviar": '<path d="M12 19V5M6 11l6-6 6 6"/>',
}

def icone(nome, px=40, cor="#ffffff", sw=1.8, classe="icv"):
    corpo = ICONES[nome].replace("<path ", '<path pathLength="1" ').replace("<rect ", '<rect pathLength="1" ').replace("<circle ", '<circle pathLength="1" ')
    return (f'<svg class="{classe}" width="{px}" height="{px}" viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round">{corpo}</svg>')

def desenha(c, sel, t, d=0.7, stagger=0.08):
    """Traço do ícone se desenhando (use em todo ícone que entra — ícone parado vira 'texto')."""
    c.JS.append(f'tl.fromTo("{sel} [pathLength]",{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{d},stagger:{stagger},ease:"power2.inOut"}},{r(t)});')

# ---------- pílula de vidro: logo/ícone + nome (+ subtítulo) ----------
def chip(c, de, ate, x, y, titulo, sub="", logo_html=None, icone_nome=None, lado="esq", tam=1.0):
    """Ex.: "Claude Code · Anthropic" com a logo; ou "Motion design" com ícone que se desenha.
    lado="esq"/"dir": de onde desliza."""
    vis = logo_html or f'<span class="chip-ic">{icone(icone_nome or "brilho", int(34 * tam))}</span>'
    sub_html = f'<div class="chip-sub">{sub}</div>' if sub else ""
    i = c.clip(de, ate, f'<div class="vidro chip2" style="--k:{tam}">{vis}<div><div class="chip-tit">{titulo}</div>{sub_html}</div></div>',
               estilo=f"left:{x}px;top:{y}px")
    dx = -70 if lado == "esq" else 70
    c.JS.append(f'tl.fromTo("#{i}",{{opacity:0,x:{dx},scale:.9,filter:"blur(12px)"}},{{opacity:1,x:0,scale:1,filter:"blur(0px)",duration:.55,ease:"power3.out"}},{r(de)});')
    if not logo_html:
        desenha(c, f"#{i}", de + 0.15)
    c.JS.append(f'tl.fromTo("#{i} .chip-tit",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.5,ease:"power2.out"}},{r(de + 0.18)});')
    c.sfx("whoosh_curto", de - 0.08, 0.35)
    c.sai(i, ate)
    return i

# ---------- card de mídia: prévia REAL + rótulo com ícone ----------
def card_midia(c, de, ate, x, y, w, midia, rotulo, icone_nome=None, razao=16 / 9, media_start=0.0, ken=True, lado="esq"):
    """Print / gravação de tela / imagem gerada / vídeo gerado dentro de um card de vidro com rótulo.
    midia .png/.jpg/.webp → <img> com Ken Burns lento; .mp4/.mov → <video> por cima do card (regra do HF:
    vídeo não pode ficar dentro de clip com tempo; vira clip próprio, alinhado ao card)."""
    pad, h = 14, round((w - 28) / razao)
    video = Path(midia).suffix.lower() in (".mp4", ".mov", ".webm")
    icone_nome = icone_nome or ("gravacao" if video else "imagem")
    slot = (f'<div class="midia" style="width:{w - 2 * pad}px;height:{h}px">'
            + ("" if video else f'<img class="kb" src="{midia}"/>') + '</div>')
    i = c.clip(de, ate, f'<div class="vidro cardm" style="width:{w}px;padding:{pad}px {pad}px 12px">{slot}'
                        f'<div class="cardm-rot">{icone(icone_nome, 24)}<span>{rotulo}</span></div></div>',
               estilo=f"left:{x}px;top:{y}px")
    dx = -60 if lado == "esq" else 60
    c.JS.append(f'tl.fromTo("#{i}",{{opacity:0,x:{dx},y:20,scale:.92,rotationY:{-10 if lado == "esq" else 10},filter:"blur(14px)"}},'
                f'{{opacity:1,x:0,y:0,scale:1,rotationY:0,filter:"blur(0px)",duration:.6,ease:"power3.out"}},{r(de)});')
    desenha(c, f"#{i} .cardm-rot", de + 0.3)
    if ken and not video:
        c.JS.append(f'tl.fromTo("#{i} .kb",{{scale:1.0}},{{scale:1.08,duration:{r(ate - de)},ease:"none"}},{r(de)});')
    if video:
        vid = c.nid("mv")
        c.HTML.append(f'<video id="{vid}" class="clip" src="{midia}" muted playsinline data-start="{r(de)}" data-duration="{r(ate - de)}" '
                      f'data-media-start="{r(media_start + 0.001)}" data-track-index="7" '
                      f'style="position:absolute;left:{x + pad}px;top:{y + pad}px;width:{w - 2 * pad}px;height:{h}px;object-fit:cover;border-radius:14px;z-index:6"></video>')
        c.JS.append(f'tl.fromTo("#{vid}",{{opacity:0,x:{dx},y:20}},{{opacity:1,x:0,y:0,duration:.6,ease:"power3.out"}},{r(de)});'
                    f'tl.to("#{vid}",{{opacity:0,duration:.28,ease:"power2.in"}},{r(ate - 0.28)});')
    c.sfx("whoosh_curto", de - 0.08, 0.35)
    c.sai(i, ate)
    return i

# ---------- caixa de prompt digitando ----------
def prompt(c, de, ate, x, y, w, texto, t_ini, t_fim, modelo_html="", modelo_nome=""):
    """Prompt sendo digitado letra a letra (casado com a fala), caret piscando e o botão de enviar "apertado" no fim."""
    i = c.clip(de, ate, f'<div class="vidro prompt" style="width:{w}px"><div class="prompt-txt"><span class="ptx"></span><i class="caret"></i></div>'
                        f'<div class="prompt-pe"><span class="prompt-mod">{modelo_html}<span>{modelo_nome}</span></span>'
                        f'<span class="prompt-btn">{icone("enviar", 22, "#0a0a0a", 2.4, "icv")}</span></div></div>',
               estilo=f"left:{x}px;top:{y}px")
    c.entra(i, de)
    txt = texto.replace("\\", "\\\\").replace('"', '\\"')
    c.JS.append(f'(function(){{const o={{v:0}},el=document.querySelector("#{i} .ptx"),s="{txt}";'
                f'tl.to(o,{{v:s.length,duration:{r(max(0.4, t_fim - t_ini))},ease:"none",onUpdate:()=>{{el.textContent=s.slice(0,Math.round(o.v))}}}},{r(t_ini)});'
                f'tl.set(el,{{textContent:""}},0);}})();')
    c.JS.append(f'tl.fromTo("#{i} .caret",{{opacity:1}},{{opacity:0,duration:.45,repeat:{max(1, int((ate - de) / 0.9))},yoyo:true,ease:"steps(1)"}},{r(de)});')
    c.JS.append(f'tl.fromTo("#{i} .prompt-btn",{{scale:1}},{{scale:.82,duration:.12,yoyo:true,repeat:1,ease:"power2.inOut"}},{r(t_fim + 0.15)});')
    d = t_fim - t_ini
    c.sfx("digitacao_1_5s" if d <= 1.5 else "digitacao_2_5s", t_ini, 0.45, dur=min(d, 2.5))
    c.sfx("clique", t_fim + 0.15, 0.45)
    c.sai(i, ate)
    return i

# ---------- demonstração: print numa janela + cursor andando e clicando ----------
def demo(c, de, ate, x, y, w, print_src, larg_img, alt_img, passos, url="", zoom=None):
    """Mostra o PASSO A PASSO que ele fala ("entra em Configurações e ativa tal função").
    passos = [(t, px, py, "move"|"clique"), ...] em px da IMAGEM (larg_img × alt_img).
    zoom = [(t, px, py, escala), ...] opcional: a imagem aproxima do ponto dentro da janela.
    Clique = anel + som seco. Nada é clicado de verdade em conta nenhuma: é motion sobre o print."""
    h = round(w * alt_img / larg_img); k = w / larg_img
    i = c.clip(de, ate, f'<div class="vidro janela" style="width:{w + 20}px">'
                        f'<div class="jan-barra"><i></i><i></i><i></i><span>{url}</span></div>'
                        f'<div class="jan-corpo" style="width:{w}px;height:{h}px"><div class="jan-cena" style="width:{w}px;height:{h}px"><img class="jan-img" src="{print_src}" style="width:{w}px;height:{h}px"/>'
                        f'<div class="jan-anel"></div><div class="jan-cursor">{icone("cursor", 34, "#ffffff", 1.8, "cur")}</div></div></div></div>',
               estilo=f"left:{x}px;top:{y}px")
    c.entra(i, de)
    x0, y0 = (passos[0][1] * k, passos[0][2] * k) if passos else (w / 2, h / 2)
    c.JS.append(f'tl.set("#{i} .jan-cursor",{{x:{r(x0)},y:{r(y0 + 60)},opacity:0}},0);tl.to("#{i} .jan-cursor",{{opacity:1,duration:.25}},{r(de + 0.35)});')
    for t, px, py, acao in passos:
        c.JS.append(f'tl.to("#{i} .jan-cursor",{{x:{r(px * k)},y:{r(py * k)},duration:.55,ease:"power3.inOut"}},{r(t - 0.55)});')
        if acao == "clique":
            c.JS.append(f'tl.fromTo("#{i} .jan-cursor",{{scale:1}},{{scale:.82,duration:.1,yoyo:true,repeat:1}},{r(t)});'
                        f'tl.fromTo("#{i} .jan-anel",{{x:{r(px * k - 30)},y:{r(py * k - 30)},scale:.3,opacity:1}},{{scale:1.5,opacity:0,duration:.55,ease:"power2.out"}},{r(t)});')
            c.sfx("clique", t - 0.02, 0.5)
    for t, px, py, s in (zoom or []):
        c.JS.append(f'tl.to("#{i} .jan-cena",{{transformOrigin:"{r(px * k)}px {r(py * k)}px",scale:{s},duration:.7,ease:"power3.inOut"}},{r(t)});')
    c.sfx("whoosh_curto", de - 0.08, 0.35)
    c.sai(i, ate)
    return i

# ---------- parede de imagens (thumbnails, prints, resultados) ----------
def parede(c, de, ate, imagens, W=1920, H=1080, colunas=5, gap=18, rot=-8):
    """Parede de imagens reais entrando em cascata com leve 3D. Ex.: thumbs do canal, prints de resultado."""
    cw = (W * 1.1 - gap * (colunas - 1)) / colunas; ch = cw * 9 / 16
    cel = "".join(f'<img class="pw" src="{s}" style="width:{r(cw)}px;height:{r(ch)}px"/>' for s in imagens)
    i = c.clip(de, ate, f'<div class="parede" style="width:{W * 1.1}px;gap:{gap}px;transform:rotate({rot}deg)">{cel}</div>',
               estilo=f"left:{-W * 0.05}px;top:{H * 0.5 - ch * 1.6}px", cls="ov fundo-cena")
    c.JS.append(f'tl.fromTo("#{i} .pw",{{opacity:0,y:80,rotationX:35,scale:.8}},{{opacity:1,y:0,rotationX:0,scale:1,duration:.55,stagger:{{each:.035,from:"center"}},ease:"power3.out"}},{r(de)});'
                f'tl.fromTo("#{i} .parede",{{scale:1.08}},{{scale:1,duration:{r(ate - de)},ease:"none"}},{r(de)});')
    c.sfx("whoosh", de - 0.1, 0.45)
    c.sai(i, ate)
    return i

# ---------- objeto em destaque (imagem gerada sem fundo ou com fundo escuro) ----------
def objeto(c, de, ate, x, y, w, src, rotulo=""):
    """Imagem ilustrativa (ex.: gerada por IA, fundo escuro) flutuando + reflexo de luz passando."""
    rot = f'<div class="obj-rot">{rotulo}</div>' if rotulo else ""
    i = c.clip(de, ate, f'<div class="obj" style="width:{w}px"><img src="{src}" style="width:{w}px"/><i class="obj-luz"></i>{rot}</div>',
               estilo=f"left:{x}px;top:{y}px")
    c.JS.append(f'tl.fromTo("#{i}",{{opacity:0,y:60,scale:.85,rotationY:-18,filter:"blur(16px)"}},{{opacity:1,y:0,scale:1,rotationY:0,filter:"blur(0px)",duration:.7,ease:"power3.out"}},{r(de)});'
                f'tl.fromTo("#{i} img",{{y:0}},{{y:-14,duration:{r((ate - de) / 2)},yoyo:true,repeat:1,ease:"sine.inOut"}},{r(de)});'
                f'tl.fromTo("#{i} .obj-luz",{{xPercent:-120}},{{xPercent:220,duration:1.1,ease:"power2.inOut"}},{r(de + 0.5)});')
    c.sfx("impacto_grave", de - 0.05, 0.4)
    c.sai(i, ate)
    return i

# ---------- moldura HUD pros trechos cinematográficos em tela cheia ----------
def hud(c, de, ate, W, H, esq="VÓRTEX EDIÇÃO · MOTION", dir_="1080P · 30", secao=""):
    """Cantos, rótulos em fonte mono e barra de progresso. Use SÓ por cima de cena em tela cheia."""
    i = c.clip(de, ate, f'<div class="hud" style="width:{W}px;height:{H}px"><b class="c1"></b><b class="c2"></b><b class="c3"></b><b class="c4"></b>'
                        f'<span class="h-esq">{esq}</span><span class="h-dir">{dir_}</span><span class="h-sec">{secao}</span>'
                        f'<div class="h-barra"><i></i></div></div>', estilo="left:0;top:0", track=9)
    c.JS.append(f'tl.fromTo("#{i}",{{opacity:0}},{{opacity:1,duration:.3}},{r(de)});'
                f'tl.fromTo("#{i} .h-barra i",{{scaleX:0}},{{scaleX:1,duration:{r(ate - de)},ease:"none"}},{r(de)});')
    c.sai(i, ate, 0.25)
    return i
