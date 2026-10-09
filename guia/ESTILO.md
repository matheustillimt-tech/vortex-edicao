# Estilo Vórtex Edição — regras

A edição tem que prender (dopaminérgica) sem parecer brinquedo (clean). O critério de todo efeito é uma pergunta: **"isso passa autoridade ou parece brinquedo?"**

> **Leia antes o [`MOTIONS.md`](MOTIONS.md).** Os princípios de lá vencem as tabelas daqui: o motion não transcreve a fala, adjetivo vira prova e ao lado do rosto só entram logo, número e inscrição. A cena branca do kit (`cenas.py`) tem a paleta própria descrita lá (branco radial, preto e um azul de destaque).

## Visual

- **Paleta:**
  - fundo `#0a0a0a`, cards de vidro escuro, texto `#e6e6e6`;
  - **destaque = branco puro com brilho** (`text-shadow` de glow), nunca cor saturada;
  - cor só na **logo real** e na **mídia real** (print, gravação). Vermelho só em "AO VIVO".
- **Fonte:** Inter em tudo (título 52 px, número 124 px, texto 28–38 px em 1080p, pensando no celular).
- **Destaque de palavra:** sublinhado reto que se desenha. Nada de rabisco, elipse à mão ou emoji.
- **Número ou botão que aparece NA TELA:** zoom + `circulo()`, um traço limpo e geométrico, no lugar de card por cima.
- **Todo elemento tem saída animada** (`sai()`: fade + blur + leve escala). Nunca corte seco.

## Densidade

| Formato | Quanto motion |
|---|---|
| **YouTube: abertura (0–45 s)** | densa: um motion ilustrado a cada 2–4 s, zoom seco no rosto, 4 a 6 letterings com o núcleo das frases-chave (nunca a frase inteira) |
| **YouTube: corpo** | um a cada 20–40 s, sempre ilustrado; zoom in/out onde a pessoa aponta ou explica |
| **Reels / TikTok** | o mais denso: imagem ou ícone animado em quase tudo |
| **Aula / tutorial longo** | leve: abertura, zoom em texto pequeno, número em destaque, card do entregável |

## O que na fala vira qual motion

| A pessoa fala… | Motion |
|---|---|
| nome de ferramenta, modelo, empresa, rede | `il.chip` com a **logo real** (`tile()` / `scripts/baixar_logos.sh`), um de cada lado da câmera |
| um conceito | `il.chip` com **ícone que se desenha** |
| "olha isso", um resultado, "dá pra fazer X" | `il.card_midia` com **print ou gravação real** (`captura/capturar.mjs`) |
| o que se pede pra IA | `il.prompt` digitando junto com a fala |
| passo a passo ("vai em Configurações e ativa…") | `il.demo`: print + cursor andando, clicando e dando zoom |
| número | `conta()` + `contador_som()` (card) ou, se está na tela, `zoom` + `circulo` |
| "meu canal", volume de trabalho | `il.parede` com thumbnails ou prints reais |
| ideia, objeto | `il.objeto` com imagem gerada por IA (fundo escuro), flutuando com reflexo |
| abertura cinematográfica | `cena()` + `il.hud` + texto cinético |

## Cortes

- **Repetiu ou errou: fica a ÚLTIMA tentativa.** Corte também falsos começos e o que ficou prolixo.
- Respiros acima de ~0,3 s saem (`cortar.py`).
- **A tela aparece inteira**, sem cortar palavras na borda. Zoom só em trecho, com a borda travada (o `zoom()` já trava).
- Na tela + webcam: durante o zoom, a webcam original é tampada e a câmera volta por cima **sem zoom**, em janelinha com moldura. Card nunca invade a área da webcam.

## Som

- Kit sintetizado em `sons/` (`gerar_sons.py`): `whoosh`, `whoosh_curto`, `clique`, `clique2`, `swish`, `impacto_grave`, `contador_*`, `digitacao_*`.
- **Nada infantil** (bloop, sininho, glide) e **nada de tom agudo sustentado** ("piii"). Todo som novo passa no teste de tom do `gerar_sons.py`.
- Proporção em relação à voz: whoosh ≈ +3 a +4 dB, clique ≈ −2 dB.
- Trilha de fundo (`trilha.wav`) ~15 dB abaixo da voz.
- Master final em −14 LUFS / −1 dBTP.

## Armadilhas do HyperFrames (já resolvidas no modelo)

- O vídeo precisa de **fps constante** (o `cortar.py` faz). Todo `<audio>` tem `id` + `data-duration` + trilha própria.
- Não anime `left`/`top`/`letter-spacing`; use `x`/`y`/`scale`. Vários `fromTo` no mesmo alvo precisam de `immediateRender:false`.
- Vídeo dentro de card: vira um clip próprio alinhado ao card (`il.card_midia` faz), nunca dentro de um elemento com tempo.
- No render em trechos, o início da mídia leva **+1 ms** (senão pega o quadro anterior). O `render_rapido.py` já faz.
