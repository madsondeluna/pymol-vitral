"""Renderiza cada preset em tres orientacoes, para a galeria do README.

    /Applications/PyMOL.app/Contents/MacOS/PyMOL -cq tests/make_gallery.py

Sao 20 presets por 3 vistas, 60 imagens, e o sistema de membrana tem 64 mil
atomos: a corrida inteira leva dezenas de minutos. Por isso o script pula o que
ja existe em docs/img, e pode ser interrompido e retomado sem perder trabalho.

As tres vistas nao sao arbitrarias. Membrana: de lado, que e como se le uma
bicamada; de topo, que mostra o empacotamento no plano; e oblíqua. Proteina:
frente, o giro de 90 graus e o de 180, que e a face oposta.
"""
import os
import sys

from pymol import cmd


def _raiz():
    cand = os.getcwd()
    for _ in range(4):
        if os.path.isdir(os.path.join(cand, "pymol_molviz")):
            return cand
        cand = os.path.dirname(cand)
    raise RuntimeError("rode a partir da raiz do repositorio")


RAIZ = _raiz()
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

import pymol_molviz                                   # noqa: E402
from pymol_molviz import membrane, protein            # noqa: E402

SAIDA = os.path.join(RAIZ, "docs", "img")
LARGURA, ALTURA, DPI = 560, 440, 90

# Folga em angstrom em volta do que se enquadra, por sistema. Sao diferentes
# porque os dois objetos tem forma diferente: a bicamada e larga e fina e
# preenche a largura do quadro, entao pede folga maior para nao encostar na
# borda; a proteina e globular e com a mesma folga sairia pequena demais para
# se ver detalhe.
MARGEM_MEMB = 6
MARGEM_PROT = 3

# (rotulo, giros aplicados sobre a vista de referencia)
#
# Os tres angulos sao os mesmos nos dois sistemas: de lado, de cima e a quina.
#
# A referencia da MEMBRANA e a vista canonica do 'reset', onde z aponta para o
# observador e a bicamada aparece de topo. Nao da para usar o enquadramento do
# preset: '_finish' chama 'orient', que alinha o maior eixo do objeto com a
# horizontal da tela, e numa bicamada, que e plana em xy, isso devolve a vista
# de topo com o rotulo 'lado'.
#
# A referencia da PROTEINA e o 'orient' que o preset deixou, que e a vista mais
# informativa de uma molecula globular.
VISTAS_MEMB = (("lado", [("x", 90)]),
               ("cima", []),
               ("quina", [("x", 55), ("y", 35)]))
VISTAS_PROT = (("lado", []),
               ("cima", [("x", 90)]),
               ("quina", [("x", 45), ("y", 45)]))


def render(modulo, prefixo, indices, vistas, arquivo, obj_zoom, margem,
           reset_camera=False):
    cmd.delete("all")
    cmd.load(arquivo, "sistema")
    modulo.split()
    cmd.set("ray_opaque_background", 1)
    # Projecao ortografica: em perspectiva um folheto plano parece curvo, e a
    # comparacao entre as tres vistas deixa de valer porque o que esta mais
    # perto da camera aparece maior.
    cmd.set("orthoscopic", 1)

    for i in indices:
        fn = getattr(modulo, "preset%d" % i, None)
        if fn is None:
            continue
        nome = "%s%d" % (prefixo, i)
        destinos = [os.path.join(SAIDA, "%s_%s.png" % (nome, v))
                    for v, _ in vistas]
        if all(os.path.exists(d) for d in destinos):
            print("PULA   %s (ja existe)" % nome)
            continue

        fn()
        # O preset pode religar a perspectiva pelo material.
        cmd.set("orthoscopic", 1)
        if reset_camera:
            cmd.reset()
        # A vista de referencia e uma so: cada giro parte dela, e nao do giro
        # anterior, senao a terceira vista acumularia os tres.
        base = cmd.get_view()
        for (rotulo, giros), destino in zip(vistas, destinos):
            cmd.set_view(base)
            for eixo, ang in giros:
                cmd.turn(eixo, ang)
            if obj_zoom and cmd.count_atoms(obj_zoom):
                # complete=1 e o que garante que a geometria INTEIRA caiba:
                # sem ele o zoom enquadra pelo centro e por um raio aproximado,
                # e uma bicamada, que e larga e fina, sai cortada nas bordas.
                cmd.zoom(obj_zoom, margem, complete=1)
            cmd.png(destino, LARGURA, ALTURA, dpi=DPI, ray=1)
            print("OK     %s" % os.path.basename(destino))


if not os.path.isdir(SAIDA):
    os.makedirs(SAIDA)

pymol_molviz.load(auto=False)

render(protein, "prot", range(1, 11), VISTAS_PROT,
       os.path.join(RAIZ, "prot", "4hhb.pdb"), "obj_prot", MARGEM_PROT)
render(membrane, "memb", range(1, 11), VISTAS_MEMB,
       os.path.join(RAIZ, "memb", "bilbo_preview.pdb"), "obj_lipid",
       MARGEM_MEMB, reset_camera=True)

print("GALERIA COMPLETA")
