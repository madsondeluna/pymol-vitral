# =============================================================================
# style_madson.pml
# Estilo de visualizacao molecular: cartoon suave (helice azul / folha vermelha /
# alca branca), material plastico opaco, sombreamento por oclusao ambiente,
# lipideos em licorice CG-friendly, agua como campo continuo translucido.
#
# Uso:
#   pymol estrutura.pdb style_madson.pml
#   ou, dentro do PyMOL:  @style_madson.pml
#
# O script NAO renderiza nem salva nada. Ver bloco 11.
# =============================================================================


# -----------------------------------------------------------------------------
# 0. Paleta
# Cores definidas explicitamente para reprodutibilidade entre maquinas
# (as cores nomeadas do PyMOL variam de percepcao conforme o gamma do display).
# -----------------------------------------------------------------------------
set_color mad_helix,   [0.11, 0.33, 0.65]    # azul profundo, helices
set_color mad_sheet,   [0.78, 0.19, 0.17]    # vermelho tijolo, folhas
set_color mad_loop,    [0.94, 0.94, 0.92]    # branco quente, alcas/coil
set_color mad_water,   [0.62, 0.76, 0.88]    # azul claro, campo de agua
set_color mad_head,    [0.30, 0.75, 0.25]    # verde, cabecas polares
set_color mad_phos,    [0.90, 0.55, 0.15]    # laranja, fosfato
set_color mad_glyc,    [0.85, 0.85, 0.85]    # cinza claro, glicerol
set_color mad_tail_a,  [0.93, 0.60, 0.20]    # laranja, cauda A
set_color mad_tail_b,  [0.86, 0.40, 0.75]    # magenta, cauda B
set_color mad_tail_in, [0.82, 0.15, 0.12]    # vermelho, folheto interno
set_color mad_lig,     [0.55, 0.45, 0.80]    # lilas, ligantes
set_color mad_dna_bb,  [0.90, 0.90, 0.93]    # branco perolado, backbone DNA
set_color mad_dna_p,   [0.95, 0.70, 0.72]    # rosa pastel, fosfatos DNA


# -----------------------------------------------------------------------------
# 1. Qualidade geometrica
# Amostragem alta em todas as primitivas: e o que remove as facetas visiveis e
# da a leitura de "superficie continua" em vez de malha poligonal.
# Custo: memoria e tempo de ray tracing. Reduzir sphere_quality para 2 e
# cartoon_sampling para 10 se a cena tiver > 500k atomos.
# -----------------------------------------------------------------------------
set sphere_quality, 3
set stick_quality, 20
set surface_quality, 1
set cartoon_sampling, 16
set ribbon_sampling, 16
set line_smooth, 1


# -----------------------------------------------------------------------------
# 2. Material: plastico opaco de qualidade
# specular baixo + shininess intermediario = brilho largo e difuso, tipico de
# polimero fosco. Valores altos de shininess (> 60) produzem highlight pontual,
# que le como vidro/metal e nao como plastico.
# reflect controla o quanto a luz difusa preenche as regioes nao iluminadas.
# -----------------------------------------------------------------------------
set specular, 0.28
set shininess, 22
set spec_reflect, 0.12
set spec_direct, 0.05
set spec_count, 1
set reflect, 0.42
set direct, 0.38
set ambient, 0.14


# -----------------------------------------------------------------------------
# 3. Iluminacao e sombreamento
# Muitas luzes fracas em vez de uma forte: elimina o contraste duro e produz o
# gradiente suave. A profundidade vem da oclusao ambiente, nao de sombras
# projetadas, o que evita as manchas escuras que poluem cenas densas.
#
# Nota importante: ambient_occlusion_mode atua sobre esferas e superficies.
# Cartoon nao recebe AO no PyMOL; a percepcao de volume no cartoon vem do
# conjunto reflect/direct acima.
# -----------------------------------------------------------------------------
set light_count, 8
set light,  [-0.35, -0.35, -0.90]
set light2, [ 0.45, -0.20, -0.70]
set light3, [-0.20,  0.50, -0.60]
set light4, [ 0.30,  0.35, -0.85]

set ambient_occlusion_mode, 1
set ambient_occlusion_scale, 18
set ambient_occlusion_smooth, 12

set ray_shadow, 0
set ray_trace_mode, 0
set ray_interior_color, grey20
set ray_interior_reflect, 0.3

# Perspectiva leve. Ortografico (1) achata a cena e remove a sensacao de
# profundidade fisica; field_of_view alto (> 30) distorce as bordas.
set orthoscopic, 0
set field_of_view, 20

# Fog desligado por padrao. Ligar (depth_cue 1) se quiser separar planos em
# sistemas muito espessos, como membrana + solvente.
set depth_cue, 0
set ray_trace_fog, 0


# -----------------------------------------------------------------------------
# 4. Separacao dos componentes
# Selecoes nomeadas, nao objetos: preserva os estados da trajetoria e evita
# duplicar coordenadas. Se preferir objetos independentes, ver bloco 10.
#
# 'organic' e 'inorganic' sao seletores automaticos do PyMOL e falham em
# topologias coarse-grained, onde tudo costuma vir como HETATM sem elemento
# atribuido. As listas por resn abaixo cobrem esse caso.
# -----------------------------------------------------------------------------
select prot,  polymer.protein
select nucl,  polymer.nucleic
select wat,   resn HOH+WAT+SOL+TIP3+TIP4+T3P+W+PW+SPC
select ions,  resn NA+CL+K+MG+CA+ZN+FE+MN+CU+SOD+CLA+POT+ION+NA++CL-
select memb,  resn POPC+POPE+POPG+POPS+POPA+POPI+DPPC+DPPE+DPPG+DOPC+DOPE+DOPG+DLPC+DMPC+CHOL+CHL1+LPS+REMP+RAMP+KDO+LIPA+CDL+CDL2+CARD
select lig,   not (prot or nucl or wat or ions or memb) and not hydro

# Hidrogenios ocultos por padrao: em AA eles so adicionam ruido visual.
select hidro, hydro
deselect

hide everything


# -----------------------------------------------------------------------------
# 5. Proteina: cartoon sem pontas agudas
# 'oval' nas folhas substitui a seta por uma fita eliptica de extremidade
# arredondada. 'loop' com raio alto transforma a alca em tubo continuo.
# flat_sheets desligado mantem a torcao real da fita, que e o que da o aspecto
# organico; ligado, a fita vira um plano rigido.
# -----------------------------------------------------------------------------
show cartoon, prot

cartoon oval, prot and ss S
cartoon automatic, prot and ss H
cartoon loop, prot and not (ss S or ss H)

set cartoon_oval_width, 0.85
set cartoon_oval_length, 1.30
set cartoon_oval_quality, 16
set cartoon_loop_radius, 0.32
set cartoon_loop_quality, 16
set cartoon_tube_radius, 0.45
set cartoon_tube_quality, 16

set cartoon_flat_sheets, 0
set cartoon_smooth_loops, 1
set cartoon_round_helices, 1
set cartoon_fancy_helices, 0        # 1 adiciona aresta na helice; quebra o "smooth"
set cartoon_highlight_color, -1
set cartoon_discrete_colors, 0
set cartoon_side_chain_helper, 1
set cartoon_transparency, 0.0

color mad_loop,  prot
color mad_helix, prot and ss H
color mad_sheet, prot and ss S


# -----------------------------------------------------------------------------
# 6. Acidos nucleicos
# Backbone como tubo continuo + fosfatos como esferas destacadas, no espirito
# da referencia pastel. Bases em sticks finos para nao competir com a proteina.
# -----------------------------------------------------------------------------
show cartoon, nucl
set cartoon_ring_mode, 3            # aneis preenchidos, superficie solida
set cartoon_ring_finder, 1
set cartoon_ring_width, 0.25
set cartoon_ring_transparency, 0.15
set cartoon_nucleic_acid_mode, 4
set cartoon_ladder_mode, 1

color mad_dna_bb, nucl
color mad_dna_p,  nucl and name P+OP1+OP2+O1P+O2P


# -----------------------------------------------------------------------------
# 7. Lipideos (all-atom e coarse-grained)
# Licorice com raio alto: as tampas dos sticks do PyMOL sao hemisfericas, entao
# o resultado ja e naturalmente arredondado, sem pontas.
# As cabecas ficam em esferas para reproduzir a leitura de "coroa polar densa"
# sobre o campo de caudas.
# -----------------------------------------------------------------------------
show sticks, memb
set stick_radius, 0.30, memb
set stick_h_scale, 1.0

# Nomes de particula Martini. Em topologia all-atom essas selecoes ficam vazias
# e o fallback por resn no final do bloco assume o colorido.
select lip_head, memb and name NC3+NH3+CNO+PO4+GL0+NC3+TAP+GM1+GM2+GM3
select lip_phos, memb and name PO4+PO1+PO2+P+P1+P2+OP1+OP2
select lip_glyc, memb and name GL1+GL2+AM1+AM2+C1+C2+C3+GLY
select lip_tail, memb and (name C1A+C2A+C3A+C4A+C5A+D1A+D2A+D3A+D4A+C1B+C2B+C3B+C4B+C5B+D1B+D2B+D3B+D4B)
deselect

color mad_tail_a,  memb
color mad_glyc,    lip_glyc
color mad_phos,    lip_phos
color mad_head,    lip_head
color mad_tail_b,  lip_tail and name *B

show spheres, lip_head
set sphere_scale, 0.55, lip_head

# Diferenciacao por especie lipidica. Ajustar conforme a composicao do sistema:
# aqui o cardiolipina/PG (tipicamente citoplasmatico) recebe o vermelho do
# folheto interno da referencia.
color mad_tail_in, memb and resn POPG+POPS+CDL+CDL2+CARD and not (lip_head or lip_phos)
color mad_glyc,    memb and resn CHOL+CHL1


# -----------------------------------------------------------------------------
# 8. Ions
# Esferas cheias, sem transparencia: contraste de material contra a agua
# translucida e o que os torna legiveis sem aumentar o tamanho.
# -----------------------------------------------------------------------------
show spheres, ions
set sphere_scale, 0.50, ions

color purple,     ions and resn NA+SOD+NA+
color green,      ions and resn CL+CLA+CL-
color orange,     ions and resn K+POT
color forest,     ions and resn MG
color grey60,     ions and resn CA
color slate,      ions and resn ZN


# -----------------------------------------------------------------------------
# 9. Agua como campo continuo
# Mapa gaussiano + isosuperficie, em vez de milhares de esferas. Reproduz o
# aspecto de volume difuso da referencia e custa muito menos que renderizar
# cada molecula.
#
# gaussian_resolution controla o "grao": valores baixos (2-3) revelam moleculas
# individuais; valores altos (5-7) fundem tudo em um campo liso.
# Edge case: com > 200k aguas o map_new pode consumir varios GB. Nesse caso use
# o bloco alternativo comentado logo abaixo.
# -----------------------------------------------------------------------------
set gaussian_resolution, 5.0

map_new map_wat, gaussian, 1.2, wat, 4
isosurface surf_wat, map_wat, 1.0

color mad_water, surf_wat
set transparency, 0.62, surf_wat
set surface_smooth_edges, 1
set two_sided_lighting, 1
disable map_wat

# Alternativa leve (comentar o bloco acima e descomentar este):
# show spheres, wat
# set sphere_scale, 0.35, wat
# set sphere_transparency, 0.75, wat
# color mad_water, wat


# -----------------------------------------------------------------------------
# 10. Ligantes e finalizacao
# -----------------------------------------------------------------------------
show sticks, lig
set stick_radius, 0.22, lig
color mad_lig, lig
color grey70, lig and elem C

hide everything, hidro

set transparency_mode, 2            # blending por profundidade; evita artefato
                                    # de ordenacao entre agua e membrana

# Opcional: separar em objetos independentes, para ligar/desligar via painel.
# Nao usar em trajetorias multi-estado sem verificar a copia de todos os frames.
# create obj_prot, prot
# create obj_memb, memb
# create obj_ions, ions
# create obj_wat,  wat

orient prot
zoom prot, 5


# =============================================================================
# 11. RENDER E SAIDA (nao executado; descomentar quando for exportar)
# =============================================================================
# bg_color white
# set opaque_background, 0
# set antialias, 5
# set hash_max, 400
# ray 3000, 2400
# png figura.png, dpi=600
