# Princípios de motion

Leia antes de planejar a LINHA DO TEMPO. **Estes princípios valem mais que qualquer tabela de "fala → motion"**: quando um gatilho da fala pedir texto na tela, confira aqui se ele passa.

O erro que eles evitam: motion que repete a fala. Quando o texto que aparece é a mesma frase que a pessoa acabou de dizer, a edição fica rígida, ao pé da letra, e **parece feita por IA**. O motion tem que acrescentar alguma coisa que a fala sozinha não mostra.

## 1. O motion não transcreve a fala

- **Palavra vazia nunca vai pra tela.** Advérbio, conectivo, intensificador ou adjetivo solto ("principalmente", "basicamente", "realmente", "muito", "sensacional", "incrível", "absurdo") não ganha motion. Se só sobrou isso, não tem motion.
- **O texto dos objetos é inventado, concreto e curto:** o prompt que a pessoa digitaria, o nome do arquivo, a mensagem do cliente, a notificação "Pagamento recebido · pedido #1042". Nunca é o trecho transcrito.
- A fala literal só entra quando **é** um prompt ou uma pergunta citada. Aí ela vai dentro de uma caixa de prompt ou de um balão digitando, marcada com `class="fala-ok"`.
- **Pergunta ou objeção do público** vira balão de chat digitando ("Tá, mas e se eu não souber programar?").
- **Trava:** o `checa_texto.py` roda no fim do `build.py` e recusa palavra vazia sozinha e texto que repete 5 ou mais palavras seguidas da fala.

## 2. Adjetivo vira prova

Não escreva o adjetivo: mostre o que o comprova.

| A pessoa diz… | Na tela |
|---|---|
| qualidade ("ficou muito melhor") | check, barra subindo ou antes × depois |
| dinheiro ou tamanho ("é muito dinheiro") | contador R$ ou gráfico que enche (`agua()`) |
| "sem X" ("sem dor de cabeça") | chip "X" sendo riscado (`riscavel()` + `risca()`) |
| "vários X" ("vários prompts") | nuvem de X reais e concretos ("refaz tudo", "muda a cor", "não, assim não"…) |
| "de graça" | preço zerado + o limite visível |
| "crescendo" | linha subindo |

| Fala | Errado | Certo |
|---|---|---|
| "principalmente no seu nicho" | "principal-mente" gigante ao lado do rosto | nada pra palavra; se houver motion, é do substantivo (uma lupa varrendo nichos) |
| "é um mercado sensacional" | card "🔥 mercado sensacional" | notificações de venda empilhando com o gráfico subindo atrás, nenhum adjetivo escrito |
| "por uma boa grana" | card "boa grana" | contador subindo de 300 para 2.000 |
| "design e código já resolvidos" | card com a frase | editor com código + selos de check, sem as palavras |

## 3. Cena = objeto em passos, com a câmera correndo e check no fim

- **O texto nunca é o protagonista.** Toda cena tem um OBJETO principal: janela, caixa de prompt digitando, arquivo, card de produto, barra, gráfico, chip, logo, celular, notificação.
- O título é opcional e pequeno: ~46 px em 1080p, no topo, **1 a 4 palavras**, com a última em destaque. As palavras entram junto com a fala, de cinza claro pra preto.
- **Cada cena é um raciocínio em 3 a 5 passos de objeto:**
  - um passo a cada 1 a 3 s;
  - a câmera virtual corre pro lado a cada objeto novo e o anterior sai pela borda (`corre()`);
  - termina com um **check** no objeto principal (`selo()` + `check()`, com o som de "deu certo");
  - não é um card parado com duas linhas.
- A cena entra **no fim do raciocínio**, dura 5 a 7 s (uma demonstração contínua pode durar mais) e monta em até 2 s.
- Entre duas cenas, **pelo menos 8 s de rosto** (`checa_ritmo()` avisa).
- **Frase-ponte de texto puro** dura no máximo ~1 s: pequena, no centro, e passa direto pra um objeto.
- **Família visual única:** fundo branco radial com vinheta cinza nos cantos; preto e um azul de destaque; verde só pra "ligado/ok", vermelho só pra erro/risco; emoji em ALGUNS momentos, de preferência dentro de um card de interface, nunca como enfeite solto.

## 4. Ao lado do rosto, só logo, número e inscrição

Sobre a câmera cheia entram três coisas:
- **logo** da ferramenta ou marca citada;
- **número** contando (R$, usuários, %), com `num_lado()`;
- o **banner de inscrição**.

Nada de palavra gigante e nada de card com frase ao lado do rosto. A câmera não fica parada: `bate()` dá um zoom seco na palavra forte **em volta do rosto** (o rosto cresce, mas não sobe, não desce e não anda; escala de no máximo 1,10). Meça `"rosto": [x, y]` no `config.json`.

## 5. Letterings só nas frases-chave do início

A exceção ao item 4, e só no começo do vídeo:
- **4 a 6 letterings** no gancho e na apresentação (`letreiro()`);
- cada um com **2 a 5 palavras do núcleo** (tese, número, promessa), em tipografia forte, no lado livre do rosto;
- **2,5 a 4 s** cada, com um zoom seco na palavra forte;
- nunca palavra vazia e nunca a frase inteira.

## 6. Lower third bonito no nome

Quando a pessoa diz o próprio nome, entra um lower third (`lower_third()`) de 5 a 6 s, no terço inferior e longe do banner de inscrição:
- nome grande subindo por uma máscara;
- uma linha que se desenha;
- 1 ou 2 credenciais, cada uma com a **logo real** ("Fundador · Sua Empresa").

## 7. Painéis explicativos quando a explicação é um mecanismo prático

Quando a pessoa explica **como uma coisa funciona** (um fluxo, uma rede de parceiros, um funil), o meio do vídeo ganha painéis:
- card branco grande com objetos ligados por linhas e contadores (ex.: parceiro → indicados → clientes, cada um com o número subindo);
- **4 a 6 painéis** por explicação, cada um com 3 a 5 passos e 6 a 12 s;
- respiro de 6 a 8 s sem nada entre eles.

## 8. A tela que a pessoa mostra fica sem motion

Se ela está mostrando a tela, **deixe a tela falar**: só zoom e círculo (`zoom()`, `circulo()`). Trechos de 45 a 90 s sem nada por cima são normais.
- Dado sensível na tela (nome de cliente, e-mail): `borrar()`.
- Na gravação com a webcam dentro da tela, o zoom não pode levar a webcam junto: a camada `webcam_fixa.py` mantém a webcam parada e inteira por cima. A solução definitiva é gravar câmera e tela separadas (`guia/GRAVACAO.md`).

## Checklist antes do render

1. Nenhum texto repete a fala (o `build.py` roda o `checa_texto.py`).
2. Toda cena tem um objeto e termina com check.
3. Ao lado do rosto, só logo, número e inscrição (fora os letterings do começo).
4. `checa_ritmo()` sem problema: ≥ 8 s de rosto entre cenas.
5. Snapshot conferido: nada em cima do rosto, nada cortado na borda.
