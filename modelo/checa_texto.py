#!/usr/bin/env python3
"""Trava contra motion que TRANSCREVE a fala (o que mais faz uma edição parecer "feita por IA").

Uso:  python3 checa_texto.py [index.html]      (o build.py já roda no fim)
Lista os textos suspeitos e sai com código 1 se houver algum:
  - palavra vazia sozinha na tela: advérbio, conectivo, intensificador ou adjetivo solto ("principalmente", "incrível");
  - texto que repete 5 ou mais palavras seguidas da fala.
Fala citada de propósito (o prompt que a pessoa digita, a pergunta do público num balão) fica dentro de um
elemento com class="fala-ok" e é ignorada. Princípios: guia/MOTIONS.md.
"""
import json, re, sys, unicodedata, html as H
from pathlib import Path

AQUI = Path(__file__).parent
VAZIAS = set("""principalmente basicamente realmente simplesmente literalmente totalmente muito super mega
sensacional incrivel absurdo absurda impressionante fantastico fantastica maravilhoso maravilhosa
enorme gigante demais bem mais menos tipo entao assim inclusive tambem ainda justamente exatamente
olha cara gente beleza""".split())

def n(s):
    return re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())

def problemas(src, palavras):
    pal = [n(x["w"]).strip() for x in palavras]
    grams = {" ".join(pal[i:i + 5]) for i in range(len(pal) - 4)}
    src = re.sub(r"<script.*?</script>|<style.*?</style>", "", src, flags=re.S)
    src = re.sub(r'<(\w+)[^>]*class="[^"]*fala-ok[^"]*"[^>]*>.*?</\1>', "", src, flags=re.S)   # fala citada de propósito
    ruins = []
    for b in re.split(r"</(?:div|p|h\d|li)>", src):          # um bloco = um título/card (junta as palavras soltas)
        t = re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", b))).strip()
        if not t: continue
        w = n(t).split()
        # "principal-mente" quebrado em spans também conta (junta as partes)
        if (len(w) == 1 and w[0] in VAZIAS) or (1 < len(w) <= 3 and ("".join(w) in VAZIAS or all(x in VAZIAS for x in w))):
            ruins.append(("palavra vazia", t))
        elif len(w) >= 5 and any(" ".join(w[i:i + 5]) in grams for i in range(len(w) - 4)):
            ruins.append(("copia a fala", t))
    return ruins

if __name__ == "__main__":
    alvo = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / "index.html"
    ruins = problemas(alvo.read_text(), json.load(open(AQUI / "media/palavras_saida.json")))
    for k, t in ruins: print(f"  ✗ {k}: {t[:90]}")
    print(f"checa_texto: {len(ruins)} problema(s)" + (" · troque por um objeto que PROVE a ideia (guia/MOTIONS.md)" if ruins else ""))
    sys.exit(1 if ruins else 0)
