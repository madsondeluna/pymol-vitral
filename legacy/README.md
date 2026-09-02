# legacy

Scripts anteriores ao pacote `pymol_molviz`, mantidos por dois motivos.

`membrane_popc_style.pml` e um script linear, sem funcoes: aplica o mesmo
estilo de cima a baixo, na ordem em que os comandos rodam. E mais facil de ler
do que o pacote quando o objetivo e entender ou modificar o que acontece,
porque as funcoes escondem a sequencia.

`style_madson.pml` e `style_madson.py` sao o estilo geral fora do contexto de
membrana ou de analise: proteina, acido nucleico e ligante, sem a divisao em
objetos nem os presets.

Nenhum deles recebe manutencao. Para uso normal, prefira o pacote.
