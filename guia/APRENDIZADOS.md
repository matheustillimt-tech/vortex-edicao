# Etapa 2 · Memória: aprendizados

**Toda correção que a pessoa faz vira regra, e a skill nunca mais erra a mesma coisa.** Editor humano esquece; este arquivo não.

- **Leia este arquivo inteiro antes de planejar qualquer vídeo** (junto com o `MOTIONS.md`). Regra daqui vence o `ESTILO.md`.
- **Escreva aqui** toda vez que a pessoa corrigir algo, no formato abaixo, na mesma sessão. Se a regra puder virar código (trava, padrão de função), faça também, e anote onde.
- Preferência que vale fora da edição (tom, como a pessoa gosta de receber as coisas) vai também na memória do Claude.

## Formato

```markdown
### AAAA-MM-DD · título curto
- **Pediu:** o que a pessoa disse, com as palavras dela
- **Regra:** frase direta, no imperativo
- **Onde está no código:** função ou trava (se tiver)
- **Estado:** ✅ funcionando · ⏳ testar no próximo vídeo
```

---

## Regras que já vêm com a skill

Aprendidas editando dezenas de vídeos de YouTube, Reels e aulas. Apague o que não servir pro seu estilo.

### Motion
- **O motion entra no FIM da fala**, nunca no começo da explicação. Âncora com `W("…", fim=True)`. Monta tudo em até **1,2 s** (stagger de 0,08 a 0,15 s) e, depois de montado, algo sempre se mexe (boia, ponto correndo, push-in) até sair. Motion parado esperando a próxima palavra deixa o vídeo lento. ✅
- **O texto na tela não copia a fala.** Palavra vazia não vai pra tela; adjetivo vira prova. Trava: `checa_texto.py`. ✅
- **Ao lado do rosto, só logo, número e inscrição.** ✅
- **Demonstração em cena branca de tela cheia**, sem a pessoa aparecer. Cor por emoção: verde positivo, vermelho negativo. ✅
- **Motion em cima do dedo:** quando a pessoa aponta, o objeto aparece onde o dedo está; trocou de mão, troca de lado. ✅

### Câmera e tela
- **Zoom em volta do rosto:** o rosto fica parado e só cresce, escala de no máximo 1,10. Rosto subindo ou andando a cada zoom parece manipulação. Código: `cn.bate()`. ✅
- **Círculo vermelho** (`#ef4444`) em número ou botão da tela gravada. O branco some em cima da tela. Código: `circulo()`. ✅
- **A tela aparece sempre inteira**, sem cortar palavra na borda. ✅
- **Exemplo mostrado (vídeo antigo, lousa) roda limpo**, sem zoom nem card por cima. ✅

### Cortes
- **Errou ou repetiu: fica a ÚLTIMA tentativa.** ✅
- **Nenhuma emenda come palavra.** A transcrição erra o tempo das palavras de vez em quando: a borda do corte vai até o silêncio real. ✅
- **Silêncio longo sai inteiro** (> 0,4 s), inclusive trecho com só ruído de teclado ou mouse. Depois de cortar, retranscreva o áudio final e compare com o texto pra achar tropeço que sobrou. ✅
- **A transcrição pode inventar palavras dentro de um silêncio longo.** Confira a energia do áudio de cada palavra suspeita e retranscreva o trecho. ✅

### Som e voz
- **Nada de som infantil** (bloop, sininho, glide) **nem tom agudo** ("piii"). Efeitos secos e discretos, concentrados na abertura e no fim. ✅
- **Voz com tratamento leve:** só passa-alta em 70 Hz + volume nivelado. Cadeia pesada (gate, EQ forte, isolamento) deixou a voz artificial. ✅
- **Trilha abaixando sozinha quando a pessoa fala** (ducking). Teste se ela fica melhor só na abertura ou no vídeo inteiro: depende do canal. ⏳

### Imagem
- **Gravação HDR de iPhone** (HEVC 10 bits HLG): converta pra SDR com tonemap `npl=203` e codifique a base com **libx264 CRF 15** (nunca o codificador de hardware, que borra pele e cabelo). Compare um recorte do rosto: original × base × final. ✅

---

## Aprendizados deste canal

<!-- Os seus entram aqui, do mais novo pro mais antigo. -->
