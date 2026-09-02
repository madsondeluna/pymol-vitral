# Proteina solvatada, saida de dinamica molecular.
#
# Antes de abrir o PyMOL, corrija a imagem periodica no terminal:
#
#   gmx trjconv -s topol.tpr -f traj.xtc -o frame.pdb -pbc mol -center -dump 0
#
# Sem isso, a camada de solvatacao sai vazia ou errada.

preset_prot7

# Ajuste os raios conforme a pergunta. 4 A pega a primeira camada; 6 a 8 A
# pega tambem a segunda e a atmosfera ionica.
prot_water shell, 4.0
prot_ions shell, 6.0

mv_ao medium
mv_shadows off
ray 1600, 1200
