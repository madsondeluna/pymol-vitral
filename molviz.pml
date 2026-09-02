# molviz.pml
#
# Ponto de entrada. Carregue este arquivo de dentro do PyMOL:
#
#     run /caminho/pymol-molviz/molviz.pml
#
# Ele adiciona o diretorio do repositorio ao sys.path e registra todos os
# comandos. Nao e preciso instalar nada nem mexer no PYTHONPATH.

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

import pymol_molviz
pymol_molviz.load()
python end
