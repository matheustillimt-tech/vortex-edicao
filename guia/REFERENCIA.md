# Etapa 1 · Referência

**Sem referência, a IA entrega uma edição genérica, e é isso que deixa cara de IA.** Antes de gravar ou editar, escolha as referências e deixe o Claude analisar.

## Dois tipos de referência

| Tipo | Pra quê | Como escolher |
|---|---|---|
| **De vídeo** (tema e estrutura) | o que falar, em que ordem, como abrir e como fechar | um vídeo do seu nicho que **estourou num canal pequeno**: divida as views pelos inscritos. 68 mil views num canal de 4 mil inscritos = **17×**. Quanto maior, mais o tema puxou sozinho |
| **De edição** (estilo) | como o vídeo se parece: cor, fonte, ritmo, onde entra cada efeito e cada som | 2 ou 3 canais cuja edição você gosta. Se você já tem vídeos editados com a skill, o **seu último vídeo** entra aqui também, pra manter o padrão do canal |

## Passo a passo

1. **Baixe a referência:**
   ```bash
   bash $SKILL/scripts/referencia.sh "https://www.youtube.com/watch?v=..."
   ```
   Sai em `~/vortex-edicao-projetos/_referencias/<id>/`: `info.txt` (com o score), `capitulos.txt`, `transcricao.txt` e as folhas de quadros (`folha-abertura.jpg` e `folha-NN.jpg`).
2. **Leia** a transcrição e os capítulos, e **OLHE** cada folha de quadros.
3. **Escreva o `REFERENCIA.md`** na pasta da referência:
   - **Estrutura:** como abre (os primeiros 60 s frase a frase), quantos blocos ou etapas, onde fica a promessa, como fecha, qual é o CTA.
   - **Edição:** cada componente que se repete (barra de etapas, número gigante, janela de terminal, card ao lado do rosto, lower third), com o momento em que aparece e quanto dura.
   - **Ritmo:** quanto tempo de rosto entre os motions, densidade na abertura × no meio.
   - **Som:** trilha (o vídeo inteiro ou só a abertura) e quais movimentos têm efeito.
4. **Adapte, não copie.** Monte uma tabela "na referência → no meu" passando cada componente pelo seu design system (`config.json → "marca"`, `estilo.css`) e pelas regras do `guia/MOTIONS.md` e do `guia/APRENDIZADOS.md`. Exemplo:

   | Na referência | No meu |
   |---|---|
   | verde neon em fundo escuro | preto + branco brilhante |
   | número da etapa gigante em tela cheia | igual, na cor de destaque da marca |
   | palavra de ênfase ao lado do rosto | não entra: ao lado do rosto só logo, número e inscrição |

5. **Mostre a tabela pra pessoa** antes do planejamento de motions (etapa 6). É ela que vai guiar a linha do tempo.

## Cuidados

- A referência é **estrutura e linguagem**, nunca conteúdo: não copie o texto, o roteiro nem a identidade visual de outro canal.
- Não use a mídia da referência (trilha, imagem, trecho de vídeo) no seu vídeo.
- O YouTube às vezes bloqueia download em sequência ("Sign in to confirm you're not a bot"). Espere alguns minutos e tente de novo.
