# molviz.pml
#
# Ponto de entrada. Carregue este arquivo de dentro do PyMOL:
#
#     run /caminho/pymol-molviz/molviz.pml
#
# Ele adiciona o diretorio do repositorio ao sys.path e registra todos os
# comandos. Nao e preciso instalar nada nem mexer no PYTHONPATH.
#
# Rodar de novo SEMPRE traz o codigo do disco. Sem a limpeza abaixo isso nao
# aconteceria: o import encontraria o pacote em sys.modules e devolveria o que
# esta na memoria, sem ler o arquivo e sem avisar, e uma edicao pareceria nao
# ter efeito nenhum.

python
import os, sys

# Descobre o diretorio deste arquivo, para o pacote ser encontrado
# independentemente de onde o repositorio foi colocado.
try:
    _here = os.path.dirname(os.path.abspath(__script__))
except NameError:
    _here = os.getcwd()

if _here not in sys.path:
    sys.path.insert(0, _here)

for _mod in [_m for _m in list(sys.modules)
             if _m == "pymol_molviz" or _m.startswith("pymol_molviz.")]:
    del sys.modules[_mod]

import pymol_molviz
pymol_molviz.load()
python end
