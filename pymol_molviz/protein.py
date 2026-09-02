"""
pymol_molviz.protein

Presets de visualizacao para proteinas e peptideos.

Divide o sistema em objetos independentes (obj_prot, obj_nucl, obj_lig,
obj_ions, obj_wat) e aplica combinacoes de representacao, cor e solvente.
"""

from pymol import cmd
from pymol_molviz import core
from pymol_molviz.core import has, truthy, n_residues


# =============================================================================
# Nomenclatura e escalas
# =============================================================================
BASIC = "ARG+LYS+HIS"
ACIDIC = "ASP+GLU"
POLAR = "SER+THR+ASN+GLN+TYR+CYS+TRP+HIS"
APOLAR = "ALA+VAL+LEU+ILE+MET+PHE+PRO+GLY"

# Escala Kyte-Doolittle: a mais citada e a que melhor separa nucleo de
# superficie. Trocar por outra escala e substituir este dicionario.
KD = {
    "ILE": 4.5, "VAL": 4.2, "LEU": 3.8, "PHE": 2.8, "CYS": 2.5, "MET": 1.9,
    "ALA": 1.8, "GLY": -0.4, "THR": -0.7, "SER": -0.8, "TRP": -0.9,
    "TYR": -1.3, "PRO": -1.6, "HIS": -3.2, "GLU": -3.5, "GLN": -3.5,
    "ASP": -3.5, "ASN": -3.5, "LYS": -3.9, "ARG": -4.5,
}

OBJECTS = ["obj_prot", "obj_nucl", "obj_lig", "obj_ions", "obj_wat"]

# Fatores B originais, salvos antes que um esquema de cor os sobrescreva.
_SAVED_B = []

PEPTIDE_CUTOFF = 60


def _is_peptide():
    """Abaixo de 60 residuos o cartoon comunica pouco: nao ha topologia global
    a resumir, e a informacao esta na cadeia lateral. Relevante para peptideos
    antimicrobianos, onde o padrao de carga e o objeto de estudo."""
    n = n_residues("obj_prot")
    return 0 < n < PEPTIDE_CUTOFF


# =============================================================================
# Preparacao
# =============================================================================
def split(keep_source=0, dss=1):
    """Divide o sistema carregado em objetos independentes.

    Edge case: cmd.create copia todos os estados. Numa trajetoria longa isso
    duplica a memoria; carregue apenas o frame de interesse antes.
    """
    sources = core.source_objects(OBJECTS)
    if not sources:
        print("[prot] nada carregado.")
        return

    src = " or ".join(sources)
    cmd.select("_wat", "(%s) and resn %s" % (src, core.WATER_RESN))
    cmd.select("_ions", "(%s) and resn %s" % (src, core.ION_RESN))
    cmd.select("_prot", "(%s) and polymer.protein" % src)
    cmd.select("_nucl", "(%s) and polymer.nucleic" % src)
    cmd.select("_lig",
               "(%s) and not (_wat or _ions or _prot or _nucl) and not hydro"
               % src)

    for obj, sel in (("obj_prot", "_prot"), ("obj_nucl", "_nucl"),
                     ("obj_lig", "_lig"), ("obj_ions", "_ions"),
                     ("obj_wat", "_wat")):
        cmd.delete(obj)
        if has(sel):
            cmd.create(obj, sel)

    for tmp in ("_wat", "_ions", "_prot", "_nucl", "_lig"):
        cmd.delete(tmp)

    if not truthy(keep_source):
        for s in sources:
            cmd.disable(s)

    # Saida de MD e varios modelos vem sem os registros HELIX/SHEET, e sem
    # eles o cartoon sai todo em loop. E o erro silencioso mais comum ao
    # visualizar estrutura de trajetoria.
    if truthy(dss) and has("obj_prot"):
        if not has("obj_prot and (ss H or ss S)"):
            cmd.dss("obj_prot")
            print("[prot] estrutura secundaria atribuida com dss.")

    _save_bfactors()
    print("[prot] objetos: %s | residuos: %d"
          % (", ".join(o for o in OBJECTS if has(o)), n_residues("obj_prot")))


def _save_bfactors():
    """Guarda os fatores B originais.

    Necessario porque colorir por hidrofobicidade exige escrever na coluna B:
    o PyMOL nao tem campo generico por atomo para gradiente. Sem isso, o
    esquema de cor destruiria silenciosamente um dado experimental.
    """
    global _SAVED_B
    _SAVED_B = []
    if has("obj_prot"):
        cmd.iterate("obj_prot", "_SAVED_B.append(b)",
                    space={"_SAVED_B": _SAVED_B})


def restore_bfactors():
    """Restaura os fatores B apos um esquema que os sobrescreveu."""
    if not _SAVED_B or not has("obj_prot"):
        print("[prot] nada salvo para restaurar.")
        return
    it = iter(_SAVED_B)
    cmd.alter("obj_prot", "b=next(it)", space={"it": it, "next": next})
    cmd.sort("obj_prot")
    print("[prot] fatores B restaurados.")


def prepare():
    core.material()
    if not has("obj_prot") and not has("obj_nucl"):
        split()
    return has("obj_prot") or has("obj_nucl")


def _reset():
    for obj in ("surf_wat", "map_wat", "obj_ions_halo", "wat_shell",
                "ions_shell"):
        cmd.delete(obj)
    core.clear_reps(OBJECTS)


# =============================================================================
# Cor
# =============================================================================
def _col_ss():
    cmd.color("mv_loop", "obj_prot")
    cmd.color("mv_helix", "obj_prot and ss H")
    cmd.color("mv_sheet", "obj_prot and ss S")


def _col_chain():
    # get_chains devolve [''] quando o arquivo nao traz identificador de
    # cadeia, o que e comum em saida de dinamica molecular. 'chain ' sem
    # argumento e selecao malformada, entao a cadeia vazia vai entre aspas.
    chains = cmd.get_chains("obj_prot")
    for i, ch in enumerate(chains):
        cmd.color(core.CHAIN_CYCLE[i % len(core.CHAIN_CYCLE)],
                  "obj_prot and chain '%s'" % ch)
    nomeadas = [c for c in chains if c.strip()]
    if nomeadas:
        print("[prot] cadeias: %s" % ", ".join(nomeadas))
    elif chains:
        print("[prot] o arquivo nao traz identificador de cadeia: uma cor so.")


def _col_charge():
    """Carga formal em pH neutro.

    His fica no grupo basico por convencao, embora esteja majoritariamente
    neutra em pH 7,4. Se isso importar na sua analise, mova-a para POLAR.
    """
    cmd.color("grey70", "obj_prot")
    cmd.color("mv_apolar", "obj_prot and resn %s" % APOLAR)
    cmd.color("mv_polar", "obj_prot and resn %s" % POLAR)
    cmd.color("mv_neg", "obj_prot and resn %s" % ACIDIC)
    cmd.color("mv_pos", "obj_prot and resn %s" % BASIC)


def _col_hydro():
    """Gradiente Kyte-Doolittle. Sobrescreve a coluna B."""
    cmd.alter("obj_prot", "b=KD.get(resn, 0.0)", space={"KD": KD})
    cmd.sort("obj_prot")
    cmd.spectrum("b", "marine_white_orange", "obj_prot",
                 minimum=-4.5, maximum=4.5)
    print("[prot] azul = hidrofilico, laranja = hidrofobico. "
          "Fatores B sobrescritos; prot_restore_b desfaz.")


def _col_bfactor():
    """Fator B como esta no arquivo.

    Em estrutura experimental mede desordem ou resolucao local; em modelo
    predito costuma carregar pLDDT, cuja escala significa o oposto. Confira a
    origem antes de interpretar.
    """
    cmd.spectrum("b", "blue_white_red", "obj_prot")


def _col_rainbow():
    cmd.spectrum("count", "rainbow", "obj_prot and name CA+P")


COLORS = {"ss": _col_ss, "chain": _col_chain, "charge": _col_charge,
          "hydro": _col_hydro, "bfactor": _col_bfactor,
          "rainbow": _col_rainbow}


def color(scheme="ss"):
    """Esquema de cor: ss, chain, charge, hydro, bfactor, rainbow."""
    if scheme not in COLORS:
        print("[prot] esquemas: %s" % ", ".join(sorted(COLORS)))
        return
    if not has("obj_prot"):
        print("[prot] obj_prot vazio.")
        return
    COLORS[scheme]()
    _color_context()
    print("[prot] cor: %s" % scheme)


def _color_context():
    if has("obj_lig"):
        cmd.color("mv_lig", "obj_lig")
        cmd.color("grey70", "obj_lig and elem C")
    if has("obj_nucl"):
        cmd.color("mv_dna_bb", "obj_nucl")
        cmd.color("mv_dna_p", "obj_nucl and name P+OP1+OP2+O1P+O2P")
    if has("obj_ions"):
        cmd.color("mv_na", "obj_ions and resn NA+SOD")
        cmd.color("mv_cl", "obj_ions and resn CL+CLA")
        cmd.color("forest", "obj_ions and resn MG")
        cmd.color("slate", "obj_ions and resn ZN")
    if has("obj_wat"):
        cmd.color("mv_water", "obj_wat")


# =============================================================================
# Solvente e ions
# =============================================================================
def water(mode="shell", radius=4.0, transparency=0.62):
    """Agua: off, shell, spheres, surface, field.

    'shell' e o padrao e o unico conceito que nao existe no modulo de
    membranas: exibe apenas as aguas dentro de 'radius' da proteina. Numa
    caixa de MD tipica o solvente de bulk passa de 90% dos atomos e esconde o
    soluto, enquanto a primeira camada de solvatacao costuma ser o objeto de
    interesse.
    """
    for obj in ("surf_wat", "map_wat", "wat_shell"):
        cmd.delete(obj)

    # A checagem vem antes do hide: sem agua na estrutura o objeto nao existe,
    # e hide sobre nome inexistente levanta 'Invalid selection name'.
    if not has("obj_wat"):
        return
    for rep in ("surface", "spheres", "sticks", "lines", "nonbonded"):
        cmd.hide(rep, "obj_wat")
    if mode == "off":
        return

    if mode == "shell":
        # 'byres' evita meia molecula: sem ele, um oxigenio entraria e seus
        # hidrogenios ficariam de fora.
        cmd.select("wat_shell",
                   "byres (obj_wat within %.1f of obj_prot)" % float(radius))
        n = cmd.count_atoms("wat_shell")
        if n == 0:
            print("[prot] nenhuma agua a %.1f A. Causa provavel: imagem "
                  "periodica. Corrija com 'gmx trjconv -pbc mol -center'."
                  % float(radius))
            return
        cmd.show("spheres", "wat_shell")
        cmd.set("sphere_scale", 0.30, "obj_wat")
        cmd.set("sphere_transparency", 0.25, "obj_wat")
        cmd.color("mv_water", "obj_wat")
        cmd.deselect()
        print("[prot] camada de solvatacao: %d atomos a %.1f A"
              % (n, float(radius)))
    elif mode == "spheres":
        cmd.show("spheres", "obj_wat")
        cmd.set("sphere_scale", 0.30, "obj_wat")
        cmd.set("sphere_transparency", 0.75, "obj_wat")
        cmd.color("mv_water", "obj_wat")
    elif mode == "surface":
        cmd.select("wat_o", "obj_wat and (elem O or name W+PW+OW)")
        cmd.alter("wat_o", "vdw=3.3")
        cmd.rebuild()
        cmd.show("surface", "wat_o")
        cmd.color("mv_water", "obj_wat")
        cmd.set("transparency", float(transparency), "obj_wat")
        cmd.deselect()
    elif mode == "field":
        cmd.select("wat_o", "obj_wat and (elem O or name W+PW+OW)")
        if not core.gaussian_isosurface("surf_wat", "map_wat", "wat_o",
                                        grid=1.5, resolution=4.0,
                                        label="prot"):
            cmd.deselect()
            return
        cmd.color("mv_water", "surf_wat")
        cmd.set("transparency", float(transparency), "surf_wat")
        cmd.deselect()
    else:
        print("[prot] modos: off, shell, spheres, surface, field")
        return
    print("[prot] agua: %s" % mode)


def ions(mode="spheres", radius=6.0):
    """Ions: off, spheres, vdw, halo, mesh, shell.

    'shell' exibe apenas os ions dentro de 'radius' da proteina — os
    coordenados ou na atmosfera ionica. Numa caixa neutralizada, a maioria dos
    contra-ions esta no bulk e nao diz nada sobre a proteina.
    """
    cmd.delete("obj_ions_halo")
    cmd.delete("ions_shell")
    if not has("obj_ions"):
        return
    for rep in ("spheres", "mesh", "nonbonded", "surface"):
        cmd.hide(rep, "obj_ions")
    if mode == "off":
        return

    if mode == "shell":
        cmd.select("ions_shell",
                   "obj_ions within %.1f of obj_prot" % float(radius))
        n = cmd.count_atoms("ions_shell")
        if n == 0:
            print("[prot] nenhum ion a %.1f A." % float(radius))
            return
        cmd.show("spheres", "ions_shell")
        cmd.set("sphere_scale", 0.6, "obj_ions")
        cmd.deselect()
        print("[prot] %d ions a %.1f A" % (n, float(radius)))
    elif mode == "spheres":
        cmd.show("spheres", "obj_ions")
        cmd.set("sphere_scale", 0.5, "obj_ions")
    elif mode == "vdw":
        cmd.show("spheres", "obj_ions")
        cmd.set("sphere_scale", 1.0, "obj_ions")
    elif mode == "halo":
        # A casca vive num objeto separado porque um mesmo atomo nao pode ter
        # dois raios de esfera simultaneos.
        cmd.show("spheres", "obj_ions")
        cmd.set("sphere_scale", 0.45, "obj_ions")
        cmd.create("obj_ions_halo", "obj_ions")
        cmd.show("spheres", "obj_ions_halo")
        cmd.set("sphere_scale", 2.2, "obj_ions_halo")
        cmd.set("sphere_transparency", 0.72, "obj_ions_halo")
    elif mode == "mesh":
        cmd.show("spheres", "obj_ions")
        cmd.set("sphere_scale", 0.35, "obj_ions")
        cmd.alter("obj_ions", "vdw=%f" % float(radius))
        cmd.rebuild()
        cmd.show("mesh", "obj_ions")
        cmd.set("mesh_width", 0.4, "obj_ions")
    else:
        print("[prot] modos: off, spheres, vdw, halo, mesh, shell")
        return
    _color_context()
    print("[prot] ions: %s" % mode)


def _context(waters=0, show_ions=1, ligands=1, nucleic=1):
    """Ligantes, ions, acido nucleico e agua.

    Agua desligada por padrao: em estrutura cristalografica ela e centenas de
    esferas soltas que poluem a cena sem informar.
    """
    if truthy(ligands) and has("obj_lig"):
        cmd.show("sticks", "obj_lig")
        cmd.set("stick_radius", 0.22, "obj_lig")
    if truthy(show_ions) and has("obj_ions"):
        cmd.show("spheres", "obj_ions")
        cmd.set("sphere_scale", 0.45, "obj_ions")
    if truthy(nucleic) and has("obj_nucl"):
        cmd.show("cartoon", "obj_nucl")
        cmd.set("cartoon_ring_mode", 3, "obj_nucl")
        cmd.set("cartoon_ring_finder", 1, "obj_nucl")
        cmd.set("cartoon_ring_transparency", 0.15, "obj_nucl")
        cmd.set("cartoon_nucleic_acid_mode", 4, "obj_nucl")
    if truthy(waters) and has("obj_wat"):
        cmd.show("spheres", "obj_wat")
        cmd.set("sphere_scale", 0.25, "obj_wat")
        cmd.set("sphere_transparency", 0.5, "obj_wat")


def _finish(msg):
    cmd.rebuild()          # assa a oclusao ambiente na geometria nova
    ref = "obj_prot" if has("obj_prot") else "obj_nucl"
    if has(ref):
        cmd.orient(ref)
        cmd.zoom(ref, 4)
    print("[prot] %s" % msg)


# =============================================================================
# PRESETS
# =============================================================================
def preset1():
    """Cartoon suave por estrutura secundaria.

    Helice azul, folha vermelha, alca branca. Ligantes em sticks, agua
    desligada.

    O preset de leitura geral e o unico que comunica topologia de dominio.
    Contrapartida: cartoon nao recebe oclusao ambiente no PyMOL, entao esta e
    a cena com menos relevo do conjunto.
    """
    if not prepare():
        return
    _reset()
    cmd.show("cartoon", "obj_prot")
    cmd.cartoon("oval", "obj_prot and ss S")
    cmd.cartoon("automatic", "obj_prot and ss H")
    cmd.cartoon("loop", "obj_prot and not (ss S or ss H)")
    color("ss")
    _context()
    _finish("preset_prot1: cartoon por estrutura secundaria")


def preset2():
    """Cartoon com superficie fantasma.

    Mostra a topologia sem perder o contorno molecular. E o preset para sitio
    de ligacao: o ligante fica visivel por dentro da superficie, o que uma
    superficie opaca impediria.
    """
    if not prepare():
        return
    _reset()
    cmd.show("cartoon", "obj_prot")
    cmd.cartoon("oval", "obj_prot and ss S")
    cmd.cartoon("loop", "obj_prot and not (ss S or ss H)")
    cmd.show("surface", "obj_prot")
    cmd.set("transparency", 0.55, "obj_prot")
    color("ss")
    _context()
    _finish("preset_prot2: cartoon com superficie fantasma")


def preset3():
    """Superficie solida por hidrofobicidade.

    Para analisar face de interacao: anfipaticidade, bolso hidrofobico,
    interface de dimero. A superficie recebe oclusao ambiente, entao e a cena
    com mais relevo. Sobrescreve os fatores B; prot_restore_b desfaz.
    """
    if not prepare():
        return
    _reset()
    cmd.set("solvent_radius", 1.4)
    cmd.show("surface", "obj_prot")
    color("hydro")
    _context()
    _finish("preset_prot3: superficie por hidrofobicidade")


def preset4():
    """Spacefill por cadeia.

    Volume ocupado e empacotamento. Em complexo multi-cadeia e a forma mais
    direta de mostrar a arquitetura do conjunto.
    """
    if not prepare():
        return
    _reset()
    cmd.show("spheres", "obj_prot")
    cmd.set("sphere_scale", 1.0, "obj_prot")
    color("chain")
    if has("obj_lig"):
        cmd.show("spheres", "obj_lig")
        cmd.set("sphere_scale", 1.0, "obj_lig")
    _context(ligands=0)
    _finish("preset_prot4: spacefill por cadeia")


def preset5():
    """Putty por fator B.

    A espessura codifica o fator B: regiao flexivel fica grossa e vermelha.
    Valido para estrutura experimental. Em modelo predito a coluna B costuma
    carregar pLDDT, cuja escala significa o oposto — vermelho grosso passaria
    a marcar regiao confiavel, nao flexivel.
    """
    if not prepare():
        return
    _reset()
    cmd.show("cartoon", "obj_prot")
    cmd.cartoon("putty", "obj_prot")
    cmd.set("cartoon_putty_scale_min", 0.6, "obj_prot")
    cmd.set("cartoon_putty_scale_max", 3.5, "obj_prot")
    cmd.set("cartoon_putty_transform", 0, "obj_prot")
    cmd.set("cartoon_putty_radius", 0.35, "obj_prot")
    color("bfactor")
    _context()
    _finish("preset_prot5: putty por fator B")


def preset6():
    """All-atom licorice, cor por carga.

    Para peptideos, onde o cartoon comunica pouco: nao ha topologia global a
    resumir e a informacao esta na cadeia lateral. O esquema de carga expoe
    diretamente a anfipaticidade de um peptideo cationico.

    Em proteina grande esta cena vira uma massa ilegivel.
    """
    if not prepare():
        return
    _reset()
    cmd.show("sticks", "obj_prot")
    cmd.set("stick_radius", 0.20, "obj_prot")
    cmd.set("cartoon_side_chain_helper", 0)
    color("charge")
    _context()
    if not _is_peptide():
        print("[prot] aviso: %d residuos. Acima de %d o all-atom fica "
              "ilegivel; considere preset_prot1 ou preset_prot3."
              % (n_residues("obj_prot"), PEPTIDE_CUTOFF))
    _finish("preset_prot6: all-atom por carga")


def preset7(shell=4.0):
    """Sistema solvatado: proteina, camada de agua e ions proximos.

    O preset para caixa de MD. Descarta agua e ions de bulk, que numa caixa
    tipica sao mais de 90% dos atomos e escondem completamente o soluto.
    """
    if not prepare():
        return
    _reset()
    cmd.show("cartoon", "obj_prot")
    cmd.cartoon("oval", "obj_prot and ss S")
    cmd.cartoon("loop", "obj_prot and not (ss S or ss H)")
    color("ss")
    _context(waters=0, show_ions=0)
    water("shell", shell)
    ions("shell", 6.0)
    _finish("preset_prot7: sistema solvatado (camada de %.1f A)" % float(shell))


def preset8():
    """Caixa completa: proteina em superficie dentro do volume de solvente.

    Para ilustrar o sistema simulado como um todo — dimensao da caixa,
    proporcao soluto/solvente. Nao serve para analisar a proteina: o solvente
    a cobre por construcao.
    """
    if not prepare():
        return
    _reset()
    cmd.show("surface", "obj_prot")
    color("charge")
    _context(waters=0, show_ions=0)
    water("surface", transparency=0.72)
    ions("halo")
    _finish("preset_prot8: caixa completa")


def auto():
    """Escolhe o preset inicial pelo tamanho do sistema."""
    if not prepare():
        return
    if _is_peptide():
        preset6()
    else:
        preset1()


def register():
    for name, fn in (("preset_prot1", preset1), ("preset_prot2", preset2),
                     ("preset_prot3", preset3), ("preset_prot4", preset4),
                     ("preset_prot5", preset5), ("preset_prot6", preset6),
                     ("preset_prot7", preset7), ("preset_prot8", preset8),
                     ("prot_split", split), ("prot_color", color),
                     ("prot_water", water), ("prot_ions", ions),
                     ("prot_restore_b", restore_bfactors),
                     ("prot_prepare", prepare), ("prot_auto", auto)):
        cmd.extend(name, fn)
