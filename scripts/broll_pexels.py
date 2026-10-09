#!/usr/bin/env python3
"""Busca e baixa b-roll GRÁTIS do Pexels (API oficial) pra usar com o broll() do kit de cenas.

Chave grátis em https://www.pexels.com/api/  →  coloque no .env da skill:  PEXELS_API_KEY=...

Uso:
  python3 scripts/broll_pexels.py "city night" -o ~/vortex-edicao-projetos/meu-video/midia/broll
  python3 scripts/broll_pexels.py "dinheiro" --orientacao portrait --min 5 --max 15 -n 3 -o midia/broll
  python3 scripts/broll_pexels.py "office" --dry-run          # só mostra a busca, não baixa nada

- Aceita termo em português, mas o acervo responde MUITO melhor em inglês ("money", "city skyline", "office team").
- Escolhe, de cada vídeo, o arquivo HD mais próximo de 1920×1080 (ou 1080×1920 em vertical).
- Grava creditos.json na pasta de saída com autor e link. O Pexels recomenda (não exige) dar o crédito;
  ponha na descrição do vídeo se quiser.
"""
import argparse, json, os, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
API = "https://api.pexels.com/videos/search"

def chave():
    k = os.environ.get("PEXELS_API_KEY")
    env = RAIZ / ".env"
    if not k and env.exists():
        for l in env.read_text().splitlines():
            if l.startswith("PEXELS_API_KEY="):
                k = l.split("=", 1)[1].strip().strip('"')
    return k or None

def url_busca(termo, orientacao, por_pagina):
    q = {"query": termo, "orientation": orientacao, "size": "medium", "per_page": por_pagina}
    return API + "?" + urllib.parse.urlencode(q)

def melhor_arquivo(video, orientacao):
    """Arquivo mp4 com resolução mais próxima do alvo (1920×1080 ou 1080×1920), preferindo não passar dele."""
    alvo = (1920, 1080) if orientacao == "landscape" else (1080, 1920)
    arqs = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("width") and f.get("height")]
    if not arqs: return None
    def custo(f):
        dw, dh = f["width"] - alvo[0], f["height"] - alvo[1]
        acima = max(dw, 0) + max(dh, 0)                 # 4K pesa no disco e não melhora o 1080p
        return (abs(dw) + abs(dh)) + acima * 0.5
    return min(arqs, key=custo)

def baixa(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": "vortex-edicao"})
    with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)

def main():
    ap = argparse.ArgumentParser(description="b-roll grátis do Pexels")
    ap.add_argument("termo", help='o que buscar (em inglês dá mais resultado: "money", "city night")')
    ap.add_argument("-o", "--saida", default="midia/broll", help="pasta de saída (padrão: midia/broll)")
    ap.add_argument("--orientacao", choices=["landscape", "portrait"], default="landscape")
    ap.add_argument("--min", type=float, default=4, help="duração mínima (s)")
    ap.add_argument("--max", type=float, default=20, help="duração máxima (s)")
    ap.add_argument("-n", "--quantidade", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true", help="mostra a busca e o que baixaria, sem baixar")
    a = ap.parse_args()

    url = url_busca(a.termo, a.orientacao, min(80, max(15, a.quantidade * 5)))
    k = chave()
    if a.dry_run and not k:
        print(f"[dry-run] GET {url}\n[dry-run] header Authorization: <PEXELS_API_KEY>  (sem chave: crie grátis em pexels.com/api e ponha no .env)")
        return 0
    if not k:
        print("Falta a PEXELS_API_KEY. Crie grátis em https://www.pexels.com/api/ e coloque no .env da skill:\n  PEXELS_API_KEY=...", file=sys.stderr)
        return 2
    try:
        req = urllib.request.Request(url, headers={"Authorization": k, "User-Agent": "vortex-edicao"})
        dados = json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        print(f"Pexels respondeu {e.code}: {'chave inválida' if e.code in (401, 403) else e.reason}", file=sys.stderr); return 1
    except urllib.error.URLError as e:
        print(f"Sem conexão com o Pexels: {e.reason}", file=sys.stderr); return 1

    escolhidos = []
    for v in dados.get("videos", []):
        if not (a.min <= v.get("duration", 0) <= a.max): continue
        f = melhor_arquivo(v, a.orientacao)
        if f: escolhidos.append((v, f))
        if len(escolhidos) >= a.quantidade: break
    if not escolhidos:
        print(f"Nada entre {a.min:g} e {a.max:g} s para {a.termo!r}. Tente um termo em inglês ou outra faixa de duração.")
        return 1

    pasta = Path(a.saida).expanduser(); pasta.mkdir(parents=True, exist_ok=True)
    cred_arq = pasta / "creditos.json"
    creditos = json.loads(cred_arq.read_text()) if cred_arq.exists() else []
    for v, f in escolhidos:
        nome = f"pexels_{v['id']}_{f['width']}x{f['height']}.mp4"
        info = f"{nome} · {v['duration']} s · {v['user']['name']}"
        if a.dry_run:
            print(f"[dry-run] baixaria {info}"); continue
        destino = pasta / nome
        if not destino.exists():
            baixa(f["link"], destino)
        print(f"ok  {info}")
        if not any(c.get("arquivo") == nome for c in creditos):
            creditos.append({"arquivo": nome, "autor": v["user"]["name"], "perfil": v["user"]["url"], "link": v["url"],
                             "fonte": "Pexels", "termo": a.termo})
    if not a.dry_run:
        cred_arq.write_text(json.dumps(creditos, ensure_ascii=False, indent=2))
        print(f"créditos em {cred_arq}\nno build (caminho relativo ao projeto): cn.broll(de, ate, \"midia/{pasta.name}/{nome}\")")
    return 0

if __name__ == "__main__":
    sys.exit(main())
