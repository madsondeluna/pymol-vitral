# legacy

Scripts anteriores ao pacote `pymol_vitral`, mantidos por dois motivos.

`membrane_popc_style.pml` é um script linear, sem funções: aplica o mesmo estilo
de cima a baixo, na ordem em que os comandos rodam. É mais fácil de ler do que o
pacote quando o objetivo é entender ou modificar o que acontece, porque as
funções escondem a sequência.

`style_madson.pml` e `style_madson.py` são o estilo geral fora do contexto de
membrana ou de análise: proteína, ácido nucleico e ligante, sem a divisão em
objetos nem os presets.

Nenhum deles recebe manutenção. Para uso normal, prefira o pacote.
