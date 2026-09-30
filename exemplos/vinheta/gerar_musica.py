#!/usr/bin/env python3
"""Música eletrônica impactante SINTETIZADA (sem direitos autorais) com as seções casadas com a vinheta.
141 bpm (1 tempo = 0,425 s): subida 0–2,2 s · DROP 1 em 2,2 s · impacto + acorde aberto em 5,6 s ·
DROP 2 em 7,725 s · batida final em 11,125 s · cauda até 12 s.  Saída: media/musica.wav (48 kHz estéreo)."""
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
from pathlib import Path

SR = 48000; DUR = 12.0; N = int(SR * DUR)
B = 0.425                                   # 1 tempo
D1, IMP, D2, FIM = 2.2, 5.6, 7.725, 11.125
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N)

def filt(x, tipo, f, ordem=4):
    return sosfilt(butter(ordem, f, btype=tipo, fs=SR, output="sos"), x)

def add(sig, t, g=1.0, pan=0.0):
    a = int(t * SR); b = min(N, a + len(sig))
    if b <= a: return
    L[a:b] += sig[:b - a] * g * (1 - max(0, pan)); R[a:b] += sig[:b - a] * g * (1 + min(0, pan))

def hz(n): return 440 * 2 ** ((n - 69) / 12)

def kick():
    t = np.arange(int(.38 * SR)) / SR
    f = 45 + 110 * np.exp(-t / .045)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .16)
    s[:240] += rng.standard_normal(240) * .5 * np.linspace(1, 0, 240)
    return np.tanh(s * 2.2) * .9

def clap():
    n = int(.22 * SR); s = np.zeros(n)
    for k, off in enumerate((0, .011, .022)):
        a = int(off * SR); m = n - a
        s[a:] += rng.standard_normal(m) * np.exp(-np.arange(m) / SR / (.012 if k < 2 else .09))
    return filt(s, "band", [900, 5000]) * .55

def hat(aberto=False):
    n = int((.16 if aberto else .045) * SR)
    return filt(rng.standard_normal(n), "high", 7500) * np.exp(-np.arange(n) / SR / (.05 if aberto else .012)) * .22

def supersaw(notas, dur, corte=4200, ataque=.005, rel=.08, vozes=7):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for nota in notas:
        for v in range(vozes):
            det = (v - (vozes - 1) / 2) * 11 / 1200
            ph = (t * hz(nota) * 2 ** det + rng.random()) % 1
            s += (2 * ph - 1)
    s /= (len(notas) * vozes) ** .5
    env = np.minimum(1, t / ataque) * np.clip((dur - t) / rel, 0, 1)
    return filt(s * env, "low", corte, 2) * .5

def sub(nota, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * hz(nota - 12) * t) + .35 * np.sign(np.sin(2 * np.pi * hz(nota) * t))
    return filt(s, "low", 180, 4) * np.minimum(1, t / .01) * np.clip((dur - t) / .03, 0, 1) * .75

ACORDES = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]   # Am F C G
RAIZ = [45, 41, 48, 43]
SC = np.ones(N)                               # sidechain (baixa acordes e baixo no kick)

def secao_drop(t0, t1):
    k = 0; t = t0
    while t < t1 - 1e-3:
        add(kick(), t, 1.0)
        a = int(t * SR); m = min(N - a, int(.3 * SR))
        SC[a:a + m] = np.minimum(SC[a:a + m], 1 - .75 * np.exp(-np.arange(m) / SR / .09))
        if k % 2 == 1: add(clap(), t, .9)
        add(hat(), t + B / 2, 1.0, pan=.2); add(hat(k % 4 == 3), t + B / 4 * 3, .7, pan=-.2)
        t += B; k += 1
    # acordes em semínima com gate + baixo em colcheia
    t = t0; k = 0
    while t < t1 - 1e-3:
        i = (k // 4) % 4
        add(supersaw(ACORDES[i], B * .8, 5200), t, .55, pan=.0)
        for q in (0, .5):
            add(sub(RAIZ[i], B * .45), t + q * B, .8)
        t += B; k += 1

# ---- subida 0–2,2 s: acordes filtrados abrindo + ruído subindo + caixa acelerando
pad = supersaw(ACORDES[0] + [81], D1, 9000, ataque=.6, rel=.05)
cortes = np.geomspace(350, 6000, len(pad))
blk = 1200
out = np.zeros_like(pad)
for a in range(0, len(pad), blk):
    out[a:a + blk] = filt(pad[max(0, a - 4000):a + blk], "low", float(cortes[a]), 2)[-len(pad[a:a + blk]):]
add(out, 0, .6)
n = int(D1 * SR); t = np.arange(n) / SR
riser = rng.standard_normal(n); riser = filt(riser, "band", [800, 9000]) * (t / D1) ** 2.2 * .35
add(riser, 0, 1.0)
tt = D1 - 1.7; step = B / 2
while tt < D1 - .02:
    add(clap(), tt, .35 + .5 * (1 - (D1 - tt) / 1.7)); tt += step
    if tt > D1 - .85: step = B / 4
    if tt > D1 - .42: step = B / 8
secao_drop(D1, IMP - B)
# ---- respiro de 1 tempo antes do impacto (tensão)
# ---- impacto em 5,6 s: boom + crash + acorde aberto sustentado
t = np.arange(int(1.8 * SR)) / SR
add(np.sin(2 * np.pi * np.cumsum(40 + 60 * np.exp(-t / .08)) / SR) * np.exp(-t / .55) * .9, IMP, 1.0)
cr = filt(rng.standard_normal(int(2.0 * SR)), "high", 3500) * np.exp(-np.arange(int(2.0 * SR)) / SR / .55) * .3
add(cr, IMP, 1.0, pan=.15); add(cr[::-1][::-1] * .9, IMP + .01, 1.0, pan=-.15)
add(supersaw([57, 64, 69, 72, 76], D2 - IMP, 6500, ataque=.02, rel=.3, vozes=9), IMP, .75)
n = int((D2 - IMP) * SR); t = np.arange(n) / SR
add(filt(rng.standard_normal(n), "band", [1500, 11000]) * (t / (D2 - IMP)) ** 3 * .3, IMP, 1.0)
tt = D2 - .85; step = B / 4
while tt < D2 - .02:
    add(clap(), tt, .3 + .5 * (1 - (D2 - tt) / .85)); tt += step
    if tt > D2 - .42: step = B / 8
secao_drop(D2, FIM)
# ---- batida final + cauda
add(kick(), FIM, 1.1); add(cr, FIM, 1.0)
add(supersaw([45, 57, 64, 69, 72], DUR - FIM, 5000, ataque=.005, rel=.8, vozes=9), FIM, .7)

# sidechain nos acordes/baixo: aproximação aplicando no mix inteiro (kick fica por cima)
kick_bus = np.zeros(N)
mix = np.stack([L, R], 1) * SC[:, None] ** .6
# reverb curto (combs) pra dar espaço
def rev(x):
    y = np.zeros_like(x)
    for d, g in ((.031, .7), (.037, .68), (.041, .66), (.047, .64)):
        k = int(d * SR); b_ = np.zeros(len(x))
        from scipy.signal import lfilter
        y += lfilter([1], np.r_[1, np.zeros(k - 1), -g], x)
    return x + y * .06
mix = np.stack([rev(mix[:, 0]), rev(mix[:, 1])], 1)
mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.6) * .89
fo = int(.25 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
import sys
_saida = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("musica.wav")
sf.write(_saida, mix.astype("float32"), SR, subtype="PCM_16")
print(_saida)
