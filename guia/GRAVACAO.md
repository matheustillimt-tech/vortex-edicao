# Como gravar

Metade da edição está na gravação. A regra mais importante: **câmera e tela em arquivos separados**.

## Por que separar

| Jeito | O que dá pra fazer na edição |
|---|---|
| **Separado (recomendado):** a câmera num arquivo, a tela em outro | câmera cheia nítida com zoom no rosto, tela inteira com zoom e círculo, câmera em janelinha sem duplicar |
| **Único:** a tela com a webcam "colada" num canto (cena pronta do OBS, Screen Studio, Tella) | funciona, mas a câmera é um recorte pequeno. Todo zoom na tela leva a webcam junto, então o motor precisa tampar e devolver a webcam por cima (`webcam_fixa.py`). Se o gravador muda de layout no meio, o recorte fixo quebra naquele trecho |

> **Estado do motor:** hoje o `transcrever.py` recebe **um** arquivo. Com a gravação separada, monte o arquivo de entrada juntando os dois (veja "Juntar câmera e tela" abaixo) ou edite só a câmera. A entrada nativa com dois arquivos (`--camera` + `--tela`, sincronizados pelo áudio) ainda não está implementada.

## Câmera e tela separadas no OBS (plugin Source Record)

O plugin gratuito **Source Record** grava cada fonte do OBS no próprio arquivo, ao mesmo tempo, com o mesmo botão "Iniciar gravação".

**Instalar**
1. Feche o OBS.
2. Baixe o plugin na página do Source Record no fórum do OBS (obsproject.com/forum/resources/source-record.1285) → "Go to download" → o instalador do seu sistema. Use a versão compatível com o seu OBS.
3. Instale e abra o OBS de novo.

**Configurar a câmera** (a fonte da webcam)
1. Botão direito na fonte da câmera → **Filtros** → **+** → **Source Record**.
2. Ajuste:
   - **Record Mode:** Recording (grava junto com o botão principal);
   - **Path:** uma pasta só pra isso, ex.: `~/Movies/OBS/separado`;
   - **Filename:** `%CCYY-%MM-%DD %hh-%mm-%ss CAMERA`;
   - **Format:** mp4 (ou hybrid mp4, que não corrompe se o computador travar);
   - **Encoder:** o de hardware (Apple VT H264 no Mac, NVENC na NVIDIA), ~12 Mbps;
   - **Audio track:** 1, a faixa com o microfone. É ela que permite sincronizar os dois arquivos pelo som.

**Configurar a tela** (a fonte de captura de tela)
1. Mesmo caminho e o mesmo filtro.
2. Ajuste:
   - **Filename:** `%CCYY-%MM-%DD %hh-%mm-%ss TELA`;
   - **Encoder:** o mesmo, ~10 Mbps (tela comprime bem);
   - **Audio track:** 1.

**Gravação principal do OBS**
- Nos primeiros vídeos, mantenha ligada como backup.
- Depois de 2 ou 3 vídeos que deram certo, baixe pra ~6 Mbps ou desligue, pra economizar disco.

**Teste antes do primeiro vídeo:** grave 30 s e confira se saíram 2 arquivos (CAMERA e TELA), **com áudio nos dois**.

**Disco (25 min de vídeo, valores aproximados):**
| Gravação | Tamanho |
|---|---|
| Só a gravação principal | ~3–4 GB |
| Separado + principal de backup | ~7–8 GB |
| Só separado | ~4 GB |

Os brutos saem do computador depois que o vídeo for publicado.

## Juntar câmera e tela (enquanto o motor recebe um arquivo só)

Os dois arquivos começam juntos (mesmo botão), então dá pra montar a entrada com a câmera num canto, no lugar que você quiser, e preencher `webcam` no `config.json` com esse retângulo:

```bash
ffmpeg -i "… TELA.mp4" -i "… CAMERA.mp4" -filter_complex \
  "[0:v]scale=1920:1080[t];[1:v]scale=-2:726,crop=453:726[c];[t][c]overlay=1467:324[v]" \
  -map "[v]" -map 1:a -c:v libx264 -crf 16 -c:a aac gravacao.mp4
# config.json → "webcam": {"x":1467,"y":324,"w":453,"h":726}
```

Se os arquivos não começarem juntos, bata uma palma no início e alinhe com `-itsoffset`.

## Enquadramento e fala

- Rosto centralizado, olhos no terço superior e **espaço sobrando dos lados**: os letterings e os números entram no lado livre.
- Meça o centro do rosto num quadro com grade e ponha em `"rosto": [x, y]` no `config.json`:
  ```bash
  ffmpeg -ss 20 -i media/base.mp4 -frames:v 1 -vf "drawgrid=w=100:h=100:c=red@0.5" grade.png
  ```
- **Abra no meio da frase de impacto**, sem "fala pessoal, tudo bem?". Nos primeiros 3 s, a prova (número, resultado).
- **Dê gatilhos concretos:** números, nomes de ferramentas, listas faladas item a item, pedidos citados ("aí eu pedi: me manda um relatório todo dia às 19h"). Cada um vira um objeto na tela.
- Errou? **Repita a frase inteira** depois de uma pausa. A edição fica com a última tentativa.
