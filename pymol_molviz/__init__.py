"""
pymol_molviz

Presets de visualizacao para PyMOL, voltados a sistemas de simulacao
molecular: membranas lipidicas, proteinas e peptideos.

Carregamento normal, de dentro do PyMOL:

    run /caminho/pymol-vitral/molviz.pml

Ou, se o pacote estiver no PYTHONPATH:

    import pymol_molviz; pymol_molviz.load()
"""

__version__ = "1.3.1"

_LOADED = False


def load(auto=True):
    """Registra todos os comandos e, opcionalmente, aplica um preset inicial.

    auto=True escolhe o preset conforme o conteudo da sessao: membrana se
    houver lipideos, proteina caso contrario. Passe auto=False para apenas
    registrar os comandos sem alterar a cena.
    """
    global _LOADED
    import os
    from pymol import cmd
    from pymol_molviz import core, membrane, protein

    core.register_common()
    membrane.register()
    protein.register()
    _LOADED = True

    print("[molviz] v%s carregado de %s" % (__version__, os.path.dirname(os.path.abspath(__file__))))
    print("[molviz] membrana: preset_memb1..10, memb_color, memb_water")
    print("[molviz] proteina: preset_prot1..10, prot_color, prot_water, "
          "prot_ions")
    print("[molviz] comum:    mv_ao, mv_shadows, mv_realism, mv_paper, "
          "mv_grayscale, mv_extent, mv_render")

    if not auto:
        return

    # Detecta o tipo de sistema pelo que esta carregado. Lipideo tem
    # precedencia: numa membrana com peptideo inserido, o modulo de membrana e
    # o que enquadra a cena corretamente.
    if not cmd.get_object_list("all"):
        print("[molviz] sessao vazia. Carregue uma estrutura e rode "
              "preset_memb1 ou prot_auto.")
        return

    if cmd.count_atoms("resn %s" % membrane.LIPID_RESN) > 0:
        membrane.preset1()
    else:
        protein.auto()
