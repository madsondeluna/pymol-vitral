"""Roda todos os presets contra os sistemas sinteticos e checa invariantes.

    /Applications/PyMOL.app/Contents/MacOS/PyMOL -cq tests/run_presets.py

Nao ha assercao sobre a aparencia: o que se verifica e o que ja quebrou na
pratica, e cada checagem corresponde a um defeito real.

  - o preset roda sem levantar excecao
  - os fatores B saem iguais aos que entraram (o mapa gaussiano escreve na
    coluna B para a gaussiana ter largura, e precisa devolver)
  - gaussian_resolution volta ao valor anterior
  - o preset que promete isosuperficie cria o objeto surf_*
  - a oclusao ambiente fica ligada, menos onde o preset a desliga de proposito
"""
import os
import sys
import traceback

from pymol import cmd

# O PyMOL executa o script com execfile sobre o namespace dele, entao aqui
# __file__ aponta para o pymol e __script__ vale 'toplevel'. A raiz sai do
# diretorio de trabalho, subindo ate encontrar o pacote.
def _raiz():
    cand = os.getcwd()
    for _ in range(4):
        if os.path.isdir(os.path.join(cand, "pymol_molviz")):
            return cand
        cand = os.path.dirname(cand)
    raise RuntimeError("rode a partir da raiz do repositorio: "
                       "pymol -cq tests/run_presets.py")


RAIZ = _raiz()
AQUI = os.path.join(RAIZ, "tests")
for caminho in (RAIZ, AQUI):
    if caminho not in sys.path:
        sys.path.insert(0, caminho)

import make_systems                                  # noqa: E402
from pymol_molviz import core, membrane, protein     # noqa: E402

# preset -> objeto que ele promete criar, e se a oclusao ambiente fica ligada.
PROMETE_SUPERFICIE = {"preset_memb5": "surf_tail", "preset_memb10": "surf_tail"}
AO_DESLIGADA = ("preset_memb6",)

falhas = []


def checa(cond, msg):
    if not cond:
        falhas.append(msg)
    return cond


def roda(rotulo, fn, modulo_obj, b_antes, espera_superficie=None,
         espera_ao=1):
    res_antes = cmd.get("gaussian_resolution")
    try:
        fn()
    except Exception:
        falhas.append("%s levantou excecao" % rotulo)
        traceback.print_exc()
        return

    b_depois = {}
    cmd.iterate(modulo_obj, "d[(model, index)] = b", space={"d": b_depois})
    checa(b_antes == b_depois, "%s alterou os fatores B" % rotulo)
    checa(cmd.get("gaussian_resolution") == res_antes,
          "%s deixou gaussian_resolution em %s" % (rotulo, cmd.get("gaussian_resolution")))
    if espera_superficie:
        checa(espera_superficie in cmd.get_names("objects"),
              "%s nao criou %s" % (rotulo, espera_superficie))
    checa(str(cmd.get("ambient_occlusion_mode")) == str(espera_ao),
          "%s deixou ambient_occlusion_mode em %s"
          % (rotulo, cmd.get("ambient_occlusion_mode")))
    print("  ok  %s" % rotulo)


def sessao(caminho, nome_obj="sistema"):
    cmd.delete("all")
    cmd.load(caminho, nome_obj)
    b = {}
    cmd.iterate(nome_obj, "d[(model, index)] = b", space={"d": b})
    return b


def suite():
    dest = os.path.join(AQUI, "systems")
    if not os.path.isdir(dest):
        os.makedirs(dest)
    make_systems.build(dest)

    casos = (
        ("membrana", "membrana.pdb", membrane, range(1, 11)),
        ("membrana com peptideo", "membrana_peptideo.pdb", membrane, range(1, 11)),
        ("peptideo sem agua nem cadeia", "peptideo.pdb", protein, range(1, 11)),
        ("complexo solvatado", "complexo_solvatado.pdb", protein, range(1, 11)),
    )

    for titulo, arquivo, modulo, indices in casos:
        pref = "memb" if modulo is membrane else "prot"
        print("\n%s (%s)" % (titulo, arquivo))
        b_antes = sessao(os.path.join(dest, arquivo))
        modulo.split()
        for i in indices:
            fn = getattr(modulo, "preset%d" % i, None)
            if fn is None:
                continue
            rotulo = "preset_%s%d" % (pref, i)
            roda(rotulo, fn, "sistema", b_antes,
                 PROMETE_SUPERFICIE.get(rotulo),
                 0 if rotulo in AO_DESLIGADA else 1)

    # O argumento paper: a mesma cena, agora ja em modo de periodico.
    print("\nmodo de periodico")
    sessao(os.path.join(dest, "membrana.pdb"))
    membrane.split()
    membrane.preset1(paper=85)
    checa(cmd.get("orthoscopic") in ("on", 1, "1"),
          "paper=85 nao ligou a projecao ortografica")
    checa(str(cmd.get("ray_shadow")) in ("off", "0", "0.00000"),
          "paper=85 nao desligou a sombra projetada")
    print("  ok  preset_memb1 paper=85")

    # Escala de cinza: as cores em uso viram luminancia e voltam iguais.
    print("\nescala de cinza")
    sessao(os.path.join(dest, "membrana.pdb"))
    membrane.split()
    membrane.preset1()
    antes = dict((n, cmd.get_color_tuple(i))
                 for n, i in cmd.get_color_indices() if n.startswith("mv_"))
    core.grayscale(1)
    cinza = dict((n, cmd.get_color_tuple(i))
                 for n, i in cmd.get_color_indices() if n.startswith("mv_"))
    mudou = [n for n in antes if antes[n] != cinza[n]]
    checa(mudou, "grayscale(1) nao converteu cor nenhuma")
    checa(all(len(set(cinza[n])) == 1 for n in mudou),
          "grayscale(1) deixou cor com canais diferentes")
    core.grayscale(0)
    depois = dict((n, cmd.get_color_tuple(i))
                  for n, i in cmd.get_color_indices() if n.startswith("mv_"))
    checa(antes == depois, "grayscale(0) nao devolveu as cores originais")
    print("  ok  grayscale converteu e devolveu %d cores" % len(mudou))

    # A superficie gaussiana com selecao vazia devolve False e nao explode.
    print("\ncasos de borda")
    cmd.select("vazio", "resn ZZZ")
    checa(core.gaussian_isosurface("s_x", "m_x", "vazio") is False,
          "gaussian_isosurface deveria devolver False para selecao vazia")
    print("  ok  isosuperficie sobre selecao vazia")


suite()
print("\n" + "=" * 60)
if falhas:
    print("FALHAS (%d):" % len(falhas))
    for f in falhas:
        print("  - %s" % f)
else:
    print("todos os presets passaram")
