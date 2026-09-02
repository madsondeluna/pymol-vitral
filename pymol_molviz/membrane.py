"""
pymol_molviz.membrane

Presets de visualizacao para sistemas de membrana.

Divide o sistema em objetos independentes (obj_lipid, obj_wat, obj_ions,
obj_prot) e aplica combinacoes de representacao de lipideo, ion e solvente.
"""

from pymol import cmd
from pymol_molviz import core
from pymol_molviz.core import has, truthy, n_residues


# =============================================================================
# Nomenclatura
# Centralizada aqui: adaptar a um force field novo e editar um dicionario, nao
# varrer o modulo.
# =============================================================================
LIPID_RESN = (
    "POPC+POPE+POPG+POPS+POPA+POPI+DPPC+DPPE+DPPG+DOPC+DOPE+DOPG+"
    "DLPC+DMPC+CHOL+CHL1+LPS+REMP+RAMP+KDO+LIPA+CDL+CDL2+CARD"
)
INNER_LEAFLET_RESN = "POPG+POPS+CDL+CDL2+CARD"
STEROL_RESN = "CHOL+CHL1"

# Nomes de atomo da cabeca, na convencao CHARMM, por classe de lipideo. Sao o
# ULTIMO recurso: entram apenas nas especies que o criterio posicional nao
# cobriu, e nunca substituem o que ele ja resolveu.
#
# Existem porque duas situacoes escapam da posicao e nao por falha dela. Uma
# cabeca dobrada para dentro nao esta alem do fosfato, e o glicerol central da
# cardiolipina fica ENTRE os dois fosfatos por construcao quimica, portanto
# mais interno que eles. Medido no sistema de teste: P1 liga a C1 e P3 liga a
# C3, entao o glicerol central e C1-C2-C3 com a hidroxila OG12.
#
# Como qualquer regra por nome, isto vale para CHARMM e nao para Berger,
# GROMOS ou Slipids. Nesses o criterio posicional continua sendo o que vale.
HEAD_NAMES = {
    "PG": "C11+C12+C13+OC2+OC3",
    "PI": "C11+C12+C13+C14+C15+C16+O2+O3+O4+O5+O6",
    "PS": "C11+C12+C13+O13A+O13B",
    "CL": "C1+C2+C3+OG12",
}

# resn -> classe em HEAD_NAMES.
HEAD_CLASS = (
    (("CL", "CDL", "CDL2", "TOCL", "TMCL", "CARD"), "CL"),
    (("PI",), "PI"),
    (("PS",), "PS"),
    (("PG",), "PG"),
)

# Abaixo desta fracao de moleculas com cabeca marcada, a especie recorre ao
# dicionario. Meia especie coberta ja indica que a posicao nao resolve ali.
HEAD_FALLBACK_RATIO = 0.5

# Nomes de particula Martini, usados quando o sistema e coarse-grained.
CG_NAMES = {
    "head": "NC3+NH3+CNO+GL0+TAP",
    "phos": "PO4+PO1+PO2+P",
    "glyc": "GL1+GL2+AM1+AM2",
}

OBJECTS = ["obj_lipid", "obj_wat", "obj_ions", "obj_prot"]


def _is_cg():
    """Heuristica de coarse-grained pela razao atomos por residuo lipidico.

    Na Martini um POPC tem cerca de 12 particulas; em all-atom sem hidrogenios
    tem 52. O corte em 25 separa os dois regimes com folga.
    """
    n = n_residues("obj_lipid")
    if n == 0:
        return False
    return (cmd.count_atoms("obj_lipid") / float(n)) < 25


# =============================================================================
# Preparacao
# =============================================================================
def split(keep_source=0):
    """Divide o sistema carregado em objetos independentes.

    Objetos, e nao selecoes: e o que da a cada componente sua propria linha no
    painel, com ponto de enable e botoes A/S/H/L/C.

    Edge case: cmd.create copia todos os estados. Numa trajetoria de milhares
    de frames isso duplica a memoria inteira; carregue apenas o frame de
    interesse antes.
    """
    sources = core.source_objects(OBJECTS)
    if not sources:
        print("[membrane] nada carregado.")
        return

    src = " or ".join(sources)
    # Antes de qualquer selecao por elemento: um PDB sem as colunas 77-78 faz
    # o PyMOL adivinhar o elemento pelo nome, e CA vira calcio.
    core.fix_elements(src)

    cmd.select("_wat", "(%s) and resn %s" % (src, core.WATER_RESN))
    cmd.select("_ions", core.ion_selection(src))
    cmd.select("_prot", "(%s) and polymer.protein" % src)
    cmd.select("_lipid",
               "(%s) and not (_wat or _ions or _prot) and not hydro" % src)

    for obj, sel in (("obj_lipid", "_lipid"), ("obj_wat", "_wat"),
                     ("obj_ions", "_ions"), ("obj_prot", "_prot")):
        cmd.delete(obj)
        if has(sel):
            cmd.create(obj, sel)

    for tmp in ("_wat", "_ions", "_prot", "_lipid"):
        cmd.delete(tmp)

    # O objeto de origem e desabilitado, nao deletado: se algo der errado nas
    # copias, ele continua disponivel para recomecar.
    if not truthy(keep_source):
        for s in sources:
            cmd.disable(s)

    _lipid_parts()
    if has("obj_wat"):
        cmd.select("wat_o", "obj_wat and (elem O or name W+PW+OW)")
        cmd.deselect()

    print("[membrane] objetos: %s | coarse-grained: %s"
          % (", ".join(o for o in OBJECTS if has(o)), _is_cg()))


def _lipid_parts():
    """Camadas quimicas dentro de obj_lipid.

    Definidas por criterio quimico e nao por nome de atomo, porque a
    nomenclatura varia entre CHARMM, Berger, Slipids e Martini enquanto a
    topologia nao:

      cabeca   = nitrogenio quaternario ou amina, mais os carbonos vizinhos
      fosfato  = fosforo, mais os oxigenios ligados
      glicerol = oxigenios de ester restantes, mais os carbonos adjacentes
      cauda    = o complemento

    Em coarse-grained nao ha elemento atribuido de forma confiavel, entao cai
    para os nomes de particula Martini.
    """
    if not has("obj_lipid"):
        return

    if _is_cg():
        cmd.select("lip_head", "obj_lipid and name %s" % CG_NAMES["head"])
        cmd.select("lip_phos", "obj_lipid and name %s" % CG_NAMES["phos"])
        cmd.select("lip_glyc", "obj_lipid and name %s" % CG_NAMES["glyc"])
    else:
        cmd.select("lip_phos",
                   "obj_lipid and (elem P or (elem O within 2.0 of "
                   "(obj_lipid and elem P)))")
        # Cabeca por nitrogenio, que cobre colina e etanolamina, mais o que
        # estiver distal ao plano do fosfato, que cobre o resto.
        cmd.select("lip_head",
                   "obj_lipid and (elem N or (elem C within 3.0 of "
                   "(obj_lipid and elem N)))")
        if _mark_distal_head():
            cmd.select("lip_head", "lip_head or lip_head_geo")
            cmd.delete("lip_head_geo")
        for resn, n in _head_by_name():
            print("[membrane] %s: cabeca pelo dicionario CHARMM (%d moleculas)"
                  % (resn, n))
        cmd.select("lip_glyc",
                   "obj_lipid and not (lip_head or lip_phos) and (elem O or "
                   "(elem C within 1.8 of (obj_lipid and elem O and not "
                   "lip_phos)))")
    cmd.select("lip_tail",
               "obj_lipid and not (lip_head or lip_phos or lip_glyc)")
    cmd.deselect()


def prepare():
    core.material()
    if not has("obj_lipid"):
        split()
    return has("obj_lipid")


def _reset():
    # As selecoes dos presets 7 a 9 entram aqui: clear_reps so mexe em objeto,
    # e uma selecao esquecida reaparece no painel lateral do preset seguinte.
    for obj in ("map_tail", "surf_tail", "map_wat", "surf_wat",
                "obj_ions_halo", "lip_slab", "lip_ring", "lip_up", "lip_dn"):
        cmd.delete(obj)
    core.clear_reps(OBJECTS)


# =============================================================================
# Cor
# =============================================================================
def _col_moiety():
    cmd.color("mv_tail_a", "obj_lipid")
    cmd.color("mv_glyc", "lip_glyc")
    cmd.color("mv_phos", "lip_phos")
    cmd.color("mv_head", "lip_head")


def _mark_distal_head(nome="lip_head_geo"):
    """Marca os atomos que ficam alem do fosfato DO PROPRIO lipideo.

    A cabeca por nitrogenio so alcanca colina e etanolamina. Fosfatidilglicerol,
    fosfatidilinositol, fosfatidilserina e cardiolipina nao tem nitrogenio
    nenhum, e num sistema misto isso deixa a maioria dos lipideos sem cabeca:
    ela some da figura e o esquema 'moiety' passa a mostrar tres camadas em vez
    de quatro.

    O que define a cabeca polar nao e a quimica dela, que varia entre especies,
    e sim a POSICAO: e a parte voltada para o solvente, alem do fosfato.

    A comparacao e por lipideo, e nao contra o z medio do folheto. Medido: com
    a media do folheto, DPPG ficou com 0,2 atomo de cabeca por molecula, porque
    as moleculas mais afundadas que a media perdem a cabeca inteira. Cada
    lipideo tem o seu proprio fosfato como referencia, e nenhum depende de onde
    os vizinhos estao.

    Assume a normal da membrana em z, a mesma premissa de memb_color leaflet e
    do preset_memb9. Numa vesicula o criterio nao vale.
    """
    cmd.delete(nome)
    if not has("lip_phos"):
        return False

    zs = []
    cmd.iterate_state(1, "lip_phos and elem P", "zs.append(z)", space={"zs": zs})
    if not zs:
        return False
    meio = sum(zs) / float(len(zs))

    # z do fosforo mais externo de cada lipideo. Cardiolipina tem dois, e o
    # externo e o que define ate onde vai a cauda daquele lado.
    ref = {}
    cmd.iterate_state(1, "lip_phos and elem P",
                      "ref[(model, segi, chain, resi)] = "
                      "max(ref.get((model, segi, chain, resi), 0.0), abs(z - meio))",
                      space={"ref": ref, "meio": meio, "max": max, "abs": abs})
    if not ref:
        return False

    fora = []
    cmd.iterate_state(1, "obj_lipid and not lip_phos",
                      "fora.append(index) if abs(z - meio) > "
                      "ref.get((model, segi, chain, resi), 1e9) else None",
                      space={"fora": fora, "ref": ref, "meio": meio, "abs": abs})
    if not fora:
        return False
    cmd.select_list(nome, "obj_lipid", fora, mode="index")
    return True


def _head_class(resn):
    r = resn.strip().upper()
    for chaves, classe in HEAD_CLASS:
        for k in chaves:
            if r == k or r.endswith(k):
                return classe
    return None


def _head_by_name():
    """Completa a cabeca por nome, nas especies que a posicao nao cobriu.

    Mede por especie: se menos da metade das moleculas de um resn ficou com
    cabeca, aquela especie inteira recorre ao dicionario. A medida e por
    especie e nao por molecula porque a causa tambem e: ou a quimica daquele
    lipideo escapa do criterio posicional, ou nao escapa.

    Devolve a lista de (resn, moleculas) que precisaram do dicionario.
    """
    por_especie = {}
    cmd.iterate("obj_lipid", "por_especie.setdefault(resn, set()).add((chain, resi))",
                space={"por_especie": por_especie})
    com_cabeca = {}
    cmd.iterate("lip_head", "com_cabeca.setdefault(resn, set()).add((chain, resi))",
                space={"com_cabeca": com_cabeca})

    usados = []
    for resn, moleculas in por_especie.items():
        classe = _head_class(resn)
        if classe is None or not moleculas:
            continue
        cobertas = len(com_cabeca.get(resn, ()))
        if cobertas / float(len(moleculas)) >= HEAD_FALLBACK_RATIO:
            continue
        alvo = ("obj_lipid and resn %s and name %s and not lip_phos"
                % (resn, HEAD_NAMES[classe]))
        if cmd.count_atoms(alvo):
            cmd.select("lip_head", "lip_head or (%s)" % alvo)
            usados.append((resn, len(moleculas)))
    return usados


def _phosphate_midplane():
    """z medio dos fosfatos, que e o plano que separa os folhetos.

    Devolve None quando nao ha fosfato: em Martini sem particula PO4 mapeada,
    ou num sistema que nao e bicamada.
    """
    if not has("lip_phos"):
        return None
    zs = []
    cmd.iterate_state(1, "lip_phos", "zs.append(z)", space={"zs": zs})
    return sum(zs) / float(len(zs)) if zs else None


def _col_leaflet():
    """Folheto superior e inferior.

    Assume a normal da membrana em z e usa o centro de massa dos fosfatos como
    plano medio. Em vesicula ou membrana com curvatura acentuada o criterio
    nao vale.
    """
    ref = "lip_phos" if has("lip_phos") else "lip_head"
    if not has(ref):
        _col_moiety()
        return
    zc = cmd.centerofmass(ref)[2]
    cmd.color("mv_tail_a", "obj_lipid and z > %f" % zc)
    cmd.color("mv_tail_in", "obj_lipid and z < %f" % zc)
    cmd.color("mv_head", "lip_head")
    cmd.color("mv_phos", "lip_phos")


def _col_type():
    """Uma cor por especie lipidica. Para membranas mistas e pan-lipidomas."""
    if not has("obj_lipid"):
        return
    resns = sorted(set(a.resn for a in cmd.get_model("obj_lipid").atom))
    for i, resn in enumerate(resns):
        cmd.color(core.TYPE_CYCLE[i % len(core.TYPE_CYCLE)],
                  "obj_lipid and resn %s" % resn)
    print("[membrane] especies: %s" % ", ".join(resns))


def _col_depth():
    """Gradiente continuo na normal. Para inspecionar interdigitacao."""
    cmd.spectrum("z", "blue_white_red", "obj_lipid")


COLORS = {"moiety": _col_moiety, "leaflet": _col_leaflet,
          "type": _col_type, "depth": _col_depth}


def color(scheme="moiety"):
    """Esquema de cor: moiety, leaflet, type, depth."""
    if scheme not in COLORS:
        print("[membrane] esquemas: %s" % ", ".join(sorted(COLORS)))
        return
    COLORS[scheme]()
    _color_context()
    print("[membrane] cor: %s" % scheme)


def _color_context():
    if has("obj_ions"):
        cmd.color("mv_na", "obj_ions and resn NA+SOD+NA+")
        cmd.color("mv_cl", "obj_ions and resn CL+CLA+CL-")
        cmd.color("orange", "obj_ions and resn K+POT")
        cmd.color("forest", "obj_ions and resn MG")
        cmd.color("grey60", "obj_ions and resn CA")


# =============================================================================
# Agua e ions
# =============================================================================
def water(mode="surface", transparency=0.62, radius=3.3):
    """Agua: off, surface, spheres, field.

    'surface' infla o raio dos oxigenios e desenha a superficie molecular. E
    mais previsivel que o mapa gaussiano, que exige calibrar o nivel de
    isosuperficie.
    """
    cmd.delete("surf_wat")
    cmd.delete("map_wat")

    # A checagem vem antes do hide: sem agua na estrutura o objeto nao existe,
    # e hide sobre nome inexistente levanta 'Invalid selection name'.
    if not has("obj_wat"):
        return
    for rep in ("surface", "spheres", "sticks", "lines", "nonbonded"):
        cmd.hide(rep, "obj_wat")
    if mode == "off":
        return

    if mode == "surface":
        cmd.alter("wat_o", "vdw=%f" % float(radius))
        cmd.rebuild()      # sem isso o novo raio nao propaga para a geometria
        cmd.set("solvent_radius", 1.8)
        cmd.show("surface", "wat_o")
        cmd.color("mv_water", "obj_wat")
        cmd.set("transparency", float(transparency), "obj_wat")
    elif mode == "spheres":
        cmd.show("spheres", "wat_o")
        cmd.set("sphere_scale", 0.35, "obj_wat")
        cmd.set("sphere_transparency", 0.75, "obj_wat")
        cmd.color("mv_water", "obj_wat")
    elif mode == "field":
        if not core.gaussian_isosurface("surf_wat", "map_wat", "wat_o",
                                        grid=1.5, resolution=4.0,
                                        label="membrane"):
            return
        cmd.color("mv_water", "surf_wat")
        cmd.set("transparency", float(transparency), "surf_wat")
    else:
        print("[membrane] modos: off, surface, spheres, field")
        return
    print("[membrane] agua: %s" % mode)


def _ions_spheres(scale=0.5):
    if not has("obj_ions"):
        return
    cmd.show("spheres", "obj_ions")
    cmd.set("sphere_scale", float(scale), "obj_ions")
    _color_context()


def _ions_vdw():
    if not has("obj_ions"):
        return
    cmd.show("spheres", "obj_ions")
    cmd.set("sphere_scale", 1.0, "obj_ions")
    _color_context()


def _ions_halo(cor=0.45, shell=2.2, transparency=0.72):
    """Nucleo opaco com casca translucida, sugerindo a esfera de solvatacao.

    A casca vive num objeto separado porque um mesmo atomo nao pode ter dois
    raios de esfera simultaneos.
    """
    if not has("obj_ions"):
        return
    _ions_spheres(cor)
    cmd.delete("obj_ions_halo")
    cmd.create("obj_ions_halo", "obj_ions")
    cmd.show("spheres", "obj_ions_halo")
    cmd.set("sphere_scale", float(shell), "obj_ions_halo")
    cmd.set("sphere_transparency", float(transparency), "obj_ions_halo")


def _ions_mesh(radius=3.0):
    """Malha em vez de superficie solida: marca a posicao sem ocultar o que
    esta atras, util quando o ion esta dentro da bicamada."""
    if not has("obj_ions"):
        return
    cmd.show("spheres", "obj_ions")
    cmd.set("sphere_scale", 0.35, "obj_ions")
    cmd.alter("obj_ions", "vdw=%f" % float(radius))
    cmd.rebuild()
    cmd.show("mesh", "obj_ions")
    cmd.set("mesh_width", 0.4, "obj_ions")
    _color_context()


def _ions_dots(scale=0.4):
    if not has("obj_ions"):
        return
    cmd.show("nonbonded", "obj_ions")
    cmd.show("spheres", "obj_ions")
    cmd.set("sphere_scale", float(scale), "obj_ions")
    cmd.set("sphere_transparency", 0.3, "obj_ions")
    _color_context()


def protein():
    """Peptideo ou proteina embebida, se houver."""
    if not has("obj_prot"):
        return
    cmd.show("cartoon", "obj_prot")
    cmd.cartoon("oval", "obj_prot and ss S")
    cmd.cartoon("loop", "obj_prot and not (ss S or ss H)")
    cmd.color("mv_loop", "obj_prot")
    cmd.color("mv_helix", "obj_prot and ss H")
    cmd.color("mv_sheet", "obj_prot and ss S")
    if not has("obj_prot and (ss H or ss S)"):
        print("[membrane] aviso: sem estrutura secundaria atribuida. Em "
              "all-atom rode 'dss'; o PyMOL nao a infere de particulas CG.")


def _finish(msg, paper=0):
    """Fecha o preset. 'paper' liga o modo de periodico na mesma linha.

    Sem 'paper' o preset so define representacao e cor, e a iluminacao fica
    como estava: e o modo de explorar na tela, e mv_paper pode vir depois. Com
    'paper', a largura de coluna em milimetros, a cena ja sai pronta para
    figura. Os dois caminhos existem porque a mesma cena serve as duas coisas.
    """
    protein()
    cmd.rebuild()          # assa a oclusao ambiente na geometria nova
    cmd.orient("obj_lipid")
    cmd.zoom("obj_lipid", 3)
    print("[membrane] %s" % msg)
    if core.truthy_width(paper):
        core.paper(float(paper))


# =============================================================================
# PRESETS
# =============================================================================
def preset1(paper=0):
    """Esferas estratificadas.

    Lipideo: esferas com folga (0.55), cor por camada quimica
    Ions:    esferas opacas medias
    Agua:    superficie translucida

    O preset de leitura geral. A folga entre esferas preserva a distincao
    entre cabeca, fosfato, glicerol e cauda, que o spacefill cheio apaga.
    """
    if not prepare():
        return
    _reset()
    cmd.show("spheres", "obj_lipid")
    cmd.set("sphere_scale", 0.55, "obj_lipid")
    cmd.set("sphere_scale", 0.66, "lip_head")
    color("moiety")
    _ions_spheres(0.5)
    water("surface", 0.62)
    _finish("preset_memb1: esferas estratificadas", paper)


def preset2(paper=0):
    """Spacefill solido.

    Lipideo: raio de van der Waals real, cor por folheto
    Ions:    raio real, coerentes com o lipideo
    Agua:    superficie muito translucida

    Mostra volume ocupado e empacotamento. A organizacao interna fica
    invisivel por construcao: o que se ve e a barreira.
    """
    if not prepare():
        return
    _reset()
    cmd.show("spheres", "obj_lipid")
    cmd.set("sphere_scale", 1.0, "obj_lipid")
    color("leaflet")
    _ions_vdw()
    water("surface", 0.78)
    _finish("preset_memb2: spacefill solido", paper)


def preset3(paper=0):
    """Licorice com ions destacados.

    Lipideo: sticks de raio alto, cabecas em esfera
    Ions:    nucleo opaco com casca de solvatacao
    Agua:    esferas translucidas

    Para figuras sobre interacao ion-cabeca polar. O licorice deixa ver a
    conformacao das caudas, que o spacefill esconde.
    """
    if not prepare():
        return
    _reset()
    cmd.show("sticks", "obj_lipid")
    cmd.set("stick_radius", 0.30, "obj_lipid")
    cmd.show("spheres", "lip_head")
    cmd.set("sphere_scale", 0.45, "obj_lipid")
    color("moiety")
    _ions_halo()
    water("spheres")
    _finish("preset_memb3: licorice com ions destacados", paper)


def preset4(paper=0):
    """Bicamada fantasma.

    Lipideo: superficie translucida com licorice fino por dentro
    Ions:    esferas com malha de raio inflado
    Agua:    desligada

    O preset para peptideo inserido: preserva o contorno da membrana sem
    ocultar o que esta dentro. A agua fica desligada de proposito, pois a
    superficie do solvente esconderia o objeto de interesse.
    """
    if not prepare():
        return
    _reset()
    cmd.show("sticks", "obj_lipid")
    cmd.set("stick_radius", 0.16, "obj_lipid")
    cmd.show("surface", "obj_lipid")
    cmd.set("transparency", 0.58, "obj_lipid")
    color("moiety")
    _ions_mesh()
    _finish("preset_memb4: bicamada fantasma", paper)


def preset5(paper=0):
    """Ilustracao: nucleo hidrofobico continuo.

    Lipideo: caudas como isosuperficie gaussiana, cabecas em esfera
    Ions:    esferas opacas grandes
    Agua:    campo continuo

    Reduz milhares de atomos de cauda a uma unica superficie lisa. E o preset
    mais leve para sistemas grandes e o mais proximo da estetica de ilustracao
    cientifica.
    """
    if not prepare():
        return
    _reset()
    if core.gaussian_isosurface("surf_tail", "map_tail", "lip_tail",
                                grid=1.2, resolution=3.0, label="membrane"):
        cmd.color("mv_tail_a", "surf_tail")
    else:
        # Sem a isosuperficie o preset perderia as caudas por inteiro. Sticks
        # finos mantem a cena legivel e dizem no log que o caminho foi outro.
        cmd.show("sticks", "lip_tail")
        cmd.set("stick_radius", 0.14, "obj_lipid")
        cmd.color("mv_tail_a", "lip_tail")
        print("[membrane] preset_memb5: caudas em sticks, sem isosuperficie.")

    cmd.show("spheres", "lip_head")
    cmd.show("spheres", "lip_phos")
    cmd.set("sphere_scale", 0.75, "obj_lipid")
    cmd.color("mv_head", "lip_head")
    cmd.color("mv_phos", "lip_phos")

    _ions_spheres(0.85)
    water("field", 0.62)
    _finish("preset_memb5: nucleo continuo", paper)


def preset6(paper=0):
    """Navegacao rapida.

    Lipideo: linhas, cor por especie
    Ions:    pontos
    Agua:    desligada
    Oclusao ambiente desligada

    Nao e um preset de figura. Existe porque o custo do ray tracing e da AO
    torna a rotacao inviavel em sistema grande, e enquadrar a cena antes de
    aplicar um preset caro economiza minutos.
    """
    if not prepare():
        return
    _reset()
    cmd.set("ambient_occlusion_mode", 0)
    cmd.set("sphere_quality", 1)
    cmd.show("lines", "obj_lipid")
    cmd.set("line_width", 1.2, "obj_lipid")
    color("type")
    _ions_dots()
    _finish("preset_memb6: navegacao rapida", paper)


def _slab_selection(name, eixo=1, fracao=0.34):
    """Fatia central do sistema no eixo dado (0=x, 1=y, 2=z).

    O corte e por coordenada e nao pelo plano de recorte da camera, porque
    'clip' depende de para onde a cena esta virada: girar a figura depois
    mudaria o que aparece. Uma selecao fixa sobrevive a rotacao.
    """
    (x0, y0, z0), (x1, y1, z1) = cmd.get_extent("obj_lipid")
    lo, hi = ((x0, x1), (y0, y1), (z0, z1))[eixo]
    meio = (lo + hi) / 2.0
    meia = (hi - lo) * float(fracao) / 2.0
    letra = "xyz"[eixo]
    cmd.select(name, "obj_lipid and (%s > %f) and (%s < %f)"
               % (letra, meio - meia, letra, meio + meia))
    return cmd.count_atoms(name)


def preset7(eixo=1, paper=0):
    """Corte transversal.

    Lipideo: fatia central em spacefill, cor por camada quimica
    Ions:    esferas, so os da fatia
    Agua:    desligada

    A figura de corte: o interior da bicamada fica exposto, com cabeca,
    fosfato, glicerol e cauda visiveis na face cortada. Spacefill e nao
    superficie porque a superficie de uma selecao parcial fecha sobre si mesma
    e devolve uma casca, nao um corte.

    O corte e uma selecao por coordenada, entao girar a cena depois nao muda o
    que esta exposto.
    """
    if not prepare():
        return
    _reset()
    cmd.delete("lip_slab")
    if not _slab_selection("lip_slab", int(eixo)):
        print("[membrane] a fatia saiu vazia: verifique obj_lipid.")
        return
    cmd.show("spheres", "lip_slab")
    cmd.set("sphere_scale", 1.0, "obj_lipid")
    color("moiety")
    if has("obj_ions"):
        cmd.show("spheres", "obj_ions and (obj_ions within 8 of lip_slab)")
        cmd.set("sphere_scale", 0.5, "obj_ions")
        _color_context()
    cmd.deselect()
    _finish("preset_memb7: corte transversal no eixo %s" % "xyz"[int(eixo)],
            paper)

    # A camera olha ao longo do eixo do corte, senao a face cortada fica de
    # perfil e o corte nao aparece: a cena sai identica a bicamada inteira.
    # 'reset' devolve a vista canonica (x direita, y cima, z para o
    # observador), e a partir dela o giro que traz o eixo do corte para a
    # linha de visao e fixo.
    cmd.reset()
    if int(eixo) == 0:
        cmd.turn("y", 90)
    elif int(eixo) == 1:
        cmd.turn("x", 90)
    cmd.zoom("lip_slab", 2)


def preset8(raio=5.0, paper=0):
    """Lipideos anelares.

    Lipideo: os que tocam a proteina em licorice colorido, o resto fantasma
    Ions:    esferas pequenas
    Agua:    desligada
    Proteina: superficie opaca

    Responde a quais lipideos estao em contato com a proteina, que e a
    pergunta de anular shell. Sem proteina na sessao o preset nao tem o que
    medir e avisa.
    """
    if not prepare():
        return
    if not has("obj_prot"):
        print("[membrane] preset_memb8 precisa de proteina na sessao. "
              "Use preset_memb4 para bicamada sem proteina.")
        return
    _reset()
    cmd.delete("lip_ring")
    cmd.select("lip_ring",
               "byres (obj_lipid within %.1f of obj_prot)" % float(raio))
    n = cmd.count_atoms("lip_ring")

    cmd.show("sticks", "obj_lipid")
    cmd.set("stick_radius", 0.10, "obj_lipid")
    cmd.color("mv_glyc", "obj_lipid")
    cmd.set("stick_transparency", 0.72, "obj_lipid")

    if n:
        cmd.set("stick_transparency", 0.0, "lip_ring")
        cmd.set("stick_radius", 0.24, "lip_ring")
        cmd.color("mv_tail_a", "lip_ring")
        cmd.color("mv_head", "lip_ring and lip_head")
        cmd.color("mv_phos", "lip_ring and lip_phos")
    else:
        print("[membrane] nenhum lipideo a %.1f A da proteina." % float(raio))

    _ions_spheres(0.4)
    cmd.deselect()
    _finish("preset_memb8: lipideos anelares a %.1f A (%d atomos)"
            % (float(raio), n), paper)


def preset9(paper=0):
    """Folhetos separados.

    Lipideo: um folheto por superficie translucida, cores distintas
    Ions:    esferas medias
    Agua:    desligada
    Fosfatos em esfera, marcando os dois planos

    Para assimetria e espessura: as duas superficies deixam medir a separacao
    entre os planos de fosfato a olho, e a diferenca de composicao entre os
    folhetos aparece como diferenca de volume.
    """
    if not prepare():
        return
    _reset()
    zmed = _phosphate_midplane()
    if zmed is None:
        print("[membrane] sem fosfatos: nao da para separar os folhetos.")
        return
    for nome, sinal, cor in (("lip_up", ">", "mv_tail_a"),
                             ("lip_dn", "<", "mv_tail_b")):
        cmd.delete(nome)
        cmd.select(nome, "obj_lipid and (z %s %f)" % (sinal, zmed))
        if cmd.count_atoms(nome):
            cmd.show("surface", nome)
            cmd.color(cor, nome)
    cmd.set("transparency", 0.45, "obj_lipid")
    cmd.show("spheres", "lip_phos")
    cmd.set("sphere_scale", 0.55, "obj_lipid")
    cmd.color("mv_phos", "lip_phos")
    _ions_spheres(0.5)
    cmd.deselect()
    _finish("preset_memb9: folhetos separados (plano medio z=%.1f)" % zmed,
            paper)


def preset10(paper=0):
    """Duas cores, para reducao e impressao.

    Lipideo: cabecas claras em esfera, caudas escuras em isosuperficie
    Ions:    desligados
    Agua:    desligada

    O preset desenhado para sobreviver a coluna de 85 mm e ao teste em escala
    de cinza: duas cores so, separadas por claridade e nao por matiz, e
    nenhum elemento secundario competindo por atencao. Tudo o que nao e a
    bicamada sai da cena.
    """
    if not prepare():
        return
    _reset()
    water("off")
    if has("obj_ions"):
        for rep in core.ALL_REPS:
            cmd.hide(rep, "obj_ions")

    if core.gaussian_isosurface("surf_tail", "map_tail", "lip_tail",
                                grid=1.2, resolution=3.0, label="membrane"):
        cmd.color("mv_tail_in", "surf_tail")
    else:
        cmd.show("sticks", "lip_tail")
        cmd.set("stick_radius", 0.16, "obj_lipid")
        cmd.color("mv_tail_in", "lip_tail")

    cmd.show("spheres", "lip_head")
    cmd.show("spheres", "lip_phos")
    cmd.set("sphere_scale", 0.8, "obj_lipid")
    cmd.color("mv_glyc", "lip_head")
    cmd.color("mv_glyc", "lip_phos")
    _finish("preset_memb10: duas cores para impressao", paper)


def register():
    for name, fn in (("preset_memb1", preset1), ("preset_memb2", preset2),
                     ("preset_memb3", preset3), ("preset_memb4", preset4),
                     ("preset_memb5", preset5), ("preset_memb6", preset6),
                     ("preset_memb7", preset7), ("preset_memb8", preset8),
                     ("preset_memb9", preset9), ("preset_memb10", preset10),
                     ("memb_split", split), ("memb_color", color),
                     ("memb_water", water), ("memb_protein", protein),
                     ("memb_prepare", prepare)):
        cmd.extend(name, fn)
