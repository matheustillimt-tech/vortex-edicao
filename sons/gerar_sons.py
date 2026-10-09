#!/usr/bin/env python3
"""Kit de sons da Vórtex Edição — 100% SINTETIZADO (nenhuma amostra de terceiros, livre de direitos autorais).

Filosofia: efeitos discretos e secos, sem nada "infantil" (bloop, sininho, glide) e SEM tom agudo sustentado
("piii"). Todo arquivo passa no teste de tom no fim (≤ 50% da energia acima de 300 Hz num único pico).

Uso:  python3 sons/gerar_sons.py [pasta_saida] [--sem-trilha]        (padrão: sons/kit)
Gera: whoosh, whoosh_curto, clique, clique2, swish, impacto_grave, contador_{1_5,2_5,3_5}s,
      digitacao_{1_5,2_5}s, check e trilha.wav (pad grave + pulso, 100 bpm, 270 s, sem melodia).
"""
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, lfilter

SR = 48000
rng = np.random.default_rng(7)
_ARGS = [x for x in sys.argv[1:] if not x.startswith("--")]
OUT = Path(_ARGS[0]) if _ARGS else Path(__file__).parent / "kit"
OUT.mkdir(parents=True, exist_ok=True)

def filt(x, tipo, f, ordem=4):
    return sosfilt(butter(ordem, f, btype=tipo, fs=SR, output="sos"), x)

def pico(y, db):
    return y * (10 ** (db / 20) / (np.abs(y).max() + 1e-12))

def fade(y, ms=10):
    k = int(ms / 1000 * SR); y[-k:] *= np.linspace(1, 0, k); return y

def banda_deslizante(n, c0, c1, bw):
    out = np.zeros(n); blk = 1024
    for i in range(0, n, blk // 2):
        seg = min(blk, n - i); c = c0 + (c1 - c0) * (i / n)
        out[i:i + seg] += filt(rng.standard_normal(seg + 512), "band", [max(30, c - bw / 2), c + bw / 2], 2)[512:] * np.hanning(seg)
    return out

def whoosh(dur=1.0, pico_t=0.45, c0=300, c1=2400, db=-6):
    n = int(dur * SR); x = np.arange(n) / SR
    y = banda_deslizante(n, c0, c1, 900)
    e = np.where(x < pico_t, (x / pico_t) ** 2.2, np.exp(-(x - pico_t) / (dur * 0.22)))
    return fade(pico(y * e, db))

def clique(corpo_hz=(400, 1400), brilho=(2500, 8000), db=-8, dur=0.2):
    n = int(dur * SR); x = np.arange(n) / SR
    y = filt(rng.standard_normal(n), "band", list(brilho)) * np.exp(-x / 0.006)
    y += filt(rng.standard_normal(n), "band", list(corpo_hz)) * np.exp(-x / 0.02) * 0.6
    return fade(pico(y, db))

def swish():
    n = int(0.46 * SR); x = np.arange(n) / SR
    y = banda_deslizante(n, 450, 900, 700)
    e = np.where(x < 0.17, (x / 0.17) ** 2, np.exp(-(x - 0.17) / 0.09))
    return fade(pico(y * e, -10))

def impacto(dur=1.4):
    n = int(dur * SR); x = np.arange(n) / SR
    f = 62 * np.exp(-x / 0.35) + 38
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x / 0.32)
    y += filt(rng.standard_normal(n), "band", [60, 900]) * np.exp(-x / 0.06) * 0.35
    y[:int(.004 * SR)] *= np.linspace(0, 1, int(.004 * SR))
    return pico(y, -6)

def contador(dur):
    """Número rolando: cliques de ruído 1,8–6,5 kHz, sem tom, ~14/s, desacelerando no fim."""
    n = int(dur * SR); y = np.zeros(n); t = 0.0
    while t < dur - 0.03:
        m = int(0.006 * SR); a = int(t * SR)
        y[a:a + m] += (rng.standard_normal(m) * np.exp(-np.linspace(0, 9, m)))[: n - a] * (0.75 + 0.25 * rng.random())
        t += 1 / 14 * (1 + 1.6 * (t / dur) ** 3)
    return fade(pico(filt(y, "band", [1800, 6500]), -15))

def digitacao(dur):
    n = int(dur * SR); y = np.zeros(n); t = 0.0
    while t < dur - 0.02:
        m = int(0.018 * SR); a = int(t * SR); x = np.arange(m) / SR
        k = filt(rng.standard_normal(m), "band", [3000, 9000]) * np.exp(-x / 0.004) * rng.uniform(.55, 1)
        k += filt(rng.standard_normal(m), "band", [300, 1200]) * np.exp(-x / 0.006) * 0.25
        y[a:a + m] += k[: n - a]; t += rng.uniform(.6, 1.4) / 13
    return fade(pico(y, -15))

def trilha(dur=270.0):
    """Pad em Ré menor (Dm–B♭–F–C) + pulso grave a 100 bpm. Sem melodia: fica por baixo da voz."""
    beat = 0.6; bloco = 8 * beat; N = int(dur * SR)
    acordes = [[50, 53, 57, 62], [46, 50, 53, 58], [53, 57, 60, 65], [48, 52, 55, 60]]; raiz = [38, 34, 41, 36]
    hz = lambda n: 440 * 2 ** ((n - 69) / 12)
    Lp, Rp, pul = np.zeros(N), np.zeros(N), np.zeros(N); t0, k = 0.0, 0
    while t0 < dur:
        a = int(t0 * SR); b = min(N, int((t0 + bloco + 1.5) * SR)); n = b - a; x = np.arange(n)
        env = np.minimum(1, x / (1.2 * SR)) * np.clip((n - x) / (1.5 * SR), 0, 1)
        for nota in acordes[k % 4]:
            for det, lado in ((-7, "l"), (7, "r"), (0, "c")):
                s = (2 * ((x * hz(nota) * 2 ** (det / 1200) / SR + rng.random()) % 1) - 1) * env * .22
                if lado in "lc": Lp[a:b] += s
                if lado in "rc": Rp[a:b] += s
        for j in range(8):
            c = int((t0 + j * beat) * SR); m = min(int(.32 * SR), N - c)
            if m <= 0: break
            tt = np.arange(m) / SR
            pul[c:c + m] += np.sin(2 * np.pi * hz(raiz[k % 4]) * tt) * np.exp(-tt / .11) * (1 if j % 2 == 0 else .7)
        t0 += bloco; k += 1
    def lp2(v, fc):
        a = np.exp(-2 * np.pi * fc / SR); v = lfilter([1 - a], [1, -a], v); return lfilter([1 - a], [1, -a], v)
    Lp, Rp, pul = lp2(Lp, 850), lp2(Rp, 850), lp2(pul, 220)
    st = np.stack([Lp + pul * .9, Rp + pul * .9], 1)
    f = np.ones(N); f[:int(1.5 * SR)] = np.linspace(0, 1, int(1.5 * SR)); f[-int(4 * SR):] = np.linspace(1, 0, int(4 * SR))
    st *= f[:, None]; st = st / np.sqrt((st ** 2).mean()) * 10 ** (-20 / 20)
    return np.clip(st, -.98, .98)

def check():
    """Som de "deu certo": dois ticks secos subindo + corpo grave curto. Sem sininho, sem bipe longo."""
    def tick(dur, f, amp):
        n = int(SR * dur); return filt(rng.standard_normal(n), "band", [f / 1.45, f * 1.45], 2) * np.exp(-np.linspace(0, 7, n)) * amp
    y = np.zeros(int(SR * 0.32)); o = int(SR * 0.075)
    t1 = tick(0.035, 1300, 1.0); y[:len(t1)] += t1
    t2 = tick(0.05, 2100, 1.1); y[o:o + len(t2)] += t2
    nc = int(SR * 0.12); y[o:o + nc] += filt(rng.standard_normal(nc), "low", 220, 2) * np.exp(-np.linspace(0, 6, nc)) * 1.6
    return fade(pico(y, -6))

def tom(y):
    S = np.abs(np.fft.rfft(y * np.hanning(len(y)))); f = np.fft.rfftfreq(len(y), 1 / SR)
    m = f > 300; S, f = S[m], f[m]; i = S.argmax()
    return 100 * (S[abs(f - f[i]) < 30] ** 2).sum() / (S ** 2).sum()

KIT = {
    "whoosh": whoosh(), "whoosh_curto": whoosh(0.5, 0.2, 350, 2000),
    "clique": clique(), "clique2": clique((200, 600), (1500, 5000), -8),
    "swish": swish(), "impacto_grave": impacto(),
    "contador_1_5s": contador(1.5), "contador_2_5s": contador(2.5), "contador_3_5s": contador(3.5),
    "digitacao_1_5s": digitacao(1.5), "digitacao_2_5s": digitacao(2.5),
    "check": check(),
}
for nome, y in KIT.items():
    pc = tom(y)
    assert pc <= 50, f"{nome}: {pc:.0f}% num tom só (soa como bipe) — refazer"
    sf.write(OUT / f"{nome}.wav", y.astype("float32"), SR, subtype="PCM_16")
    print(f"ok  {nome:16s} tom {pc:4.1f}%")
if "--sem-trilha" not in sys.argv:
    sf.write(OUT / "trilha.wav", trilha().astype("float32"), SR, subtype="PCM_16")
    print("ok  trilha.wav")
