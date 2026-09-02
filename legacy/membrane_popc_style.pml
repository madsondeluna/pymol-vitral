# =============================================================================
# membrane_popc_style.pml
# Estilo para bicamada POPC all-atom sem hidrogenios explicitos.
#
# Uso:  @/caminho/para/membrane_popc_style.pml
#
# Nao renderiza nem salva. Ver bloco 6.
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Paleta
# -----------------------------------------------------------------------------
set_color mad_helix,   [0.11, 0.33, 0.65]
set_color mad_sheet,   [0.78, 0.19, 0.17]
set_color mad_loop,    [0.94, 0.94, 0.92]
set_color mad_water,   [0.62, 0.76, 0.88]
set_color mad_head,    [0.30, 0.75, 0.25]
set_color mad_phos,    [0.90, 0.55, 0.15]
set_color mad_glyc,    [0.85, 0.85, 0.85]
set_color mad_tail_a,  [0.93, 0.60, 0.20]
set_color mad_tail_in, [0.82, 0.15, 0.12]
set_color mad_lig,     [0.55, 0.45, 0.80]

# -----------------------------------------------------------------------------
# 2. Qualidade, material e iluminacao
# specular baixo + shininess intermediario: brilho largo e difuso, de polimero
# fosco. Valores altos de shininess produzem highlight pontual, que le como
# vidro ou metal.
# -----------------------------------------------------------------------------
set sphere_quality, 3
set stick_quality, 20
set surface_quality, 1
set cartoon_sampling, 16

set specular, 0.28
set shininess, 22
set spec_reflect, 0.12
set spec_direct, 0.05
set reflect, 0.42
set direct, 0.38
set ambient, 0.14

# Varias luzes fracas em vez de uma forte: elimina o contraste duro.
set light_count, 8
set light,  [-0.35, -0.35, -0.90]
set light2, [ 0.45, -0.20, -0.70]
set light3, [-0.20,  0.50, -0.60]
set light4, [ 0.30,  0.35, -0.85]

# Profundidade vem da oclusao ambiente, nao de sombras projetadas: evita as
# manchas escuras que poluem cenas densas como uma bicamada solvatada.
set ambient_occlusion_mode, 1
set ambient_occlusion_scale, 18
set ambient_occlusion_smooth, 12

set ray_shadow, 0
set ray_trace_mode, 0
set ray_interior_color, grey20
set orthoscopic, 0
set field_of_view, 20
set depth_cue, 0
set ray_trace_fog, 0
set transparency_mode, 2
set two_sided_lighting, 1

# Indicadores rosa de selecao desligados: com 20k atomos eles cobrem a cena.
set auto_show_selections, off

hide everything

# -----------------------------------------------------------------------------
# 3. Selecoes por quimica, nao por nome de atomo
# A nomenclatura de atomo varia entre CHARMM, Berger e Slipids; a topologia
# quimica nao. Criterios:
#   cabeca   = nitrogenio da colina + carbonos vizinhos
#   fosfato  = fosforo + oxigenios ligados
#   glicerol = oxigenios de ester restantes + carbonos adjacentes
#   cauda    = o complemento
# -----------------------------------------------------------------------------
select sel_wat,   resn HOH+WAT+SOL+TIP3+SPC+T3P
select sel_ions,  resn NA+CL+K+MG+CA+SOD+CLA+POT+ION
select sel_lipid, not (sel_wat or sel_ions) and not hydro and not polymer.protein

select lip_head, sel_lipid and (elem N or (elem C within 3.0 of (sel_lipid and elem N)))
select lip_phos, sel_lipid and (elem P or (elem O within 2.0 of (sel_lipid and elem P)))
select lip_glyc, sel_lipid and not (lip_head or lip_phos) and (elem O or (elem C within 1.8 of (sel_lipid and elem O and not lip_phos)))
select lip_tail, sel_lipid and not (lip_head or lip_phos or lip_glyc)
deselect

print("head/phos/glyc/tail/total:", cmd.count_atoms("lip_head"), cmd.count_atoms("lip_phos"), cmd.count_atoms("lip_glyc"), cmd.count_atoms("lip_tail"), cmd.count_atoms("sel_lipid"))
print("agua/ions:", cmd.count_atoms("sel_wat"), cmd.count_atoms("sel_ions"))

# -----------------------------------------------------------------------------
# 4. Lipideos em esferas, estratificados
# sphere_scale 0.55 e nao 1.0: em all-atom o spacefill cheio fecha a bicamada
# num bloco macico e a estratificacao de cor se perde. Subir para 1.0 se o
# objetivo for volume ocupado em vez de leitura das camadas.
# -----------------------------------------------------------------------------
show spheres, sel_lipid
set sphere_scale, 0.55, sel_lipid

color mad_tail_a, sel_lipid
color mad_glyc,   lip_glyc
color mad_phos,   lip_phos
color mad_head,   lip_head
set sphere_scale, 0.65, lip_head

# Folheto inferior em vermelho. Usa a coordenada z do centro de massa dos
# fosfatos como plano medio; assume normal da membrana em z.
python
zc = cmd.centerofmass("lip_phos")[2]
cmd.color("mad_tail_in", "lip_tail and z < %f" % zc)
python end

# Ions, se houver.
show spheres, sel_ions
set sphere_scale, 0.50, sel_ions
color purple, sel_ions and resn NA+SOD
color green,  sel_ions and resn CL+CLA

# -----------------------------------------------------------------------------
# 5. Agua como volume translucido
# Superficie sobre os oxigenios com raio inflado, em vez de mapa gaussiano:
# mais previsivel, sem a calibracao de nivel de isosuperficie.
# Desativada por padrao para nao pesar na navegacao; habilitar com
# 'enable_water' abaixo ou 'show surface, wat_o'.
# -----------------------------------------------------------------------------
select wat_o, sel_wat and elem O
alter wat_o, vdw=3.3
rebuild
set solvent_radius, 1.8
set surface_smooth_edges, 1
color mad_water, wat_o
set transparency, 0.62, wat_o
deselect

# Descomentar para exibir a agua (custa alguns segundos e deixa a cena pesada):
# show surface, wat_o

orient sel_lipid
zoom sel_lipid, 3

# =============================================================================
# 6. RENDER (nao executado; descomentar quando for exportar)
# O viewport nao aplica oclusao ambiente nem o modelo de especularidade;
# so o ray mostra o material real.
# =============================================================================
# bg_color white
# set opaque_background, 0
# set antialias, 5
# ray 3000, 2400
# png membrana.png, dpi=600
