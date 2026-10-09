# CAMADA "WEBCAM FIXA" · roda dentro do build.py, depois da LINHA DO TEMPO (o build.py já chama quando há webcam).
#
# Problema: na gravação única (tela com a webcam "colada" num canto), a webcam está DENTRO da imagem da tela.
# Todo zoom de câmera (bate(), zoom(pip=False)) que cai num trecho de TELA amplia a webcam junto, e o rosto sai
# do quadro. O zoom(pip=True) e o zoom_seq() já tratam isso; esta camada cobre o resto.
#
# Em cada zoom de câmera dentro de um trecho de tela:
#   1) uma tampa da cor de fundo cobre a webcam original dentro do #palco (ela cresce com o zoom e some);
#   2) a webcam volta por cima, SEM zoom, no lugar original (o próprio base.mp4 recortado no retângulo).
#
# config.json:
#   "webcam": {"x":..,"y":..,"w":..,"h":..}   retângulo da webcam em px de 1920×1080
#   "trechos_tela": [[ini, fim], ...]          trechos (s, no vídeo cortado) em que a tela aparece; null = o vídeo todo
#   "fundo_gravacao": "#0a0a0a"                cor da tampa (o que fica atrás da webcam na tela)

def _junta(iv, folga=0.25):
    out = []
    for a, b in sorted(iv):
        if out and a - out[-1][1] < folga: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out

_tela = CFG.get("trechos_tela") or [[0.0, DUR]]
_iv = []
for _a, _b in CAMZ:
    for _ta, _tb in _tela:
        _a2, _b2 = max(_a, _ta), min(_b, _tb)
        if _b2 - _a2 > 0.05: _iv.append((_a2, _b2))
_bt = [t for t in BATES if any(_ta < t < _tb for _ta, _tb in _tela)]
if _bt: MISS.append(f"bate() em trecho de TELA (zoom no rosto não faz sentido aqui): {[round(t, 1) for t in _bt]}")

_x0, _y0 = WEBCAM["x"], WEBCAM["y"]
_x1, _y1 = _x0 + WEBCAM["w"], _y0 + WEBCAM["h"]
_fixas = _junta(_iv)
for _a, _b in _fixas:
    PALCO.append(f'<div class="clip" data-start="{r3(_a)}" data-duration="{r3(_b - _a)}" data-track-index="4" '
                 f'style="position:absolute;left:{_x0 - 4}px;top:{_y0 - 4}px;width:{_x1 - _x0 + 8}px;height:{_y1 - _y0 + 8}px;'
                 f'background:{FUNDO_GRAVACAO};z-index:2"></div>')
    _i = nid("wf")
    HTML.append(f'<video id="{_i}" class="clip" src="media/base.mp4" muted playsinline data-start="{r3(_a)}" data-duration="{r3(_b - _a)}" '
                f'data-media-start="{r3(_a)}" data-track-index="8" style="position:absolute;left:0;top:0;width:1920px;height:1080px;'
                f'object-fit:cover;z-index:8;clip-path:inset({_y0}px {1920 - _x1}px {max(0, 1080 - _y1)}px {_x0}px round 22px)"></video>')
if _fixas: print(f"webcam_fixa: webcam parada em {len(_fixas)} zoom(s) de câmera dentro da tela")
