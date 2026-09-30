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

## Instalação

Precisa de **Node 22+**, **ffmpeg** e **Python 3**.

```bash
git clone https://github.com/matheustillimt-tech/vortex-edicao ~/.claude/skills/vortex-edicao
bash ~/.claude/skills/vortex-edicao/instalar.sh
```

Opcional (transcrição melhor): coloque sua chave da ElevenLabs no arquivo `.env` da pasta (`ELEVENLABS_API_KEY=...`). Sem chave, ela usa o Whisper local (`pip install openai-whisper`).

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
instalar.sh           instala tudo (uma vez)
novo_projeto.sh       cria o projeto de um vídeo
transcrever.py        1) prepara a gravação e transcreve
cortar.py             2) corta erros e respiros
modelo/build.py       3) a edição: ferramentas + LINHA DO TEMPO
modelo/ilustra.py     motions ilustrados
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
