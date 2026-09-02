"""
style_madson.py

Versao Python do estilo de visualizacao molecular (equivalente funcional do
style_madson.pml, com parametrizacao).

Estilo: cartoon suave (helice azul / folha vermelha / alca branca), material
plastico opaco, sombreamento por oclusao ambiente, lipideos em licorice
CG-friendly, agua como campo continuo translucido.

Uso dentro do PyMOL:

    run style_madson.py
    mad_style                              # padroes
    mad_style water=spheres                # agua leve, para sistemas grandes
    mad_style shadows=1, quality=draft     # sombras projetadas, previa rapida

Uso a partir do shell:

    pymol estrutura.pdb style_madson.py -d "mad_style"

Uso como biblioteca (pymol em modo headless / scripts de batch):

    import pymol
    pymol.finish_launching(["pymol", "-qc"])
    from pymol import cmd
    from style_madson import apply_style
    cmd.load("estrutura.pdb")
    apply_style(water="field")

O modulo nao renderiza nem salva nada. Ver mad_render() no final.
"""

from pymol import cmd


# =============================================================================
# Paleta
# Cores definidas por RGB explicito para reprodutibilidade entre maquinas: as
# cores nomeadas do PyMOL variam de percepcao conforme o gamma do display.
# =============================================================================
PALETTE = {
    "mad_helix":   [0.11, 0.33, 0.65],   # azul profundo, helices
    "mad_sheet":   [0.78, 0.19, 0.17],   # vermelho tijolo, folhas
    "mad_loop":    [0.94, 0.94, 0.92],   # branco quente, alcas/coil
    "mad_water":   [0.62, 0.76, 0.88],   # azul claro, campo de agua
    "mad_head":    [0.30, 0.75, 0.25],   # verde, cabecas polares
    "mad_phos":    [0.90, 0.55, 0.15],   # laranja, fosfato
    "mad_glyc":    [0.85, 0.85, 0.85],   # cinza claro, glicerol
    "mad_tail_a":  [0.93, 0.60, 0.20],   # laranja, cauda A
    "mad_tail_b":  [0.86, 0.40, 0.75],   # magenta, cauda B
    "mad_tail_in": [0.82, 0.15, 0.12],   # vermelho, folheto interno
    "mad_lig":     [0.55, 0.45, 0.80],   # lilas, ligantes
    "mad_dna_bb":  [0.90, 0.90, 0.93],   # branco perolado, backbone DNA
    "mad_dna_p":   [0.95, 0.70, 0.72],   # rosa pastel, fosfatos DNA
}


# =============================================================================
# Nomenclatura de residuos e particulas
# Centralizada aqui para que a adaptacao a um force field novo seja uma unica
# edicao, e nao uma varredura pelo corpo do script.
# =============================================================================
RESN = {
    "water": "HOH+WAT+SOL+TIP3+TIP4+T3P+W+PW+SPC",
    "ions":  "NA+CL+K+MG+CA+ZN+FE+MN+CU+SOD+CLA+POT+ION+NA++CL-",
    "memb": (
        "POPC+POPE+POPG+POPS+POPA+POPI+DPPC+DPPE+DPPG+DOPC+DOPE+DOPG+"
        "DLPC+DMPC+CHOL+CHL1+LPS+REMP+RAMP+KDO+LIPA+CDL+CDL2+CARD"
    ),
    # Lipideos tipicamente do folheto interno / citoplasmatico, que recebem o
    # vermelho da referencia visual.
    "memb_inner": "POPG+POPS+CDL+CDL2+CARD",
    "sterol": "CHOL+CHL1",
}

# Nomes de particula Martini. Em topologia all-atom estas selecoes ficam vazias
# e o colorido passa a ser governado apenas pelo fallback por residuo.
NAMES = {
    "head": "NC3+NH3+CNO+PO4+GL0+TAP+GM1+GM2+GM3",
    "phos": "PO4+PO1+PO2+P+P1+P2+OP1+OP2",
    "glyc": "GL1+GL2+AM1+AM2+C1+C2+C3+GLY",
    "tail": ("C1A+C2A+C3A+C4A+C5A+D1A+D2A+D3A+D4A+"
             "C1B+C2B+C3B+C4B+C5B+D1B+D2B+D3B+D4B"),
}

ION_COLORS = {
    "purple": "NA+SOD+NA+",
    "green":  "CL+CLA+CL-",
    "orange": "K+POT",
    "forest": "MG",
    "grey60": "CA",
    "slate":  "ZN",
}


# =============================================================================
# Presets de qualidade
# 'draft' existe porque o custo do ray tracing cresce com o quadrado da
# amostragem: iterar o enquadramento em 'publication' desperdica tempo.
# =============================================================================
QUALITY = {
    "draft":       {"sphere_quality": 1, "stick_quality": 8,  "surface_quality": 0,
                    "cartoon_sampling": 7,  "ao": 0},
    "screen":      {"sphere_quality": 2, "stick_quality": 14, "surface_quality": 1,
                    "cartoon_sampling": 12, "ao": 1},
    "publication": {"sphere_quality": 3, "stick_quality": 20, "surface_quality": 1,
                    "cartoon_sampling": 16, "ao": 1},
}


# -----------------------------------------------------------------------------
# Utilitarios
# -----------------------------------------------------------------------------
def _truthy(value):
    # Argumentos vindos da linha de comando do PyMOL chegam sempre como string.
    if isinstance(value, str):
        return value.strip().lower() in ("1", "on", "yes", "true", "t")
    return bool(value)


def _has(selection):
    # Guarda contra selecoes vazias: evita mapas gaussianos de zero atomos e
    # avisos de 'invalid selection' que poluem o log.
    try:
        return cmd.count_atoms(selection) > 0
    except Exception:
        return False


def _define_colors():
    for name, rgb in PALETTE.items():
        cmd.set_color(name, rgb)


# -----------------------------------------------------------------------------
# 1. Material e iluminacao
# -----------------------------------------------------------------------------
def set_material(shadows=False, ao=True, fog=False):
    """Material plastico opaco com sombreamento por oclusao ambiente.

    specular baixo + shininess intermediario produz brilho largo e difuso,
    tipico de polimero fosco. shininess alto (> 60) gera highlight pontual,
    que le como vidro ou metal.
    """
    cmd.set("specular", 0.28)
    cmd.set("shininess", 22)
    cmd.set("spec_reflect", 0.12)
    cmd.set("spec_direct", 0.05)
    cmd.set("spec_count", 1)
    cmd.set("reflect", 0.42)      # preenche as regioes nao iluminadas
    cmd.set("direct", 0.38)
    cmd.set("ambient", 0.14)

    # Varias luzes fracas em vez de uma forte: elimina o contraste duro.
    cmd.set("light_count", 8)
    cmd.set("light",  [-0.35, -0.35, -0.90])
    cmd.set("light2", [0.45, -0.20, -0.70])
    cmd.set("light3", [-0.20, 0.50, -0.60])
    cmd.set("light4", [0.30, 0.35, -0.85])

    # Oclusao ambiente atua sobre esferas e superficies; o cartoon do PyMOL nao
    # a recebe. O volume no cartoon vem do par reflect/direct acima.
    cmd.set("ambient_occlusion_mode", 1 if ao else 0)
    cmd.set("ambient_occlusion_scale", 18)
    cmd.set("ambient_occlusion_smooth", 12)

    cmd.set("ray_shadow", 1 if shadows else 0)
    cmd.set("ray_trace_mode", 0)
    cmd.set("ray_interior_color", "grey20")
    cmd.set("ray_interior_reflect", 0.3)

    # Perspectiva leve: ortografico achata a cena; fov > 30 distorce as bordas.
    cmd.set("orthoscopic", 0)
    cmd.set("field_of_view", 20)

    cmd.set("depth_cue", 1 if fog else 0)
    cmd.set("ray_trace_fog", 1 if fog else 0)

    cmd.set("transparency_mode", 2)   # blending por profundidade; evita
                                      # artefato de ordenacao agua/membrana
    cmd.set("two_sided_lighting", 1)
    cmd.set("line_smooth", 1)


def set_quality(preset="publication"):
    """Amostragem das primitivas. E o que remove as facetas poligonais."""
    cfg = QUALITY.get(preset, QUALITY["publication"])
    cmd.set("sphere_quality", cfg["sphere_quality"])
    cmd.set("stick_quality", cfg["stick_quality"])
    cmd.set("surface_quality", cfg["surface_quality"])
    cmd.set("cartoon_sampling", cfg["cartoon_sampling"])
    cmd.set("ribbon_sampling", cfg["cartoon_sampling"])
    cmd.set("ambient_occlusion_mode", cfg["ao"])
    return cfg


# -----------------------------------------------------------------------------
# 2. Separacao dos componentes
# -----------------------------------------------------------------------------
def make_selections():
    """Cria as selecoes nomeadas e retorna a contagem de atomos de cada uma.

    Usa selecoes e nao objetos: preserva os estados da trajetoria e nao duplica
    coordenadas. Ver split_objects() para o caminho alternativo.

    Os seletores automaticos 'organic'/'inorganic' falham em topologias
    coarse-grained, onde tudo costuma vir como HETATM sem elemento atribuido;
    dai as listas explicitas por residuo.
    """
    cmd.select("prot", "polymer.protein")
    cmd.select("nucl", "polymer.nucleic")
    cmd.select("wat",  "resn %s" % RESN["water"])
    cmd.select("ions", "resn %s" % RESN["ions"])
    cmd.select("memb", "resn %s" % RESN["memb"])
    cmd.select("lig",  "not (prot or nucl or wat or ions or memb) and not hydro")
    cmd.select("hidro", "hydro")
    cmd.deselect()

    return {name: cmd.count_atoms(name)
            for name in ("prot", "nucl", "wat", "ions", "memb", "lig")}


def split_objects():
    """Converte as selecoes em objetos independentes.

    Facilita ligar/desligar componentes pelo painel e aplicar settings por
    objeto. Edge case: cmd.create copia todos os estados por padrao, o que
    duplica a memoria de uma trajetoria inteira. Em MD longa, prefira manter
    as selecoes.
    """
    for name in ("prot", "nucl", "memb", "ions", "wat", "lig"):
        if _has(name):
            cmd.create("obj_%s" % name, name)


# -----------------------------------------------------------------------------
# 3. Proteina
# -----------------------------------------------------------------------------
def style_protein(sel="prot"):
    """Cartoon sem pontas agudas.

    'oval' nas fitas beta substitui a seta por uma fita eliptica de extremidade
    arredondada. Contrapartida: perde-se a indicacao de direcionalidade N->C;
    se ela for necessaria, trocar por cmd.cartoon('automatic', ...).
    """
    if not _has(sel):
        return

    cmd.show("cartoon", sel)
    cmd.cartoon("oval", "%s and ss S" % sel)
    cmd.cartoon("automatic", "%s and ss H" % sel)
    cmd.cartoon("loop", "%s and not (ss S or ss H)" % sel)

    cmd.set("cartoon_oval_width", 0.85)
    cmd.set("cartoon_oval_length", 1.30)
    cmd.set("cartoon_oval_quality", 16)
    cmd.set("cartoon_loop_radius", 0.32)
    cmd.set("cartoon_loop_quality", 16)
    cmd.set("cartoon_tube_radius", 0.45)
    cmd.set("cartoon_tube_quality", 16)

    cmd.set("cartoon_flat_sheets", 0)     # mantem a torcao real da fita
    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_round_helices", 1)
    cmd.set("cartoon_fancy_helices", 0)   # 1 adiciona aresta e quebra o smooth
    cmd.set("cartoon_highlight_color", -1)
    cmd.set("cartoon_discrete_colors", 0)
    cmd.set("cartoon_side_chain_helper", 1)
    cmd.set("cartoon_transparency", 0.0)

    cmd.color("mad_loop", sel)
    cmd.color("mad_helix", "%s and ss H" % sel)
    cmd.color("mad_sheet", "%s and ss S" % sel)


# -----------------------------------------------------------------------------
# 4. Acidos nucleicos
# -----------------------------------------------------------------------------
def style_nucleic(sel="nucl"):
    """Backbone continuo com aneis preenchidos e fosfatos destacados."""
    if not _has(sel):
        return

    cmd.show("cartoon", sel)
    cmd.set("cartoon_ring_mode", 3)          # aneis solidos
    cmd.set("cartoon_ring_finder", 1)
    cmd.set("cartoon_ring_width", 0.25)
    cmd.set("cartoon_ring_transparency", 0.15)
    cmd.set("cartoon_nucleic_acid_mode", 4)
    cmd.set("cartoon_ladder_mode", 1)

    cmd.color("mad_dna_bb", sel)
    cmd.color("mad_dna_p", "%s and name P+OP1+OP2+O1P+O2P" % sel)


# -----------------------------------------------------------------------------
# 5. Lipideos
# -----------------------------------------------------------------------------
def style_lipids(sel="memb"):
    """Licorice estratificado por moiety.

    As tampas dos sticks do PyMOL sao hemisfericas, entao o licorice ja e
    naturalmente arredondado. As cabecas polares vao para esferas, reproduzindo
    a leitura de coroa densa sobre o campo de caudas.
    """
    if not _has(sel):
        return

    cmd.show("sticks", sel)
    cmd.set("stick_radius", 0.30, sel)
    cmd.set("stick_h_scale", 1.0)

    cmd.select("lip_head", "%s and name %s" % (sel, NAMES["head"]))
    cmd.select("lip_phos", "%s and name %s" % (sel, NAMES["phos"]))
    cmd.select("lip_glyc", "%s and name %s" % (sel, NAMES["glyc"]))
    cmd.select("lip_tail", "%s and name %s" % (sel, NAMES["tail"]))
    cmd.deselect()

    # Ordem importa: cada camada sobrescreve a anterior nos atomos comuns.
    cmd.color("mad_tail_a", sel)
    cmd.color("mad_tail_b", "lip_tail and name *B")
    cmd.color("mad_glyc", "lip_glyc")
    cmd.color("mad_phos", "lip_phos")
    cmd.color("mad_head", "lip_head")

    cmd.color("mad_tail_in",
              "%s and resn %s and not (lip_head or lip_phos)"
              % (sel, RESN["memb_inner"]))
    cmd.color("mad_glyc", "%s and resn %s" % (sel, RESN["sterol"]))

    if _has("lip_head"):
        cmd.show("spheres", "lip_head")
        cmd.set("sphere_scale", 0.55, "lip_head")


# -----------------------------------------------------------------------------
# 6. Ions
# -----------------------------------------------------------------------------
def style_ions(sel="ions"):
    """Esferas opacas: o contraste de material contra a agua translucida e o
    que os torna legiveis sem precisar aumentar o raio."""
    if not _has(sel):
        return

    cmd.show("spheres", sel)
    cmd.set("sphere_scale", 0.50, sel)
    for color, resn in ION_COLORS.items():
        cmd.color(color, "%s and resn %s" % (sel, resn))


# -----------------------------------------------------------------------------
# 7. Agua
# -----------------------------------------------------------------------------
def style_water(sel="wat", mode="field", resolution=5.0, level=1.0, grid=1.2):
    """Agua como campo continuo (mode='field'), esferas translucidas
    (mode='spheres') ou oculta (mode='hide').

    O campo usa mapa gaussiano + isosuperficie, reproduzindo o volume difuso da
    referencia a um custo muito menor que renderizar cada molecula.

    'resolution' controla o grao: 2-3 revela moleculas individuais, 5-7 funde
    tudo em um campo liso.

    Edge case: acima de ~200k aguas o map_new pode consumir varios GB. O guarda
    abaixo cai automaticamente para esferas nesse regime.
    """
    if not _has(sel) or mode == "hide":
        cmd.hide("everything", sel)
        return

    n = cmd.count_atoms(sel)
    if mode == "field" and n > 200000:
        print("[style_madson] %d atomos de agua: usando esferas para evitar "
              "estouro de memoria no map_new." % n)
        mode = "spheres"

    if mode == "field":
        cmd.set("gaussian_resolution", resolution)
        cmd.map_new("map_wat", "gaussian", grid, sel, 4)
        cmd.isosurface("surf_wat", "map_wat", level)
        cmd.color("mad_water", "surf_wat")
        cmd.set("transparency", 0.62, "surf_wat")
        cmd.set("surface_smooth_edges", 1)
        cmd.disable("map_wat")
    else:
        cmd.show("spheres", sel)
        cmd.set("sphere_scale", 0.35, sel)
        cmd.set("sphere_transparency", 0.75, sel)
        cmd.color("mad_water", sel)


# -----------------------------------------------------------------------------
# 8. Ligantes
# -----------------------------------------------------------------------------
def style_ligands(sel="lig"):
    if not _has(sel):
        return
    cmd.show("sticks", sel)
    cmd.set("stick_radius", 0.22, sel)
    cmd.color("mad_lig", sel)
    cmd.color("grey70", "%s and elem C" % sel)


# -----------------------------------------------------------------------------
# Entrada principal
# -----------------------------------------------------------------------------
def apply_style(water="field", quality="publication", shadows=0, ao=1, fog=0,
                hydrogens=0, split=0, orient=1):
    """Aplica o estilo completo a tudo que estiver carregado.

    water     : 'field' | 'spheres' | 'hide'
    quality   : 'draft' | 'screen' | 'publication'
    shadows   : sombras projetadas (0 = apenas oclusao ambiente)
    ao        : oclusao ambiente
    fog       : depth cue, util para sistemas espessos (membrana + solvente)
    hydrogens : exibir hidrogenios (em all-atom eles so adicionam ruido)
    split     : converter as selecoes em objetos independentes
    orient    : enquadrar na proteina ao final
    """
    shadows, ao, fog = _truthy(shadows), _truthy(ao), _truthy(fog)
    hydrogens, split, orient = _truthy(hydrogens), _truthy(split), _truthy(orient)

    _define_colors()
    cmd.hide("everything")

    counts = make_selections()
    set_quality(quality)
    set_material(shadows=shadows, ao=ao, fog=fog)

    style_protein()
    style_nucleic()
    style_lipids()
    style_ions()
    style_water(mode=water)
    style_ligands()

    if not hydrogens:
        cmd.hide("everything", "hidro")

    if split:
        split_objects()

    if orient and counts.get("prot", 0) > 0:
        cmd.orient("prot")
        cmd.zoom("prot", 5)

    print("[style_madson] " + ", ".join("%s=%d" % kv for kv in counts.items()))
    return counts


def mad_render(filename="figura.png", width=3000, height=2400, dpi=600,
               background="white", opaque=0):
    """Render e exportacao. Deliberadamente separado do estilo: e a unica parte
    que produz arquivo em disco."""
    cmd.bg_color(background)
    cmd.set("opaque_background", 1 if _truthy(opaque) else 0)
    cmd.set("antialias", 5)
    cmd.set("hash_max", 400)
    cmd.ray(int(width), int(height))
    cmd.png(filename, dpi=int(dpi))


# Registro dos comandos no interpretador do PyMOL.
cmd.extend("mad_style", apply_style)
cmd.extend("mad_render", mad_render)
cmd.extend("mad_material", set_material)
cmd.extend("mad_water", style_water)
cmd.extend("mad_split", split_objects)

print("[style_madson] carregado. Comandos: mad_style, mad_render, "
      "mad_material, mad_water, mad_split")
