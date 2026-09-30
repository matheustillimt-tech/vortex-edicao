# Melhoria contínua (todo vídeo)

A skill fica melhor a cada edição. Depois de entregar um vídeo:

1. **Colete o feedback** do que a pessoa achou: o que incomodou, o que faltou, o que ficou bom.
2. **Classifique** cada ponto:
   - regra de estilo (ex.: "sem som agudo");
   - defeito técnico (ex.: "câmera aparece duas vezes");
   - componente novo (ex.: "cursor clicando num print").
3. **Registre** antes de esquecer:
   - na lista de aprendizados da skill (o que pediu, a regra e o estado ✅/⏳);
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
