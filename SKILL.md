---
name: vortex-edicao
description: Edita vídeo de YouTube (e a abertura/vinheta do canal) 100% com IA — transcreve, corta erros e respiros (fica sempre a última tentativa), e monta motions ANCORADOS NA FALA com o HyperFrames (HTML → MP4) — pílulas com logo real, ícones que se desenham, prints e gravações de tela reais em cards de vidro, prompt digitando, cursor clicando, zoom com câmera em janelinha, círculo em número da tela, contador, trilha e efeitos sonoros sintetizados; cenas brancas com objeto em passos (gráfico que enche, celular com conversa, terminal digitando, check), lettering do gancho, lower third, b-roll grátis do Pexels, e uma trava que recusa texto que transcreve a fala. Estética clean e dopaminérgica: preto + branco brilhante, vidro, saída animada em tudo. Render rápido com cache. Ative em "edita esse vídeo", "edição dopaminérgica", "coloca motion nesse vídeo", "faz uma vinheta pro meu canal", "/vortex-edicao".
---

# Vórtex Edição de Vídeo

Transforma uma gravação bruta (câmera, ou tela + webcam) num vídeo com edição de alto ritmo, sem timeline manual. Quem edita é você (Claude): lê a transcrição, decide os cortes, escreve a LINHA DO TEMPO em Python ancorada nas palavras e renderiza.

Pasta desta skill = `$SKILL` (onde está este arquivo). Projetos ficam em `~/vortex-edicao-projetos/<nome>/` (ou `$VORTEX_PROJETOS`).

## O que ela faz

- Transcreve palavra a palavra e corta erros e respiros (fica a última tentativa).
- Motions ancorados na fala: logo real, ícone que se desenha, print e gravação de tela, prompt digitando, demonstração com cursor, zoom com câmera em janelinha, círculo em número da tela, contador.
- **Princípios de motion** (`guia/MOTIONS.md`): o motion não transcreve a fala; adjetivo vira prova; cena = objeto em passos com câmera correndo e check; ao lado do rosto só logo, número e inscrição.
- **Kit de cenas** (`cenas.py`, opcional): cena branca, gráfico que enche, celular com conversa e notificação, terminal, barras, pontos, chip riscado, lettering, lower third, b-roll, zoom seco centrado no rosto, checagem de ritmo.
- **Trava de texto** (`checa_texto.py`) no fim do build.
- **Webcam fixa** no zoom de tela (`webcam_fixa.py`).
- **B-roll grátis do Pexels** (`scripts/broll_pexels.py`).
- Sons e trilha sintetizados, master −14 LUFS, render rápido com cache.

## Novidades (outubro/2026)

- `guia/MOTIONS.md`: princípios de motion. **Leia antes de planejar** (valem mais que a tabela do `ESTILO.md`).
- `checa_texto.py`: o build recusa palavra vazia e frase copiada da transcrição.
- Kit de cenas `cenas.py` + `cenas.css`, `bate()` centrado no rosto (`"rosto"` no `config.json`), `broll()`.
- `webcam_fixa.py`: zoom de câmera dentro da tela não amplia a webcam.
- `scripts/broll_pexels.py`: b-roll grátis.
- `guia/GRAVACAO.md`: câmera e tela separadas com o Source Record do OBS.
- `render_rapido.py`: clip com data-start negativo é cortado no início do trecho (data-media-start ajustado); trechos de até 90 s.

## 0. Primeira vez na máquina

```bash
bash $SKILL/instalar.sh          # confere Node 22+, ffmpeg, Python; instala o resto; gera sons, fontes e logos
```

Transcrição: ElevenLabs (melhor, `ELEVENLABS_API_KEY` no `$SKILL/.env`) ou Whisper local (`pip install openai-whisper`). B-roll: `PEXELS_API_KEY` (grátis em pexels.com/api) no mesmo `.env`. **Nunca** peça chave no chat: peça pra pessoa colar no `.env`.

Se a pessoa ainda vai gravar, mostre o `$SKILL/guia/GRAVACAO.md` (câmera e tela em arquivos separados com o Source Record do OBS).

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
3. **Layout da gravação:** se for tela + webcam num canto, preencha `webcam` (px em 1920×1080) e, se a tela só aparece em parte do vídeo, `trechos_tela` no `config.json` do projeto. Com câmera cheia, meça o centro do rosto em `rosto` (o zoom seco gira em volta dele). Tire um quadro com grade pra medir:
   ```bash
   ffmpeg -ss 30 -i media/base.mp4 -frames:v 1 -vf "drawgrid=w=100:h=100:c=red@0.5" grade.png
   ```

## 2. Escrever a edição (a parte que é sua)

Abra `build.py` do projeto. Os helpers estão documentados no topo. Apague o EXEMPLO e escreva a LINHA DO TEMPO:
- **Tudo ancorado na fala:** `t = W("frase exata", apos)`. Nunca use segundo "chutado".
- Leia **`$SKILL/guia/MOTIONS.md`** e depois `$SKILL/guia/ESTILO.md`. O primeiro diz o que NÃO vira motion (e vence quando os dois discordam); o segundo tem densidade, o que vira qual motion, sons e armadilhas.
- **O motion não transcreve a fala.** Palavra vazia não vai pra tela; adjetivo vira prova (contador, `agua()`, chip riscado); texto de objeto é inventado e concreto (o prompt, a notificação), nunca o trecho falado. Fala citada de propósito vai com `class="fala-ok"`.
- **Kit de cenas (opcional):** `cn = carrega_cenas()`. Cena branca no FIM do raciocínio (5 a 7 s, ≥ 8 s de rosto entre cenas), 3 a 5 passos de objeto com `cn.corre()` e `cn.check()` no fim; ao lado do rosto só logo, número (`cn.num_lado`) e inscrição; `cn.letreiro` só no gancho; `cn.lower_third` quando a pessoa diz o nome; `cn.bate()` na palavra forte (nunca em trecho de tela); `cn.checa_ritmo()` no fim.
- **B-roll:** quando a fala pedir uma imagem genérica ("cidade", "dinheiro", "escritório"), busque no Pexels com o termo **em inglês** e use `cn.broll(de, ate, "midia/broll/<arquivo>.mp4")` (tela cheia) ou `card=True`:
  ```bash
  $SKILL/.venv/bin/python $SKILL/scripts/broll_pexels.py "city skyline night" -o midia/broll -n 2 --min 4 --max 15
  ```
  Sem chave, avise a pessoa (é grátis). B-roll gerado por IA (Higgsfield ou similar) é a opção avançada, paga: só quando não houver imagem de banco, e com a chave do provedor que a pessoa escolher.
- **Tela que a pessoa mostra fica sem motion:** só `zoom()` e `circulo()`; dado sensível com `cn.borrar()`.
- **Design system:** os motions já seguem as regras de ritmo e estética; a cor de destaque e a fonte da pessoa vão em `config.json → "marca"`, o resto em `estilo.css`/`cenas.css`.
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
$SKILL/.venv/bin/python build.py                     # no fim roda o checa_texto.py: tem que dar 0 problema
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
6. **Sincronize:** a cópia da skill no repositório da equipe, na mesma sessão.
7. **Pergunte no próximo vídeo** se a regra nova funcionou. Regra que não funcionou volta pro passo 1.
