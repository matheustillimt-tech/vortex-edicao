---
name: vortex-edicao
description: Edita vídeo de YouTube (e a abertura/vinheta do canal) 100% com IA — transcreve, corta erros e respiros (fica sempre a última tentativa), e monta motions ANCORADOS NA FALA com o HyperFrames (HTML → MP4) — pílulas com logo real, ícones que se desenham, prints e gravações de tela reais em cards de vidro, prompt digitando, cursor clicando, zoom com câmera em janelinha, círculo em número da tela, contador, trilha e efeitos sonoros sintetizados. Estética clean e dopaminérgica: preto + branco brilhante, vidro, saída animada em tudo. Render rápido com cache. Ative em "edita esse vídeo", "edição dopaminérgica", "coloca motion nesse vídeo", "faz uma vinheta pro meu canal", "/vortex-edicao".
---

# Vórtex Edição de Vídeo

Transforma uma gravação bruta (câmera, ou tela + webcam) num vídeo com edição de alto ritmo, sem timeline manual. Quem edita é você (Claude): lê a transcrição, decide os cortes, escreve a LINHA DO TEMPO em Python ancorada nas palavras e renderiza.

Pasta desta skill = `$SKILL` (onde está este arquivo). Projetos ficam em `~/vortex-edicao-projetos/<nome>/` (ou `$VORTEX_PROJETOS`).

## 0. Primeira vez na máquina

```bash
bash $SKILL/instalar.sh          # confere Node 22+, ffmpeg, Python; instala o resto; gera sons, fontes e logos
```

Transcrição: ElevenLabs (melhor, `ELEVENLABS_API_KEY` no `$SKILL/.env`) ou Whisper local (`pip install openai-whisper`). **Nunca** peça a chave no chat: peça pra pessoa colar no `.env`.

## 1. Transcrever e cortar

```bash
bash $SKILL/novo_projeto.sh <nome> <gravacao.mp4>        # cria o projeto e transcreve
```

1. **LEIA o `fonte/roteiro.txt` inteiro.** Marque:
   - erros e falsos começos ("não, pera…");
   - frases repetidas: **quando a pessoa repete, fica sempre a ÚLTIMA tentativa**;
   - trechos prolixos que não fazem falta.
2. Mostre a lista de cortes pra pessoa se houver dúvida. Depois rode:
   ```bash
   $SKILL/.venv/bin/python $SKILL/cortar.py ~/vortex-edicao-projetos/<nome> --remover 12.3-15.8,40-41.2
   ```
   Os respiros (> 0,32 s entre palavras) saem sozinhos.
3. **Layout da gravação:** se for tela + webcam num canto, preencha `webcam` no `config.json` do projeto (px em 1920×1080). Tire um quadro com grade pra medir:
   ```bash
   ffmpeg -ss 30 -i media/base.mp4 -frames:v 1 -vf "drawgrid=w=100:h=100:c=red@0.5" grade.png
   ```

## 2. Escrever a edição (a parte que é sua)

Abra `build.py` do projeto. Os helpers estão documentados no topo. Apague o EXEMPLO e escreva a LINHA DO TEMPO:
- **Tudo ancorado na fala:** `t = W("frase exata", apos)`. Nunca use segundo "chutado".
- Leia `$SKILL/guia/ESTILO.md` antes. Tem as regras de densidade, o que vira qual motion, sons e armadilhas.
- **Motions ilustrados primeiro** (`il.*`): se a pessoa fala de uma ferramenta, vai a logo real; se mostra um resultado, vai print ou gravação; se é um passo a passo, vai `il.demo` com cursor clicando. Texto sozinho só no gancho e em número.
- Prints e gravações de páginas públicas:
  ```bash
  node $SKILL/captura/capturar.mjs print <url> midia/x.png
  node $SKILL/captura/capturar.mjs gravar roteiro.json midia/y.mp4
  ```
  **Página logada, conta da pessoa ou mudança de configuração:** só com o OK dela. De preferência, ela grava. Nunca clique em nada que altere a conta.

Confira antes de renderizar:

```bash
cd ~/vortex-edicao-projetos/<nome>
$SKILL/.venv/bin/python build.py
HYPERFRAMES_SKIP_SKILLS=1 npx -y hyperframes lint | grep "error(s)"                      # tem que dar 0
HYPERFRAMES_SKIP_SKILLS=1 npx -y hyperframes snapshot --at 2,10,30 --no-end --describe false -o snap
```

**OLHE** o `snap/contact-sheet*.jpg`: texto cortado, card em cima do rosto, câmera duplicada, zoom mostrando borda.

## 3. Renderizar

```bash
$SKILL/.venv/bin/python render_rapido.py -o renders/v1.mp4
```

- Só os trechos com motion passam pelo navegador (em paralelo, com cache). O resto sai direto da gravação.
- Uma compressão só (x264 CRF 16) e master em −14 LUFS (padrão do YouTube).
- Num ajuste, rode de novo: só o trecho que mudou é refeito.

Entregue o caminho do arquivo e abra a pasta. Mídia pesada não vai pra repositório.

## Vinheta do canal (exemplo pronto)

```bash
$SKILL/.venv/bin/python $SKILL/exemplos/vinheta/criar_vinheta.py --canal @seucanal --nome "Seu Nome" \
    --bio "O que o canal ensina" --linha1 "IA APLICADA" --linha2 "A NEGÓCIOS" --chip "Vídeo novo toda semana" [--marca logo.png]
```

São 12 s: texto cinético, parede com as thumbnails reais do canal, a marca com anel de luz e a foto com "Inscrever-se" clicado. A música eletrônica é sintetizada, com drops casados com a imagem.

## Melhoria contínua (todo vídeo)

A skill fica melhor a cada edição. Depois de entregar um vídeo:

1. **Colete o feedback** do que a pessoa achou: o que incomodou, o que faltou, o que ficou bom.
2. **Classifique** cada ponto:
   - regra de estilo (ex.: "sem som agudo");
   - defeito técnico (ex.: "câmera aparece duas vezes");
   - componente novo (ex.: "cursor clicando num print").
3. **Registre** antes de esquecer:
   - em `guia/MELHORIA.md` (histórico) ou no `guia/ESTILO.md` (regra) (o que pediu, a regra e o estado ✅/⏳);
   - na memória, se for preferência da pessoa.
4. **Corrija na fonte**, não só no vídeo:
   - regra vira código no modelo (`build.py`, `ilustra.py`, `gerar_sons.py`);
   - defeito vira trava (ex.: teste de tom dos sons, +1 ms no início da mídia).
5. **Teste:**
   - `lint` com 0 erros;
   - `snapshot` dos quadros afetados;
   - render de um trecho;
   - comparação com a versão anterior.
6. **Sincronize:** a cópia da skill no repositório ou vault da equipe, na mesma sessão.
7. **Pergunte no próximo vídeo** se a regra nova funcionou. Regra que não funcionou volta pro passo 1.
