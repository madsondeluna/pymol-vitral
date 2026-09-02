"""
pymol_molviz.core

Base compartilhada pelos modulos de membrana e de proteina: paleta, material,
iluminacao, oclusao ambiente, sombras, modo periodico e exportacao.

Nao e usado diretamente. Carregue pymol_molviz.membrane ou
pymol_molviz.protein, que importam este modulo.
"""

from pymol import cmd


# =============================================================================
# Paleta
# Cores em RGB explicito, e nao por nome do PyMOL, porque a percepcao das
# cores nomeadas varia com o gamma do display.
# =============================================================================
PALETTE = {
    # Estrutura secundaria
    "mv_helix":   [0.11, 0.33, 0.65],
    "mv_sheet":   [0.78, 0.19, 0.17],
    "mv_loop":    [0.94, 0.94, 0.92],
    # Lipideos
    "mv_head":    [0.30, 0.75, 0.25],
    "mv_phos":    [0.90, 0.55, 0.15],
    "mv_glyc":    [0.85, 0.85, 0.85],
    "mv_tail_a":  [0.93, 0.60, 0.20],
    "mv_tail_b":  [0.86, 0.40, 0.75],
    "mv_tail_in": [0.82, 0.15, 0.12],
    # Residuos por carga
    "mv_pos":     [0.15, 0.40, 0.80],
    "mv_neg":     [0.82, 0.20, 0.18],
    "mv_polar":   [0.55, 0.75, 0.90],
    "mv_apolar":  [0.95, 0.85, 0.45],
    # Contexto
    "mv_water":   [0.62, 0.76, 0.88],
    "mv_lig":     [0.55, 0.45, 0.80],
    "mv_dna_bb":  [0.90, 0.90, 0.93],
    "mv_dna_p":   [0.95, 0.70, 0.72],
    "mv_na":      [0.55, 0.35, 0.85],
    "mv_cl":      [0.35, 0.80, 0.45],
}

CHAIN_CYCLE = ["skyblue", "salmon", "palegreen", "wheat", "lightpink",
               "paleyellow", "deepteal", "lightorange"]

TYPE_CYCLE = ["mv_tail_a", "mv_tail_b", "mv_tail_in", "mv_head",
              "skyblue", "wheat", "deepteal", "salmon", "palegreen"]

WATER_RESN = "HOH+WAT+SOL+TIP3+TIP4+T3P+SPC+W+PW"
ION_RESN = "NA+CL+K+MG+CA+ZN+FE+MN+CU+SOD+CLA+POT+ION+NA++CL-"

ALL_REPS = ("cartoon", "spheres", "sticks", "surface", "mesh", "dots",
            "lines", "nonbonded", "ribbon")


# =============================================================================
# Utilitarios
# =============================================================================
def truthy(v):
    # Argumentos da linha de comando do PyMOL chegam sempre como string.
    if isinstance(v, str):
        return v.strip().lower() in ("1", "on", "yes", "true", "t")
    return bool(v)


# Elementos que um sistema biomolecular realmente contem. O que cair fora
# disto veio de inferencia errada, nao do sistema.
BIO_ELEM = ("H", "C", "N", "O", "P", "S", "Se", "F",
            "Na", "Cl", "K", "Mg", "Ca", "Zn", "Fe", "Mn", "Cu", "Br", "I")

# Raio de van der Waals por elemento. O alter de 'elem' NAO reatribui o raio:
# o PyMOL o define no load, entao corrigir so o elemento deixaria a esfera com
# o tamanho errado.
VDW = {"H": 1.20, "C": 1.70, "N": 1.55, "O": 1.52, "P": 1.80, "S": 1.80,
       "Se": 1.90, "F": 1.47, "Cl": 1.75, "Br": 1.85, "I": 1.98,
       "Na": 2.27, "K": 2.75, "Mg": 1.73, "Ca": 2.31, "Zn": 1.39,
       "Fe": 1.94, "Mn": 1.97, "Cu": 1.40}

# Residuo de ion: o elemento vem do nome do residuo, e nao do nome do atomo.
# Sem isto um ion CL viraria carbono pela regra da primeira letra.
ION_ELEM = {"NA": "Na", "SOD": "Na", "CL": "Cl", "CLA": "Cl", "K": "K",
            "POT": "K", "MG": "Mg", "CA": "Ca", "CAL": "Ca", "ZN": "Zn",
            "FE": "Fe", "MN": "Mn", "CU": "Cu"}


def _elem_from_name(name, resn, monoatomico=True):
    """Elemento a partir do nome do atomo, a convencao dos campos de forca.

    O nome do residuo so decide quando o residuo tem um atomo so. 'CL' e ao
    mesmo tempo o cloreto e o resname da cardiolipina, e tratar a segunda como
    ion transforma 241 atomos de lipideo em cloro.
    """
    r = resn.strip().upper()
    if monoatomico and r in ION_ELEM:
        return ION_ELEM[r]
    n = name.strip().lstrip("0123456789")
    return n[0].upper() if n else "C"


def poliatomicos(sel, resns):
    """Dos resns dados, os que tem mais de um atomo por residuo em 'sel'.

    Um ion e monoatomico. Um resname da lista de ions com dezenas de atomos por
    residuo e outra molecula com o mesmo nome, e a colisao que aparece na
    pratica e CL: cloreto e cardiolipina.
    """
    fora = []
    # ION_RESN traz 'NA++CL-', entao o split devolve entradas vazias: os nomes
    # com carga carregam o mesmo caractere que separa a lista.
    for resn in [r for r in resns.split("+") if r]:
        alvo = "(%s) and resn %s" % (sel, resn)
        n_at = cmd.count_atoms(alvo)
        if not n_at:
            continue
        ids = set()
        cmd.iterate(alvo, "ids.add((model, segi, chain, resi))",
                    space={"ids": ids})
        if ids and n_at / float(len(ids)) > 1.0:
            fora.append((resn, n_at, len(ids)))
    return fora


def ion_selection(src, quiet=0):
    """Selecao de ions, descartando resname homonimo de molecula poliatomica."""
    fora = poliatomicos(src, ION_RESN)
    sel = "(%s) and resn %s" % (src, ION_RESN)
    if fora:
        sel += " and not resn %s" % "+".join(f[0] for f in fora)
        if not truthy(quiet):
            for resn, n_at, n_res in fora:
                print("[molviz] '%s' tem %.0f atomos por residuo: nao e ion, "
                      "%d moleculas tratadas como lipideo."
                      % (resn, n_at / float(n_res), n_res))
    return sel


def fix_elements(sel="all", quiet=0):
    """Corrige elementos inferidos errado a partir do nome do atomo.

    Um PDB sem as colunas 77-78 deixa o PyMOL adivinhar o elemento pelo nome, e
    ele adivinha por prefixo de duas letras: CA vira calcio, CD vira cadmio, OG
    vira oganesson, SO vira um simbolo que nao existe. Sao nomes normais de
    atomo em campo de forca, entao o erro atinge qualquer saida de dinamica
    molecular escrita sem esse campo.

    O estrago nao e cosmetico. O raio de van der Waals passa a ser o do
    elemento errado, e com ele mudam spacefill, superficie e o mapa gaussiano;
    as selecoes por 'elem C' e 'elem O' que definem as camadas do lipideo
    perdem esses atomos; e a cor por elemento sai trocada.

    Devolve quantos atomos foram corrigidos.
    """
    simbolos = set()
    cmd.iterate(sel, "simbolos.add(elem)", space={"simbolos": simbolos})

    # Simbolo que nao existe num sistema biomolecular: erro certo.
    suspeitos = sorted(e for e in simbolos if e and e not in BIO_ELEM)
    alvos = ["elem %s" % e for e in suspeitos]

    # Simbolo de ion que aparece FORA de um residuo de ion: 'CA' e o caso que
    # importa, porque e ao mesmo tempo calcio e o nome do carbono alfa, e o
    # mesmo vale para CD, MG e ZN em campo de forca. O elemento sozinho nao
    # decide; o residuo decide.
    metais = sorted(set(ION_ELEM.values()) & simbolos)
    if metais:
        alvos.append("((%s) and not resn %s)"
                     % (" or ".join("elem %s" % e for e in metais), ION_RESN))
        suspeitos += [e for e in metais if e not in suspeitos]

    if not alvos:
        return 0

    alvo = "(%s) and (%s)" % (sel, " or ".join(alvos))
    n = cmd.count_atoms(alvo)
    if not n:
        return 0

    poli = set(f[0] for f in poliatomicos(sel, ION_RESN))
    cmd.alter(alvo,
              "elem = _de_nome(name, resn, resn.strip().upper() not in _poli)",
              space={"_de_nome": _elem_from_name, "_poli": poli})
    cmd.alter(alvo, "vdw = _vdw.get(elem, 1.70)", space={"_vdw": VDW})
    cmd.rebuild()
    if not truthy(quiet):
        print("[molviz] %d atomos com elemento inferido errado (%s): "
              "corrigidos pelo nome do atomo."
              % (n, ", ".join(suspeitos[:6])))
    return n


def reload_package():
    """Recarrega o pacote a partir do disco, sem reabrir o PyMOL.

    'run molviz.pml' de novo NAO traz o codigo novo: o import encontra o pacote
    ja em sys.modules e devolve o que esta na memoria, entao a sessao continua
    rodando a versao antiga sem nenhum aviso. O sintoma e uma edicao que nao
    surte efeito, ou um preset que imprime a mensagem antiga.

    Isto apaga as entradas do pacote em sys.modules e importa de novo, o que
    faz cmd.extend registrar as funcoes novas por cima das velhas.
    """
    import os
    import sys

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for nome in [n for n in list(sys.modules)
                 if n == "pymol_molviz" or n.startswith("pymol_molviz.")]:
        del sys.modules[nome]
    if raiz not in sys.path:
        sys.path.insert(0, raiz)

    import pymol_molviz
    pymol_molviz.load(auto=False)
    print("[molviz] recarregado de %s" % raiz)


def truthy_width(v):
    """Largura de coluna em milimetros, ou 0 para nao ligar o modo periodico.

    Separada de truthy porque o argumento aqui nao e uma chave: '85' e '170'
    sao valores, e truthy('85') seria falso por nao estar na lista de sim.
    """
    try:
        return float(v) > 0
    except (TypeError, ValueError):
        return False


def has(sel):
    try:
        return cmd.count_atoms(sel) > 0
    except Exception:
        return False


def n_residues(sel):
    if not has(sel):
        return 0
    return len(set(cmd.get_model(sel).get_residues()))


def define_colors():
    for name, rgb in PALETTE.items():
        cmd.set_color(name, rgb)


def source_objects(reserved):
    """Objetos carregados pelo usuario, excluindo os criados pelos modulos."""
    return [o for o in cmd.get_object_list("all") if o not in reserved]


def clear_reps(objects):
    for obj in objects:
        if has(obj):
            for rep in ALL_REPS:
                cmd.hide(rep, obj)
            cmd.set("transparency", 0.0, obj)
            cmd.set("sphere_transparency", 0.0, obj)
            cmd.set("cartoon_transparency", 0.0, obj)


def auto_isolevel(map_name, bins=8):
    """Nivel de isosuperficie derivado do histograma do mapa.

    Um nivel fixo falha em silencio quando a resolucao gaussiana muda: o
    isosurface nao gera triangulo nenhum, e objeto vazio nao e registrado pelo
    PyMOL, o que produz um confuso 'Invalid selection name' adiante.
    """
    h = cmd.get_volume_histogram(map_name, bins)
    return min(h[2] + h[3], h[1] * 0.8)   # media + 1 desvio, teto em 80% do max


# Caixa unitaria devolvida por get_extent quando o mapa nao tem conteudo.
_EMPTY_MAP_EXTENT = [[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]]

# Fator B temporario para a gaussiana ter largura. O valor nao aparece na
# figura: define a dispersao de cada atomo no mapa, e o nivel sai do histograma
# do mapa resultante, entao a superficie e a mesma para qualquer B uniforme.
_MAP_B = 20.0


def gaussian_map_empty(map_name):
    """Mapa sem conteudo, que e o que map_new devolve nos casos tratados
    abaixo. O PyMOL nao levanta erro aqui: ele aparece so no histograma, como
    'failed to get map state', que nao diz nada sobre a causa."""
    try:
        return cmd.get_extent(map_name) == _EMPTY_MAP_EXTENT
    except Exception:
        return True


def gaussian_isosurface(surf_name, map_name, selection, grid=1.2,
                        resolution=3.0, buffer=4, label="molviz"):
    """Isosuperficie gaussiana sobre uma selecao, com as tres armadilhas do
    map_new tratadas.

    map_new do tipo gaussian devolve um mapa VAZIO quando todos os fatores B
    da selecao sao zero, que e exatamente o que um PDB escrito por dinamica
    molecular traz. A largura da gaussiana de cada atomo sai do fator B; com
    B zero para todos, nada e depositado na grade. Nem map_new nem isosurface
    reclamam: o erro aparece adiante, no histograma.

    Os fatores B originais sao restaurados atomo a atomo. lip_tail e wat_o sao
    selecoes dentro de obj_lipid e obj_wat, e nao objetos proprios, entao
    escrever na coluna B aqui atinge o objeto que o usuario ve.

    Devolve True se a superficie foi criada.
    """
    if not cmd.count_atoms(selection):
        print("[%s] '%s' nao tem atomos: isosuperficie nao criada." %
              (label, selection))
        return False

    b_orig = {}
    cmd.iterate(selection, "b_orig[(model, index)] = b",
                space={"b_orig": b_orig})
    tocar_b = max(b_orig.values()) <= 0.0

    res_orig = cmd.get("gaussian_resolution")
    try:
        if tocar_b:
            cmd.alter(selection, "b = %f" % _MAP_B)
        cmd.set("gaussian_resolution", float(resolution))
        cmd.delete(map_name)
        cmd.map_new(map_name, "gaussian", float(grid), selection, float(buffer))
    finally:
        if tocar_b:
            cmd.alter(selection, "b = b_orig.get((model, index), b)",
                      space={"b_orig": b_orig})
        cmd.set("gaussian_resolution", res_orig)

    if gaussian_map_empty(map_name):
        cmd.delete(map_name)
        print("[%s] mapa gaussiano de '%s' saiu vazio: isosuperficie nao "
              "criada." % (label, selection))
        return False

    cmd.delete(surf_name)
    cmd.isosurface(surf_name, map_name, auto_isolevel(map_name))
    cmd.disable(map_name)

    if surf_name not in cmd.get_names("objects"):
        print("[%s] o nivel nao interceptou o mapa de '%s': nenhum triangulo "
              "gerado." % (label, selection))
        return False
    return True


# =============================================================================
# Material e iluminacao
# =============================================================================
def material(shadows=1, ao=1, hq=1):
    """Material plastico opaco, oclusao ambiente e fundo branco.

    specular baixo + shininess intermediario produz brilho largo e difuso, de
    polimero fosco. shininess alto gera highlight pontual, que le como vidro.

    O balanco de luz e calibrado para a oclusao ambiente ser visivel: a AO do
    PyMOL modula o termo ambiente, entao com 'ambient' baixo ela existe mas
    nao aparece. Dai ambiente relativamente alto e luz direta moderada.
    """
    define_colors()

    hq = truthy(hq)
    cmd.set("sphere_quality", 3 if hq else 1)
    cmd.set("stick_quality", 20 if hq else 8)
    cmd.set("surface_quality", 1 if hq else 0)
    cmd.set("cartoon_sampling", 16 if hq else 7)
    cmd.set("ribbon_sampling", 16 if hq else 7)

    cmd.set("specular", 0.22)
    cmd.set("shininess", 25)
    cmd.set("spec_reflect", 0.10)
    cmd.set("spec_direct", 0.05)
    cmd.set("reflect", 0.32)
    cmd.set("direct", 0.22)
    cmd.set("ambient", 0.44)

    # Poucas luzes: com ambiente alto, muitas luzes lavam a cena e anulam o
    # contraste que a oclusao acabou de criar.
    cmd.set("light_count", 4)
    cmd.set("light", [-0.35, -0.35, -0.90])
    cmd.set("light2", [0.45, -0.20, -0.70])
    cmd.set("light3", [-0.20, 0.50, -0.60])

    cmd.set("ambient_occlusion_mode", 1 if truthy(ao) else 0)
    cmd.set("ambient_occlusion_scale", 12)
    cmd.set("ambient_occlusion_smooth", 15)

    cmd.set("ray_shadow", 1 if truthy(shadows) else 0)
    cmd.set("ray_shadow_decay_factor", 0.15)
    cmd.set("ray_shadow_decay_range", 1.8)
    # Transparencia nao projeta sombra: uma superficie de agua cobrindo a caixa
    # escureceria tudo por baixo e a cena viraria um cinza uniforme.
    cmd.set("ray_transparency_shadows", 0)
    cmd.set("ray_interior_shadows", 0)
    cmd.set("ray_trace_mode", 0)          # > 0 desenha contorno de ilustracao
    cmd.set("ray_interior_color", "grey20")

    cmd.set("orthoscopic", 0)
    cmd.set("field_of_view", 20)
    cmd.set("depth_cue", 0)
    cmd.set("ray_trace_fog", 0)
    cmd.set("transparency_mode", 2)       # blending por profundidade
    cmd.set("two_sided_lighting", 1)
    cmd.set("surface_smooth_edges", 1)
    cmd.set("auto_show_selections", 0)    # indicadores rosa cobririam a cena

    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)

    cartoon_style()


def cartoon_style():
    """Cartoon sem pontas agudas.

    'oval' nas fitas beta substitui a seta por uma fita eliptica arredondada.
    Contrapartida: perde-se a indicacao de direcionalidade N->C.
    """
    cmd.set("cartoon_oval_width", 0.85)
    cmd.set("cartoon_oval_length", 1.30)
    cmd.set("cartoon_oval_quality", 16)
    cmd.set("cartoon_loop_radius", 0.32)
    cmd.set("cartoon_loop_quality", 16)
    cmd.set("cartoon_tube_radius", 0.45)
    cmd.set("cartoon_flat_sheets", 0)     # mantem a torcao real da fita
    cmd.set("cartoon_smooth_loops", 1)
    cmd.set("cartoon_round_helices", 1)
    cmd.set("cartoon_fancy_helices", 0)   # 1 adiciona aresta e quebra o smooth
    cmd.set("cartoon_highlight_color", -1)
    cmd.set("cartoon_discrete_colors", 0)
    cmd.set("cartoon_side_chain_helper", 1)


# ambient_occlusion_scale e a distancia de amostragem em angstrom, e o padrao
# 25 do PyMOL e calibrado para esfera. Numa superficie molecular de proteina as
# cavidades sao mais largas que isso, ficam totalmente ocluidas e saem PRETAS,
# em manchas que leem como defeito de geometria. Medido nos dois regimes: em
# esferas de membrana 12 e 25 rendem imagem indistinguivel, e em superficie so
# o valor baixo e utilizavel. Dai a escala menor em todos os niveis.
AO_LEVELS = {
    # (modo, ambient, direct, reflect, escala)
    "off":     (0, 0.14, 0.38, 0.42, 0),
    "soft":    (1, 0.32, 0.26, 0.36, 8),
    "medium":  (1, 0.45, 0.20, 0.32, 12),
    "strong":  (1, 0.62, 0.12, 0.22, 17),
    "extreme": (1, 0.80, 0.05, 0.12, 22),
}


def ambient_occlusion(strength="medium"):
    """Oclusao ambiente: off, soft, medium, strong, extreme.

    Cada nivel ajusta ambiente, luz direta e escala em conjunto, porque a AO
    modula o termo ambiente e mexer so na escala nao muda quase nada.

    A AO e assada na geometria no momento da construcao, entao o rebuild e
    obrigatorio. Limitacao do PyMOL: ela atua sobre esferas e superficies, nao
    sobre cartoon.
    """
    if strength not in AO_LEVELS:
        print("[molviz] niveis: %s" % ", ".join(AO_LEVELS))
        return
    mode, amb, direct, reflect, scale = AO_LEVELS[strength]
    cmd.set("ambient_occlusion_mode", mode)
    cmd.set("ambient", amb)
    cmd.set("direct", direct)
    cmd.set("reflect", reflect)
    if scale:
        cmd.set("ambient_occlusion_scale", scale)
    cmd.rebuild()
    print("[molviz] oclusao: %s (nao atua sobre cartoon)" % strength)


SHADOW_LEVELS = {
    # (ray_shadow, luzes, direct, ambient, decaimento)
    "off":    (0, 3, 0.20, 0.45, 0.0),
    "soft":   (1, 6, 0.35, 0.38, 0.15),
    "medium": (1, 3, 0.50, 0.30, 0.10),
    "hard":   (1, 1, 0.70, 0.18, 0.00),
}


def shadows(level="soft"):
    """Sombras projetadas: off, soft, medium, hard.

    So aparecem apos 'ray', nunca no viewport. Dependem de luz direta forte,
    que e o que a calibracao de AO reduz, entao cada nivel reajusta direct e
    ambient junto.

    A maciez vem do numero de luzes: nao existe raio de fonte de luz no PyMOL,
    e a penumbra e a sobreposicao de varias sombras. Por isso 'soft' custa
    mais tempo de render que 'hard', nao menos.
    """
    if level not in SHADOW_LEVELS:
        print("[molviz] niveis: %s" % ", ".join(SHADOW_LEVELS))
        return
    shadow, nlight, direct, ambient, decay = SHADOW_LEVELS[level]
    cmd.set("ray_shadow", shadow)
    cmd.set("light_count", nlight)
    cmd.set("direct", direct)
    cmd.set("ambient", ambient)
    cmd.set("ray_shadow_decay_factor", decay)
    cmd.set("ray_shadow_decay_range", 1.8)
    cmd.set("ray_transparency_shadows", 0)
    cmd.rebuild()
    print("[molviz] sombras: %s. Visiveis apenas apos 'ray'." % level)


def realism(mode="studio", desat=1):
    """Combinacao de iluminacao: studio, depth, dramatic, flat.

    Nenhum parametro isolado produz realismo. O que produz e a convivencia de
    oclusao de contato, sombra projetada suave, perspectiva real e
    desaturacao — pigmento real e menos saturado que RGB puro.

    studio   - luz de tres pontos, sombra suave. Neutro, para figura.
    depth    - studio + neblina atmosferica, para sistemas espessos.
    dramatic - luz principal unica e rasante. Alto contraste; perde detalhe
               nas regioes escuras.
    flat     - sem sombra nem AO. Nao e realista; existe para comparar.
    """
    presets = {
        # (ambient, direct, reflect, luzes, sombra, ao, ao_escala, fog, fov)
        "studio":   (0.38, 0.34, 0.30, 6, 1, 1, 28, 0, 30),
        "depth":    (0.38, 0.34, 0.30, 6, 1, 1, 28, 1, 32),
        "dramatic": (0.16, 0.75, 0.18, 1, 1, 1, 20, 0, 35),
        "flat":     (0.55, 0.45, 0.20, 2, 0, 0, 0, 0, 20),
    }
    if mode not in presets:
        print("[molviz] modos: %s" % ", ".join(presets))
        return

    amb, direct, refl, nlight, shad, ao, scale, fog, fov = presets[mode]
    cmd.set("ambient", amb)
    cmd.set("direct", direct)
    cmd.set("reflect", refl)
    cmd.set("light_count", nlight)
    cmd.set("ray_shadow", shad)
    cmd.set("ambient_occlusion_mode", ao)
    if scale:
        cmd.set("ambient_occlusion_scale", scale)
    cmd.set("depth_cue", fog)
    cmd.set("ray_trace_fog", fog)
    cmd.set("field_of_view", fov)
    if fog:
        # Com fundo branco a neblina clareia, nao escurece.
        cmd.set("fog_start", 0.40)
    if mode == "dramatic":
        cmd.set("light", [-0.60, -0.45, -0.65])

    # Especularidade dupla: um lobo largo e fosco mais um estreito e fraco. E
    # o que separa plastico de qualidade de plastico de brinquedo, que tem um
    # unico highlight duro.
    cmd.set("specular", 0.20)
    cmd.set("shininess", 28)
    cmd.set("spec_count", 2)
    cmd.set("spec_reflect", 0.08)
    cmd.set("ray_transparency_specular", 0.12)
    cmd.set("ray_trace_mode", 0)
    cmd.set("ray_transparency_shadows", 0)

    if truthy(desat):
        desaturate(0.18)
    cmd.rebuild()
    print("[molviz] realismo: %s. Completo apenas apos 'ray'." % mode)


def desaturate(amount=0.18):
    """Puxa a paleta na direcao do cinza medio de cada cor.

    Cor totalmente saturada le como plastico de brinquedo; pigmento real
    reflete uma banda larga do espectro, nunca um canal puro. 0.18 e sutil;
    acima de 0.4 a estratificacao de cor comeca a se perder.
    Reversivel: desaturate(0) restaura a paleta original.
    """
    a = float(amount)
    for name, rgb in PALETTE.items():
        mid = sum(rgb) / 3.0
        cmd.set_color(name, [c * (1 - a) + mid * a for c in rgb])
    cmd.recolor()


# =============================================================================
# Figura de periodico e exportacao
# =============================================================================
def paper(width_mm=85, dpi=300):
    """Configuracao para figura de periodico.

    Prioriza legibilidade em impressao e reducao, nao impacto visual. Difere
    de realism() em tres pontos deliberados:

    - Sombra projetada desligada: em figura reduzida ela escurece regioes sem
      carregar informacao. A oclusao de contato fica, pois comunica relevo.
    - Projecao ortografica: perspectiva faz um folheto plano parecer curvo, o
      que e desonesto numa figura quantitativa.
    - Paleta saturada restaurada: cor saturada separa melhor as camadas quando
      a figura cai para a largura de uma coluna.

    width_mm: 85 para coluna simples, 170 para largura dupla.
    """
    cmd.set("ambient", 0.45)
    cmd.set("direct", 0.30)
    cmd.set("reflect", 0.25)
    cmd.set("light_count", 2)
    cmd.set("ray_shadow", 0)
    cmd.set("ambient_occlusion_mode", 1)
    cmd.set("ambient_occlusion_scale", 12)
    cmd.set("ambient_occlusion_smooth", 15)
    cmd.set("specular", 0.18)
    cmd.set("shininess", 30)
    cmd.set("spec_count", 1)
    cmd.set("depth_cue", 0)
    cmd.set("ray_trace_fog", 0)
    cmd.set("orthoscopic", 1)
    cmd.set("ray_trace_mode", 0)
    grayscale(0)          # devolve a cor, se um teste anterior deixou em cinza
    desaturate(0.0)
    cmd.rebuild()

    px = int(round(float(width_mm) / 25.4 * float(dpi)))
    print("[molviz] modo periodico. %s mm a %s dpi = %d px." % (width_mm, dpi, px))
    print("[molviz] renderize: mv_render figura.png, %d, %d, %s"
          % (px, int(px * 0.75), dpi))
    return px


# RGB original de cada cor convertida por grayscale(). Vazio quando a cena
# esta em cor.
_GRAY_BACKUP = {}

# Coeficientes de luminancia da recomendacao ITU-R BT.601, que e a conversao
# que uma impressora monocromatica aplica. Um cinza pela media dos canais
# daria outro resultado e nao serviria de teste.
_LUMA = (0.299, 0.587, 0.114)


def grayscale(on=1):
    """Teste de impressao em preto e branco.

    Nao e opcional: muitos periodicos ainda imprimem em P&B ou cobram por
    figura colorida. Cores de luminancia proxima (o verde das cabecas contra o
    laranja das caudas, o azul das helices contra o vermelho das folhas) podem
    colapsar no mesmo tom. Se ocorrer, diferencie por claridade, nao so matiz.

    O PyMOL nao tem ajuste de escala de cinza: cada cor em uso e reescrita
    para a sua propria luminancia e depois devolvida. So alcanca cor com nome,
    entao um gradiente aplicado por 'spectrum' continua colorido, e o log
    avisa quando encontra um.
    """
    global _GRAY_BACKUP
    ligar = truthy(on)

    if ligar and not _GRAY_BACKUP:
        usados = set()
        cmd.iterate("all", "usados.add(color)", space={"usados": usados})
        nomes = dict((i, n) for n, i in cmd.get_color_indices())
        anonimas = 0
        for idx in usados:
            nome = nomes.get(idx)
            if nome is None:
                anonimas += 1
                continue
            rgb = cmd.get_color_tuple(idx)
            if rgb is None:
                continue
            _GRAY_BACKUP[nome] = list(rgb)
            y = sum(c * k for c, k in zip(rgb, _LUMA))
            cmd.set_color(nome, [y, y, y])
        if anonimas:
            print("[molviz] %d cores sem nome (gradiente) seguem coloridas."
                  % anonimas)
    elif not ligar and _GRAY_BACKUP:
        for nome, rgb in _GRAY_BACKUP.items():
            cmd.set_color(nome, rgb)
        _GRAY_BACKUP = {}

    cmd.recolor()
    cmd.rebuild()
    print("[molviz] escala de cinza: %s" % ("on" if ligar else "off"))


def extent(sel):
    """Dimensoes em angstrom e nanometro, para a legenda da figura.

    O PyMOL nao desenha barra de escala para sistemas moleculares; o caminho
    pratico e informar a dimensao no texto.
    """
    if not has(sel):
        print("[molviz] selecao vazia: %s" % sel)
        return
    (x1, y1, z1), (x2, y2, z2) = cmd.get_extent(sel)
    d = (x2 - x1, y2 - y1, z2 - z1)
    print("[molviz] %s: %.1f x %.1f x %.1f A (%.1f x %.1f x %.1f nm)"
          % ((sel,) + d + tuple(v / 10.0 for v in d)))
    return d


def render(filename="figura.png", width=3000, height=2400, dpi=600,
           transparent=0):
    """Render e exportacao.

    O viewport nao aplica o modelo especular, as sombras nem o antialiasing:
    so o ray mostra o material real. Fundo branco gravado por padrao.
    """
    cmd.set("ray_opaque_background", 0 if truthy(transparent) else 1)
    cmd.set("antialias", 5)
    cmd.set("hash_max", 400)
    cmd.ray(int(width), int(height))
    cmd.png(filename, dpi=int(dpi))
    print("[molviz] salvo: %s (%dx%d, %s dpi)" % (filename, width, height, dpi))


def register_common():
    """Comandos compartilhados, prefixados mv_."""
    for name, fn in (("mv_material", material), ("mv_ao", ambient_occlusion),
                     ("mv_shadows", shadows), ("mv_realism", realism),
                     ("mv_desaturate", desaturate), ("mv_paper", paper),
                     ("mv_grayscale", grayscale), ("mv_extent", extent),
                     ("mv_reload", reload_package),
                     ("mv_fix_elements", fix_elements),
                     ("mv_render", render)):
        cmd.extend(name, fn)
