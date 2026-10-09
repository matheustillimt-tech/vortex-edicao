# KIT DE CENAS E DEMONSTRAÇÕES (opcional) · Vórtex Edição · MIT © Grupo Vórtex
#
# Não é importado direto: o build.py liga o kit com  cn = carrega_cenas()  e aí se usa  cn.cena(...), cn.agua(...).
# Ele roda com as ferramentas do build.py (clip, sfx, conta, tile, JS, HTML, CAMZ, PALCO, W...) e acrescenta:
#
#   cena(de, ate, titulo, plano, passos)  → cena branca em tela cheia; o "plano" é largo e a câmera virtual corre por ele
#   no_plano(i, html) · injeta(i, html)    → põe objetos no plano (correm) ou fixos na cena (não correm)
#   corre(i, t, k) · X(k) · mostra(i, sel, t) · selo(cls, x, y) + check(i, sel, t)   → objeto em passos, câmera correndo, check no fim
#   agua(i, pts, t0, dur)                  → gráfico que ENCHE como água num copo (área com degradê + linha)
#   barras(i, itens, t0) · pontos(i, n, t0, t1) · risca(i, sel, t) + riscavel(texto, cls)
#   cel(inner) + topo_app(nome) + bolhas(i, msgs) + notif(i, t, ...)   → celular com conversa chegando e notificação
#   term(i, prompt, t0, t1, saidas)        → terminal digitando o prompt e devolvendo as saídas com ✓
#   bate(t)                                → zoom seco na palavra forte, CENTRADO NO ROSTO (o rosto só cresce, escala ≤ 1,10)
#   num_lado(...)                          → número contando ao lado do rosto (ao lado do rosto, só logo, número e inscrição)
#   letreiro(de, ate, linhas, x, y)        → lettering das frases-chave do início (2 a 5 palavras do núcleo)
#   lower_third(de, ate, t_nome, nome, credenciais) → nome + credenciais com logo, linha que se desenha
#   broll(de, ate, arquivo, card=False)   → b-roll em tela cheia ou num card (baixe grátis: scripts/broll_pexels.py)
#   borrar(de, ate, x, y, w, h)            → borra um dado sensível da tela gravada (acompanha o zoom)
#   E(nome, px)                            → emoji (ou o seu ícone PNG em midia/icones/<nome>.png, se existir)
#   checa_ritmo()                          → avisa cena colada em cena (≥ 8 s de rosto entre elas) e cobertura total
#
# Princípios (o que vira motion e o que NÃO vira): guia/MOTIONS.md. Antes de renderizar: python3 checa_texto.py
#
# Configuração (config.json do projeto):
#   "rosto": [x, y]   centro do rosto na câmera cheia, em px de 1920×1080. Meça num quadro com grade.
#   "marca": {"destaque": "#1d7cf2", "fonte": "Inter"}   cor de destaque e fonte (o seu design system)
import re as _re
DESTAQUE = (CFG.get("marca") or {}).get("destaque", "#1d7cf2")   # cor de destaque da cena branca (config.json → marca)

# ---------- emoji / ícone próprio ----------
EMO = {"dinheiro": "💰", "notas": "💸", "robo": "🤖", "celular": "📱", "notebook": "💻", "grafico": "📈", "caindo": "📉",
       "calendario": "📅", "relogio": "⏰", "alvo": "🎯", "raio": "⚡", "fogo": "🔥", "check": "✅", "x": "❌", "alerta": "⚠️",
       "cadeado": "🔒", "escudo": "🛡️", "cartao": "💳", "suporte": "🎧", "bug": "🐞", "ferramenta": "🛠️", "pessoa": "🧑‍💼",
       "equipe": "👥", "predio": "🏢", "loja": "🏪", "restaurante": "🍽️", "papel": "📝", "sacola": "🛍️", "pensando": "🤔",
       "foguete": "🚀", "trofeu": "🏆", "aperto": "🤝", "lampada": "💡", "contrato": "📄", "cofre": "🏦", "balanca": "⚖️",
       "sino": "🔔", "olhos": "👀", "megafone": "📣", "casa": "🏠", "conversa": "💬", "caixa": "📦", "livros": "📚"}

def E(nome, px=96, cls=""):
    """Emoji do sistema (Apple Color Emoji no Mac). Se existir midia/icones/<nome>.png, usa o seu ícone
    (renderizado em fundo branco: entra com mix-blend-mode multiply)."""
    png = AQUI / f"midia/icones/{nome}.png"
    if png.exists():
        q = int(px * 1.6)
        return f'<img class="cn-i3 {cls}" src="midia/icones/{nome}.png" style="width:{q}px;height:{q}px">'
    return f'<span class="cn-emo {cls}" style="font-size:{px}px">{EMO.get(nome, nome)}</span>'

# ---------- sons (todos do kit sintetizado) ----------
def _som(nome, t, vol=.4, dur=None, reserva="clique2"):
    sfx(nome if (AQUI / f"sons/{nome}.wav").exists() else reserva, t, vol, dur)

def check_som(t): _som("check", t - .02, .5)

# ---------- avisos ----------
def aviso(txt, t=None):
    MISS.append(f"{txt}" + (f" (em {t:.1f} s)" if t is not None else ""))

# ---------- título pequeno que entra junto com a fala ----------
def _acha(plano, apos):
    alvo = [_n(x) for x in plano.split()]
    for k in range(len(PAL)):
        if PAL[k]["t"] < apos - 0.05: continue
        if TOK[k:k + len(alvo)] == alvo: return k
    return None

def _titulo(frase_html, apos):
    """frase_html = 1 a 4 palavras, <em>…</em> = destaque. Cada palavra entra cinza e escurece quando é dita;
    se a frase não é dita (título inventado, o normal), entra em sequência no início da cena."""
    toks = []
    for parte in _re.split(r"(<em>.*?</em>)", frase_html):
        if not parte: continue
        az = parte.startswith("<em>")
        toks += [(w, az) for w in _re.sub(r"</?em>", "", parte).split()]
    if len(toks) > 4: aviso(f"título com {len(toks)} palavras (máx. 4): {frase_html!r}")
    k = _acha(" ".join(w for w, _ in toks), apos)
    tempos = [PAL[k + j]["t"] for j in range(len(toks))] if k is not None else None
    html = ('<div class="cn-tit">' + "&nbsp;".join(f'<span class="cn-w cn-w{j}">{w}</span>' for j, (w, _) in enumerate(toks)) + "</div>")
    return html, tempos, [az for _, az in toks]

# ---------- cena branca com plano que corre ----------
PASSO = 1500                       # distância entre um objeto e o próximo no plano largo
CENAS_B = []

def cena(de, ate, titulo="", plano="", passos=1, fixo="", longa=False):
    """Cena branca em tela cheia (fundo radial com vinheta cinza). Fica no FIM do raciocínio, 5 a 7 s.
    plano = objetos posicionados no plano largo (passo k centrado em X(k)); a câmera anda com corre().
    fixo = o que não corre com o plano (cursor, título fixo). longa=True: demonstração contínua (sem aviso)."""
    if ate - de > 7.05 and not longa: aviso(f"cena de {ate - de:.1f} s (padrão 5 a 7 s; use longa=True numa demonstração)", de)
    CENAS_B.append((de, ate))
    i = nid("cn")
    tt, tempos, azs = _titulo(titulo, de - 8.0) if titulo else ("", None, [])
    HTML.append(f'<div class="clip cn-cena" data-start="{r3(de)}" data-duration="{r3(ate - de)}" data-track-index="10">'
                f'<div class="in" id="{i}"><div class="cn-plano" style="width:{max(1, passos) * PASSO + 1920}px">{plano}</div>{tt}{fixo}</div></div>')
    JS.append(f'tl.fromTo("#{i}",{{opacity:0,scale:1.04}},{{opacity:1,scale:1,duration:.35,ease:"power2.out"}},{r3(de)});'
              f'tl.to("#{i}",{{opacity:0,duration:.25,ease:"power2.in"}},{r3(ate - 0.25)});')
    for j, az in enumerate(azs):
        t = tempos[j] if tempos else de + 0.2 + j * 0.12
        JS.append(f'tl.fromTo("#{i} .cn-w{j}",{{opacity:0,y:6}},{{opacity:1,y:0,duration:.12}},{r3(t - .05)});'
                  f'tl.to("#{i} .cn-w{j}",{{color:"{DESTAQUE if az else "#111111"}",duration:.3}},{r3(t + .08)});')
    _som("whoosh_curto", de - 0.15, 0.4)
    return i

def X(k, dx=0):
    """x (px) do centro do passo k no plano largo."""
    return 960 + k * PASSO + dx

def corre(i, t, k, som=True):
    """A câmera virtual corre pro passo k: o plano anda pra esquerda e o objeto anterior sai pela borda."""
    JS.append(f'tl.to("#{i} .cn-plano",{{x:{-k * PASSO},duration:.75,ease:"power3.inOut"}},{r3(t - .12)});')
    if som: _som("swish", t - .14, .35)

def mostra(i, sel, t, y=24, sc=.85, stagger=0, som=True):
    """Objeto (ou grupo, com stagger) entrando com mola."""
    st = f",stagger:{stagger}" if stagger else ""
    JS.append(f'tl.fromTo("#{i} {sel}",{{opacity:0,y:{y},scale:{sc}}},{{opacity:1,y:0,scale:1,duration:.32,ease:"back.out(1.8)"{st}}},{r3(t - .04)});')
    if som: _som("clique2", t - .03, .35)

def selo(cls, x, y, ok=True, d=88):
    """Selo redondo ✓ (verde) ou ✕ (vermelho), escondido até o check()."""
    cor = "#16a34a" if ok else "#ef4444"
    return (f'<div class="cn-selo {cls}" style="left:{x}px;top:{y}px;width:{d}px;height:{d}px;background:{cor};'
            f'font-size:{int(d * .56)}px;box-shadow:0 12px 28px {cor}55">{"✓" if ok else "✕"}</div>')

def check(i, sel, t):
    """O passo que fecha o raciocínio: selo pulando no objeto principal + som de "deu certo"."""
    JS.append(f'tl.fromTo("#{i} {sel}",{{opacity:0,scale:0,rotation:-90}},{{opacity:1,scale:1,rotation:0,duration:.4,ease:"back.out(2.4)"}},{r3(t)});')
    check_som(t)

def pulsa(i, sel, t, rep=1):
    JS.append(f'tl.to("#{i} {sel}",{{scale:1.06,duration:.25,yoyo:true,repeat:{rep},ease:"sine.inOut"}},{r3(t)});')

def no_plano(i, html):
    """Põe objetos no plano largo da cena i (os que correm com corre()). Use depois de cena(), porque os
    componentes (agua, term, bolhas...) precisam do id da cena pra animar."""
    for k in range(len(HTML) - 1, -1, -1):
        if f'id="{i}">' in HTML[k]:
            HTML[k] = _re.sub(r'(<div class="cn-plano"[^>]*>)', lambda m: m.group(1) + html, HTML[k], count=1); return

def injeta(i, html):
    """Põe conteúdo dentro de um clip já criado (quando o html precisa do id do clip pra ser montado)."""
    for k in range(len(HTML) - 1, -1, -1):
        if f'id="{i}">' in HTML[k]:
            HTML[k] = HTML[k].replace(f'id="{i}">', f'id="{i}">' + html, 1); return

# ---------- gráficos que provam ----------
def agua(i, pts, t0, dur, x=260, y=300, w=1400, h=520, cor=None, cls="ag", base=None):
    """Gráfico que ENCHE como água num copo: área com degradê + linha, revelados da esquerda pra direita,
    com o nível subindo devagar. pts = [(x 0–1, altura 0–1), ...]. Retorna o html (ponha no plano da cena)."""
    base = h if base is None else base
    cor = cor or DESTAQUE
    P = [(px * w, base - py * (h - 20)) for px, py in pts]
    d = "M" + " L".join(f"{a:.0f} {b:.0f}" for a, b in P)
    area = d + f" L{P[-1][0]:.0f} {base} L{P[0][0]:.0f} {base} Z"
    g = nid("gd")
    svg = (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;overflow:visible">'
           f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{cor}" stop-opacity=".55"/>'
           f'<stop offset="1" stop-color="{cor}" stop-opacity=".06"/></linearGradient></defs>'
           f'<g class="{cls}lv" style="transform-origin:0 {base}px"><path d="{area}" fill="url(#{g})"/><path class="{cls}wv" d="{area}" fill="{cor}" opacity=".10"/></g>'
           f'<path d="{d}" fill="none" stroke="{cor}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    JS.append(f'tl.fromTo("#{i} .{cls}rv",{{width:0}},{{width:{w + 20},duration:{r3(dur)},ease:"sine.inOut"}},{r3(t0)});'
              f'tl.fromTo("#{i} .{cls}lv",{{scaleY:.15}},{{scaleY:1,duration:{r3(dur)},ease:"power1.out"}},{r3(t0)});'
              f'tl.fromTo("#{i} .{cls}wv",{{x:-30}},{{x:30,duration:.9,yoyo:true,repeat:{max(1, int(dur / .9) + 2)},ease:"sine.inOut",immediateRender:false}},{r3(t0)});')
    _som("contador_1_5s", t0, .3, dur=min(1.4, dur))
    return f'<div class="{cls}rv" style="position:absolute;left:{x}px;top:{y}px;height:{h + 30}px;width:0;overflow:hidden">{svg}</div>'

def barras(i, itens, t0, passo=.35, alt=440, x=360, y=330, w=1200, larg=150):
    """Barras crescendo: itens = [(rótulo, valor 0–1, cor)]."""
    cols = "".join(f'<div class="cn-bc"><div class="cn-bt"><i class="cn-bi cn-bi{k}" style="background:linear-gradient(180deg,{c_},{c_}55);'
                   f'height:{v_ * alt:.0f}px;width:{larg}px"></i></div><span>{lab}</span></div>' for k, (lab, v_, c_) in enumerate(itens))
    for k in range(len(itens)):
        JS.append(f'tl.fromTo("#{i} .cn-bi{k}",{{scaleY:0}},{{scaleY:1,duration:1.1,ease:"power1.inOut"}},{r3(t0 + k * passo)});')
    return f'<div class="cn-barras" style="left:{x}px;width:{w}px;top:{y}px;height:{alt + 60}px">{cols}</div>'

def pontos(i, n, t0, t1, cols=40, tam=18, x=360, y=330, cor=None, cls="cn-pt"):
    """Grade de n bolinhas acendendo entre t0 e t1 (ex.: 200 clientes chegando)."""
    cor = cor or DESTAQUE
    pts = "".join(f'<i class="{cls}" style="width:{tam}px;height:{tam}px"></i>' for _ in range(n))
    JS.append(f'tl.fromTo("#{i} .{cls}",{{opacity:.08,scale:.4}},{{opacity:1,scale:1,background:"{cor}",duration:.18,stagger:{r3((t1 - t0) / max(1, n))}}},{r3(t0)});')
    return f'<div class="cn-grade" style="left:{x}px;top:{y}px;width:{cols * (tam + 8)}px">{pts}</div>'

def riscavel(texto, cls, icone=""):
    """Chip que pode ser riscado com risca() ("sem X" vira o X sendo riscado)."""
    return f'<div class="cn-chip {cls}">{icone}<span>{texto}</span><i class="cn-rk"></i></div>'

def risca(i, sel, t):
    JS.append(f'tl.fromTo("#{i} {sel} .cn-rk",{{scaleX:0}},{{scaleX:1,duration:.3,ease:"power2.out"}},{r3(t)});'
              f'tl.to("#{i} {sel}",{{opacity:.45,duration:.3}},{r3(t + .2)});')
    _som("swish", t, .35)

# ---------- demonstração: celular, conversa, notificação, terminal ----------
def cel(inner, x=730, y=150, w=460, h=880, topo="", cls=""):
    """Celular (posicione no plano da cena). inner = conteúdo da tela; topo = barra do app (topo_app)."""
    return (f'<div class="cn-cel {cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="cn-cels"><div class="cn-ilha"></div>{topo}<div class="cn-celc">{inner}</div></div></div>')

def topo_app(nome, sub="online", avatar="💬", cor="#16a34a"):
    """Barra de conversa. avatar = emoji, html de logo (tile(...)) ou <img src="midia/avatar.jpg">."""
    av = avatar if avatar.startswith("<") else f'<span class="cn-emo" style="font-size:34px">{avatar}</span>'
    return (f'<div class="cn-wtop"><div class="cn-wav" style="background:{cor}">{av}</div>'
            f'<div><div class="cn-wn">{nome}</div><div class="cn-ws">{sub}</div></div></div>')

def bolhas(i, msgs):
    """msgs = [(t, "eu"|"ele", html)] → bolhas chegando no tempo de cada uma. Retorna o html (ponha no cel())."""
    out = []
    for k, (t, quem, txt) in enumerate(msgs):
        out.append(f'<div class="cn-bb {quem} cn-bb{k}">{txt}<i>{"✓✓" if quem == "eu" else ""}</i></div>')
        JS.append(f'tl.fromTo("#{i} .cn-bb{k}",{{opacity:0,display:"none",scale:.7,y:20}},{{opacity:1,display:"block",scale:1,y:0,duration:.3,ease:"back.out(1.7)"}},{r3(t)});')
        _som("clique", t, .35)
    return "".join(out)

def notif(i, t, icone, titulo, texto, cls="cn-nt"):
    """Notificação descendo no topo do celular. Texto inventado e concreto ("Pagamento recebido · pedido #1042")."""
    JS.append(f'tl.fromTo("#{i} .{cls}",{{opacity:0,y:-60}},{{opacity:1,y:0,duration:.4,ease:"back.out(1.6)"}},{r3(t)});')
    _som("clique2", t, .4)
    return f'<div class="cn-notif {cls}"><div class="cn-nti">{icone}</div><div><b>{titulo}</b><span>{texto}</span></div><em>agora</em></div>'

def term(i, prompt, t0, t1, saidas=(), x=260, y=250, w=1400, h=700, titulo="Claude Code", logo_html=None):
    """Terminal: o prompt digita entre t0 e t1; saidas = [(t, texto)] entram com ✓ e som de check."""
    if logo_html is None:
        try: logo_html = tile("claude", 34)
        except Exception: logo_html = ""
    letras = "".join(f'<span class="cn-tl">{c_}</span>' for c_ in prompt)
    sai_ = "".join(f'<div class="cn-ts cn-ts{k}"><b>✓</b> {txt}</div>' for k, (_, txt) in enumerate(saidas))
    html = (f'<div class="cn-term" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="cn-jb"><i></i><i></i><i></i><span>{logo_html} {titulo}</span></div>'
            f'<div class="cn-tc"><div class="cn-tp"><b>&gt;</b> {letras}<u class="cn-cur"></u></div>{sai_}</div></div>')
    n = max(1, len(prompt))
    JS.append(f'tl.fromTo("#{i} .cn-tl",{{display:"none"}},{{display:"inline",duration:.01,stagger:{r3((t1 - t0) / n)}}},{r3(t0)});')
    JS.append(f'tl.fromTo("#{i} .cn-cur",{{opacity:1}},{{opacity:0,duration:.35,repeat:{int((t1 - t0) / .7) + 6},yoyo:true,immediateRender:false}},{r3(t0)});')
    _som("digitacao_1_5s" if t1 - t0 <= 1.5 else "digitacao_2_5s", t0, .6, dur=min(2.5, t1 - t0))
    for k, (t, _) in enumerate(saidas):
        JS.append(f'tl.fromTo("#{i} .cn-ts{k}",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:.25,ease:"power2.out"}},{r3(t)});')
        check_som(t)
    return html

# ---------- câmera viva (sem mexer o rosto) ----------
ROSTO = tuple(CFG.get("rosto") or (960, 420))

def bate(t, s=1.08, segura=0.9):
    """Zoom seco na palavra forte EM TORNO DO ROSTO (ponto fixo): o rosto só cresce, não sobe, não desce, não anda.
    Escala máxima 1,10. Defina "rosto": [x, y] no config.json. Não use em trecho de tela gravada."""
    s = min(s, 1.10)
    CAMZ.append((t - 0.1, t + segura + 0.6)); BATES.append(t)
    zx, zy = r3((ROSTO[0] - 960) * (1 - s)), r3((ROSTO[1] - 540) * (1 - s))
    JS.append(f'tl.fromTo("#palco",{{scale:1,x:0,y:0}},{{scale:{s},x:{zx},y:{zy},duration:.16,ease:"power3.out",immediateRender:false}},{r3(t - 0.05)});'
              f'tl.to("#palco",{{scale:1,x:0,y:0,duration:.5,ease:"power2.inOut"}},{r3(t + segura)});')
    _som("swish", t - 0.08, 0.35)

def num_lado(de, ate, t0, t1, a, b, pre="", suf="", sub="", emo="", x=110, y=330, casas=0):
    """Número contando num card ao lado do rosto (uma das 3 coisas permitidas ali: logo, número, inscrição)."""
    n = nid("nl")
    corpo = (f'<div class="cn-ld"><div class="cn-nl">{E(emo, 76) if emo else ""}<div><div class="cn-nlv" id="{n}">{pre}{a}{suf}</div>'
             f'{f"<div class=cn-nls>{sub}</div>" if sub else ""}</div></div></div>')
    i = clip(de, ate, corpo, estilo=f"left:{x}px;top:{y}px", track=7)
    JS.append(f'tl.fromTo("#{i} .cn-ld",{{opacity:0,x:-60,scale:.85,rotation:-3}},{{opacity:1,x:0,scale:1,rotation:0,duration:.5,ease:"back.out(1.6)"}},{r3(de)});'
              f'tl.to("#{i} .cn-ld",{{opacity:0,x:-40,duration:.25,ease:"power2.in"}},{r3(ate - 0.25)});')
    conta(f"#{n}", t0, t1, a, b, pre, suf, casas)
    _som("contador_1_5s", t0, .5, dur=min(1.4, t1 - t0 + .2))
    _som("clique2", de - .03, .4)
    return i

# ---------- lettering das frases-chave e lower third ----------
def letreiro(de, ate, linhas, x, y, w=680, sub=True):
    """Lettering só no gancho e na apresentação (4 a 6 no começo, 2,5 a 4 s cada), no lado LIVRE do rosto.
    linhas = [(tipo, fs, [(palavra, t, destaque?)])]; tipo "k" = linha pequena em caixa alta, "g" = grande, "m" = média.
    Só o núcleo da frase (tese, número, promessa), 2 a 5 palavras; nunca palavra vazia nem a frase inteira."""
    sombra = "0 0 30px rgba(255,255,255,.30),0 6px 30px rgba(0,0,0,.60),0 2px 5px rgba(0,0,0,.45)"
    corpo, ws, n = "", [], 0
    grandes = [j for j, (tp, _, _) in enumerate(linhas) if tp == "g"]
    for j, (tp, fs, pals) in enumerate(linhas):
        sp = "".join(f'<span class="cn-lw cn-lw{n + q}"{" style=color:#4da3ff" if az else ""}>{pw}</span>' for q, (pw, _, az) in enumerate(pals))
        ws += [(n + q, t, fs) for q, (_, t, _) in enumerate(pals)]; n += len(pals)
        corpo += f'<div class="cn-l{tp}" style="font-size:{fs}px">{sp}</div>'
        if grandes and j == grandes[-1] and sub: corpo += '<div class="cn-lu"></div>'
    cid = clip(de, ate, f'<div class="cn-lt" style="width:{w}px"><div class="cn-lv"></div>{corpo}</div>', estilo=f"left:{x}px;top:{y}px", track=7)
    s = f"#{cid}"
    JS.append(f'tl.fromTo("{s} .cn-lv",{{opacity:0}},{{opacity:1,duration:.35}},{r3(de)});'
              f'tl.fromTo("{s} .cn-lt",{{scale:1}},{{scale:1.035,duration:{r3(ate - de)},ease:"none"}},{r3(de)});')
    for k, t, fs in ws:
        JS.append(f'tl.fromTo("{s} .cn-lw{k}",{{opacity:0,y:{int(fs * .32)},scale:1.14,filter:"brightness(1.8)"}},'
                  f'{{opacity:1,y:0,scale:1,filter:"brightness(1)",duration:.42,ease:"power3.out"}},{r3(t - .04)});')
    if sub: JS.append(f'tl.fromTo("{s} .cn-lu",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"power3.out"}},{r3(max(t for _, t, _ in ws) + .15)});')
    sa = ate - .3 - .035 * (n - 1)
    JS.append(f'tl.to("{s} .cn-lw",{{opacity:0,y:-18,duration:.3,stagger:.035,ease:"power2.in"}},{r3(sa)});'
              + (f'tl.to("{s} .cn-lu",{{scaleX:0,transformOrigin:"100% 50%",duration:.28}},{r3(sa)});' if sub else "")
              + f'tl.to("{s} .cn-lv",{{opacity:0,duration:.3}},{r3(ate - .3)});')
    _som("swish", ws[0][1] - .06, .32)
    _som("clique2", ws[-1][1] - .03, .4)
    return cid

def lower_third(de, ate, t_nome, nome, credenciais=(), x=80, y=748):
    """Lower third quando a pessoa diz o nome (5 a 6 s): vidro escuro, nome subindo por máscara, linha que se
    desenha e credenciais com logo real. credenciais = [(t, logo_html, papel, onde)], ex.: (t, tile("youtube", 48), "Criador", "Canal X")."""
    cred = "".join(f'<div class="cn-nc cn-nc{k}"><span class="cn-nlg">{logo}</span><span>{papel} <span class="cn-dot">·</span> <b>{onde}</b></span></div>'
                   for k, (_, logo, papel, onde) in enumerate(credenciais))
    corpo = (f'<div class="cn-nm"><div class="cn-ng"></div><div class="cn-nmask"><div class="cn-nn">{nome}</div></div>'
             f'<div class="cn-nlin"></div>{cred}</div>')
    i = clip(de, ate, corpo, estilo=f"left:{x}px;top:{y}px", track=7)
    s = f"#{i}"
    JS.append(f'tl.fromTo("{s} .cn-nm",{{opacity:0,x:-40,clipPath:"inset(0% 100% 0% 0% round 26px)"}},{{opacity:1,x:0,clipPath:"inset(0% 0% 0% 0% round 26px)",duration:.6,ease:"power3.out"}},{r3(de)});'
              f'tl.fromTo("{s} .cn-nn",{{yPercent:110}},{{yPercent:0,duration:.6,ease:"power4.out"}},{r3(t_nome - .05)});'
              f'tl.fromTo("{s} .cn-nlin",{{scaleX:0}},{{scaleX:1,duration:.8,ease:"power3.inOut"}},{r3(t_nome + .2)});')
    for k, (t, _, _, _) in enumerate(credenciais):
        JS.append(f'tl.fromTo("{s} .cn-nc{k}",{{opacity:0,x:-26}},{{opacity:1,x:0,duration:.45,ease:"power3.out"}},{r3(t - .04)});'
                  f'tl.fromTo("{s} .cn-nc{k} .cn-nlg",{{scale:.4,rotation:-12}},{{scale:1,rotation:0,duration:.5,ease:"back.out(2.2)"}},{r3(t)});')
        _som("clique2", t - .03, .35)
    t_fim = credenciais[-1][0] if credenciais else t_nome
    JS.append(f'tl.fromTo("{s} .cn-ng",{{x:-200,rotation:16}},{{x:720,rotation:16,duration:1.1,ease:"power2.inOut"}},{r3(t_fim + .6)});'
              f'tl.to("{s} .cn-nc",{{opacity:0,x:-20,duration:.25,ease:"power2.in"}},{r3(ate - .55)});'
              f'tl.to("{s} .cn-nn",{{yPercent:-110,duration:.3,ease:"power3.in"}},{r3(ate - .45)});'
              f'tl.to("{s} .cn-nlin",{{scaleX:0,transformOrigin:"100% 50%",duration:.3}},{r3(ate - .45)});'
              f'tl.to("{s} .cn-nm",{{clipPath:"inset(0% 0% 0% 100% round 26px)",duration:.4,ease:"power3.in"}},{r3(ate - .42)});')
    _som("whoosh_curto", de - .1, .35)
    _som("swish", ate - .45, .3)
    return i

# ---------- b-roll (scripts/broll_pexels.py) ----------
def broll(de, ate, arquivo, card=False, x=260, y=150, w=1400, kb=1.10, media_start=0.0):
    """B-roll (vídeo .mp4 ou imagem) com push-in lento, entrada e saída animadas.
    card=False: tela cheia por cima da câmera (conta como cena no checa_ritmo).
    card=True: num card arredondado em (x, y, w) 16:9, com a câmera continuando atrás.
    Baixe grátis com:  python3 scripts/broll_pexels.py "city night" -o midia/broll"""
    if not (AQUI / arquivo).exists(): aviso(f"b-roll não encontrado: {arquivo}", de)
    if not card: CENAS_B.append((de, ate))
    h = round(w * 9 / 16)
    pos = (f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:30px;box-shadow:0 30px 80px rgba(0,0,0,.45)" if card
           else "left:0;top:0;width:1920px;height:1080px")
    v = nid("br")
    if arquivo.lower().endswith((".mp4", ".mov", ".webm")):
        HTML.append(f'<video id="{v}" class="clip cn-broll" src="{arquivo}" muted playsinline data-start="{r3(de)}" data-duration="{r3(ate - de)}" '
                    f'data-media-start="{r3(media_start + 0.001)}" data-track-index="13" style="{pos}"></video>')
    else:
        HTML.append(f'<div class="clip cn-broll" data-start="{r3(de)}" data-duration="{r3(ate - de)}" data-track-index="13" style="{pos}">'
                    f'<img id="{v}" src="{arquivo}" style="width:100%;height:100%;object-fit:cover"></div>')
    if card:
        JS.append(f'tl.fromTo("#{v}",{{opacity:0,y:40,scale:.92,filter:"blur(12px)"}},{{opacity:1,y:0,scale:1,filter:"blur(0px)",duration:.5,ease:"back.out(1.4)"}},{r3(de)});'
                  f'tl.to("#{v}",{{opacity:0,scale:1.04,filter:"blur(12px)",duration:.28,ease:"power2.in"}},{r3(ate - .28)});')
    else:
        JS.append(f'tl.fromTo("#{v}",{{opacity:0}},{{opacity:1,duration:.3}},{r3(de)});'
                  f'tl.fromTo("#{v}",{{scale:1}},{{scale:{kb},duration:{r3(ate - de)},ease:"none",immediateRender:false}},{r3(de)});'
                  f'tl.to("#{v}",{{opacity:0,duration:.25}},{r3(ate - .25)});')
    _som("swish", de - 0.06, 0.4)
    return v

# ---------- tela gravada ----------
def borrar(de, ate, x, y, w, h, raio=10, forca=16):
    """Borra um retângulo da TELA gravada (nome de pessoa, e-mail, dado sensível). Fica dentro do #palco: acompanha o zoom."""
    PALCO.append(f'<div class="clip" data-start="{r3(de)}" data-duration="{r3(ate - de)}" data-track-index="4" '
                 f'style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:{raio}px;'
                 f'backdrop-filter:blur({forca}px);-webkit-backdrop-filter:blur({forca}px);background:rgba(255,255,255,.08)"></div>')

# ---------- ritmo ----------
def checa_ritmo(respiro=8.0):
    """Cena branca entra no FIM do raciocínio; entre duas cenas, pelo menos `respiro` s de rosto."""
    blocos, ant, prob = [], None, 0
    for de, ate in sorted(CENAS_B):
        if blocos and de - blocos[-1][1] < 0.3: blocos[-1][1] = max(blocos[-1][1], ate)
        else: blocos.append([de, ate])
    for de, ate in blocos:
        if ant is not None and de - ant < respiro - 0.01:
            aviso(f"ritmo: só {de - ant:.1f} s de rosto antes da cena", de); prob += 1
        ant = ate
    tot = sum(b - a for a, b in CENAS_B)
    print(f"ritmo: {len(CENAS_B)} cena(s) · {tot:.0f} s cobrindo o rosto em {DUR:.0f} s ({tot / max(DUR, 1) * 100:.0f}%) · {prob} problema(s)")
