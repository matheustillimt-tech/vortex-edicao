# Vórtex Edição de Vídeo

**Edição de vídeo para YouTube 100% com IA, dentro do Claude Code.** Você grava e a IA faz o resto:
- transcreve e corta os erros e os respiros;
- escreve os motions **no ritmo da sua fala**: logos reais, prints e gravações de tela, prompt digitando, cursor clicando, zoom, contador, trilha e efeitos sonoros;
- renderiza em MP4 pronto pro YouTube.

Estética **clean e dopaminérgica**: preto com branco brilhante, vidro, tudo entra e sai animado. Nada de efeito infantil.

> Feito pelo **Grupo Vórtex**. O motor de render é o [HyperFrames](https://github.com/heygen-com/hyperframes), open source (Apache 2.0), que transforma HTML em vídeo.

## O que ela faz

| Etapa | Como |
|---|---|
| Transcrição palavra a palavra | ElevenLabs Scribe (ou Whisper local, grátis) |
| Corte de erros e respiros | lê a fala, fica sempre com a **última tentativa** quando você repete, tira pausas > 0,3 s |
| Motions ancorados na fala | cada efeito entra na palavra exata (`W("frase")`), com saída animada |
| Motions **ilustrados** | pílula com logo real, ícone que se desenha, card com print ou gravação de tela, prompt digitando, demonstração com cursor, parede de thumbnails, objeto 3D, moldura HUD |
| Prints e gravações de tela | abre páginas sozinha num Chrome isolado, tira print ou grava seguindo um roteiro de cliques |
| Zoom inteligente | zoom na tela com a sua câmera em janelinha, sem zoom e sem aparecer duplicada; círculo limpo em número da tela |
| Som | kit de efeitos e trilha **sintetizados** (sem direitos autorais), master em −14 LUFS |
| Render rápido | só os trechos com motion passam pelo navegador, em paralelo e com cache. Um ajuste refaz só o trecho alterado |
| **Princípios de motion** | o motion não transcreve a fala: adjetivo vira prova, cena é objeto em passos com check, ao lado do rosto só logo, número e inscrição ([`guia/MOTIONS.md`](guia/MOTIONS.md)) |
| **Trava de texto** | `checa_texto.py` roda no fim do build e recusa palavra vazia e frase copiada da transcrição |
| **Kit de cenas** | cena branca com câmera virtual correndo, gráfico que enche como água, celular com conversa e notificação, terminal digitando, barras, pontos, chip riscado, lettering do gancho, lower third, zoom seco centrado no rosto, checagem de ritmo |
| **B-roll grátis** | busca e baixa b-roll do Pexels sozinha (`scripts/broll_pexels.py`) e põe em tela cheia ou num card (`broll()`) |
| **Webcam fixa** | na gravação com a webcam dentro da tela, o zoom não amplia a webcam: ela fica parada e inteira por cima |
| **Seu design system** | os motions já vêm treinados com regras de ritmo e estética; cor de destaque e fonte no `config.json` (`marca`), o resto no CSS |

## Novidades (outubro/2026)

- **[Princípios de motion](guia/MOTIONS.md):** o texto na tela nunca repete a fala. Palavra vazia não vai pra tela, adjetivo vira prova (contador, gráfico, chip riscado), cada cena é um objeto em 3 a 5 passos com a câmera correndo e check no fim, ao lado do rosto só logo, número e inscrição, letterings só nas frases-chave do início, lower third no nome, painéis quando a explicação é um mecanismo prático, e a tela que a pessoa mostra fica sem motion.
- **`checa_texto.py`:** trava que roda no fim do `build.py`. Fala citada de propósito (prompt, pergunta do público) vai com `class="fala-ok"`.
- **Kit de cenas (`modelo/cenas.py` + `cenas.css`), opcional:** `cn = carrega_cenas()` no `build.py` e use `cn.cena`, `cn.agua`, `cn.term`, `cn.cel`/`cn.bolhas`/`cn.notif`, `cn.barras`, `cn.pontos`, `cn.risca`, `cn.letreiro`, `cn.lower_third`, `cn.broll`, `cn.bate` e `cn.checa_ritmo`. Sem mídia própria: ícone é emoji (ou o seu PNG em `midia/icones/`), logos e avatar entram por parâmetro.
- **Zoom no rosto sem mexer o rosto:** `cn.bate()` dá o zoom em volta do centro do rosto (`"rosto": [x, y]` no `config.json`), com escala de no máximo 1,10.
- **Webcam fixa (`modelo/webcam_fixa.py`):** zoom de câmera dentro da tela não leva mais a webcam junto. Lê o retângulo da webcam e os trechos de tela do `config.json`.
- **B-roll grátis pelo Pexels (`scripts/broll_pexels.py`).**
- **[Guia de gravação](guia/GRAVACAO.md):** câmera e tela em arquivos separados com o plugin Source Record do OBS.
- **Render rápido:** clip que começa antes do trecho é cortado no início (antes ficava visível fora de hora); trechos de no máximo 90 s (não enche o disco); quadro extra do fim aparado.
- **Som de "deu certo"** (`check.wav`) no kit sintetizado.

## B-roll

- **Recomendado: Pexels, grátis.** Crie a chave em [pexels.com/api](https://www.pexels.com/api/) e cole no `.env` (`PEXELS_API_KEY=...`). O Claude busca e baixa sozinho quando a fala pede uma imagem ("cidade", "dinheiro", "escritório"), com o termo em inglês, que dá mais resultado:
  ```bash
  ~/.claude/skills/vortex-edicao/.venv/bin/python ~/.claude/skills/vortex-edicao/scripts/broll_pexels.py "city night" -o midia/broll -n 2
  ```
  Ele escolhe o arquivo HD mais próximo de 1920×1080 (ou 1080×1920 com `--orientacao portrait`) e grava `creditos.json` com autor e link. O Pexels recomenda o crédito, mas não exige.
- **Avançado: b-roll gerado por IA** (Higgsfield ou similares). É pago e mais trabalhoso; vale quando não existe imagem de banco pro que a fala pede. Dá pra plugar pela API do provedor escolhido: gere o clipe, salve em `midia/` e use o mesmo `cn.broll()`.

## Seu design system

Os motions já vêm treinados com regras de ritmo e estética (densidade, saída animada, sons discretos, cena no fim do raciocínio). A identidade é sua:
- `config.json` → `"marca": {"destaque": "#1d7cf2", "fonte": "Inter"}`: a cor de destaque das cenas e a fonte;
- `estilo.css` (vidro escuro, câmera, zoom) e `cenas.css` (cena branca, objetos): cores, raios, sombras e tamanhos;
- a sua logo entra como imagem ou SVG nos componentes que recebem `logo_html` (lower third, terminal, conversa).

## Instalação

Precisa de **Node 22+**, **ffmpeg** e **Python 3**.

```bash
git clone https://github.com/matheustillimt-tech/vortex-edicao ~/.claude/skills/vortex-edicao
bash ~/.claude/skills/vortex-edicao/instalar.sh
```

Opcional (transcrição melhor): coloque sua chave da ElevenLabs no arquivo `.env` da pasta (`ELEVENLABS_API_KEY=...`). Sem chave, ela usa o Whisper local (`pip install openai-whisper`).
Opcional (b-roll grátis): `PEXELS_API_KEY=...` no mesmo `.env`.

## Como usar

Abra o **Claude Code** e peça em português:

- *"Edita esse vídeo: ~/Movies/gravacao.mp4"*
- *"Faz uma vinheta pro meu canal @seucanal"*
- *"Em 1:20 troca o card por um print do site da OpenAI"*

A skill `vortex-edicao` ativa sozinha, ou digite `/vortex-edicao`.

Pra rodar na mão, sem o Claude, o fluxo é este:

```bash
S=~/.claude/skills/vortex-edicao
bash $S/novo_projeto.sh meu-video ~/Movies/gravacao.mp4          # transcreve
# leia ~/vortex-edicao-projetos/meu-video/fonte/roteiro.txt e anote os erros
$S/.venv/bin/python $S/cortar.py ~/vortex-edicao-projetos/meu-video --remover 12.3-15.8
cd ~/vortex-edicao-projetos/meu-video
# escreva a LINHA DO TEMPO no build.py (tem um exemplo pronto)
$S/.venv/bin/python build.py
$S/.venv/bin/python render_rapido.py -o renders/v1.mp4
```

### Exemplo: vinheta do seu canal em 30 segundos

```bash
~/.claude/skills/vortex-edicao/.venv/bin/python ~/.claude/skills/vortex-edicao/exemplos/vinheta/criar_vinheta.py --canal @seucanal --nome "Seu Nome" \
  --bio "O que o seu canal ensina" --linha1 "IA APLICADA" --linha2 "A NEGÓCIOS"
```

Ela puxa as thumbnails reais do canal, gera uma música eletrônica com drops casados com a imagem e entrega 12 s de vinheta.

## Estrutura

```
SKILL.md              instruções pro Claude Code
guia/ESTILO.md        as regras de estilo (o que vira qual motion, densidade, som, armadilhas)
guia/MOTIONS.md       os princípios de motion (o que NÃO vira motion; vale mais que a tabela do ESTILO)
guia/GRAVACAO.md      como gravar: câmera e tela separadas (OBS + Source Record), enquadramento, fala
instalar.sh           instala tudo (uma vez)
novo_projeto.sh       cria o projeto de um vídeo
transcrever.py        1) prepara a gravação e transcreve
cortar.py             2) corta erros e respiros
modelo/build.py       3) a edição: ferramentas + LINHA DO TEMPO
modelo/ilustra.py     motions ilustrados
modelo/cenas.py       kit opcional de cenas e demonstrações (+ cenas.css)
modelo/checa_texto.py trava contra motion que transcreve a fala
modelo/webcam_fixa.py zoom de câmera dentro da tela sem ampliar a webcam
scripts/broll_pexels.py  b-roll grátis do Pexels
modelo/render_rapido.py  4) render rápido com cache + master
captura/capturar.mjs  print e gravação de tela de páginas públicas
sons/gerar_sons.py    kit de efeitos e trilha, sintetizados
exemplos/vinheta/     vinheta do canal + música eletrônica sintetizada
```

## Créditos e licenças

- Código deste repositório: MIT © Grupo Vórtex.
- [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache 2.0), [GSAP](https://gsap.com), fonte [Inter](https://rsms.me/inter/) (OFL) e ícones [Simple Icons](https://simpleicons.org) (CC0), todos baixados na instalação.
- As logos de empresas pertencem aos seus donos. Use-as só pra se referir ao produto de que você está falando.
- Nenhum som ou imagem de terceiros vem no repositório: os efeitos e a trilha são gerados por código.
- B-roll do [Pexels](https://www.pexels.com/license/) segue a licença do Pexels (uso grátis, crédito recomendado); o script só baixa pra sua máquina.
