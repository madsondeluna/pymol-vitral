# pymol-molviz

Visualization presets for PyMOL, aimed at molecular simulation systems: lipid
bilayers, proteins and peptides. The package splits the loaded system into
independent objects, applies a calibrated material and exposes numbered presets
that combine one representation per component.

Requirements: PyMOL 2.x, open-source or incentive. No external dependencies.

## Install

There is none. Clone or unpack the repository anywhere and, from inside PyMOL:

```
run /path/to/pymol-molviz/molviz.pml
```

The entry point resolves its own directory, so the repository works from any
location. Add the same line to `~/.pymolrc` to load it in every session.

## Usage

Load the structure first, then the package. It detects the system type and
applies an initial preset: membrane if lipids are present, protein otherwise.

```
load system.pdb
run /path/to/pymol-molviz/molviz.pml
preset_memb5
memb_color leaflet
mv_render figure.png, 2000, 1500, 300
```

## Objects

The split produces one object per component, each with its own enable dot in
the side panel.

| Object | Content |
|---|---|
| `obj_lipid` | lipids, subdivided into `lip_head`, `lip_phos`, `lip_glyc`, `lip_tail` |
| `obj_prot` | protein or peptide |
| `obj_wat` | water |
| `obj_ions` | ions |
| `obj_lig` | ligands |
| `obj_nucl` | nucleic acid |

## Membrane presets

| Command | Lipid | Ions | Water |
|---|---|---|---|
| `preset_memb1` | spheres, scale 0.55, colored by chemical moiety | opaque spheres, scale 0.5 | translucent surface, 0.62 |
| `preset_memb2` | spacefill at van der Waals radius, colored by leaflet | real radius | translucent surface, 0.78 |
| `preset_memb3` | sticks, radius 0.30, heads as spheres | opaque core plus solvation shell | translucent spheres |
| `preset_memb4` | translucent surface, 0.58, over thin sticks | spheres with inflated mesh | off |
| `preset_memb5` | tails as a gaussian isosurface, heads as spheres | opaque spheres, scale 0.85 | gaussian field |
| `preset_memb6` | lines, width 1.2, colored by species, no ambient occlusion | dots | off |

`preset_memb5` is the lightest on large systems: it replaces thousands of tail
atoms with a single isosurface. Its isolevel is derived from the map histogram,
not fixed. `preset_memb6` is for navigation, not for figures.

## Protein presets

| Command | Representation | Color |
|---|---|---|
| `preset_prot1` | cartoon | secondary structure |
| `preset_prot2` | cartoon under a translucent surface, 0.55 | secondary structure |
| `preset_prot3` | solid surface, solvent radius 1.4 | Kyte-Doolittle gradient |
| `preset_prot4` | spacefill at van der Waals radius | chain |
| `preset_prot5` | putty, thickness 0.6 to 3.5 | B-factor |
| `preset_prot6` | all-atom sticks, radius 0.20 | formal charge |
| `preset_prot7` | cartoon plus water and ions within 4.0 A | secondary structure |
| `preset_prot8` | surface inside the solvent volume | formal charge |

`prot_auto` picks between `preset_prot1` and `preset_prot6` by residue count,
with the cutoff at 60. `preset_prot3` writes to the B-factor column;
`prot_restore_b` puts the original values back. `preset_prot5` reads the
B-factor column as deposited, which inverts on predicted models carrying pLDDT.

## Color, water and ions

```
memb_color   moiety | leaflet | type | depth
memb_water   off | surface | spheres | field
prot_color   ss | chain | charge | hydro | bfactor | rainbow
prot_water   off | shell | spheres | surface | field
prot_ions    off | spheres | vdw | halo | mesh | shell
```

`shell` exists in the protein module only. It shows water or ions within a
radius of the solute, selected by `byres`.

## Material, lighting and output

```
mv_material
mv_ao          off | soft | medium | strong | extreme
mv_shadows     off | soft | medium | hard
mv_realism     studio | depth | dramatic | flat
mv_desaturate  0.18
mv_paper       85
mv_grayscale   1
mv_extent      obj_lipid
mv_render      figure.png, 2000, 1500, 300
```

Each level sets several parameters at once. `mv_realism` overrides
`mv_shadows`, which overrides `mv_ao`: apply them from general to specific.
`mv_paper` takes a column width in millimetres, turns off cast shadows, sets
orthoscopic projection and prints the target resolution.

## Other commands

`memb_split`, `memb_protein`, `memb_prepare`, `prot_split`, `prot_prepare`,
`prot_auto`, `prot_restore_b`.

## Documentation

Written in Portuguese.

| File | Content |
|---|---|
| [`docs/passo-a-passo.md`](docs/passo-a-passo.md) | Numbered flows, command by command. Start here. |
| [`docs/presets.md`](docs/presets.md) | What each preset shows and which question it answers. |
| [`docs/limitacoes.md`](docs/limitacoes.md) | PyMOL limitations and common problems, with cause and fix. |
| [`docs/adaptacao.md`](docs/adaptacao.md) | Where to edit for another force field, scale or new preset. |
| [`docs/decisoes.md`](docs/decisoes.md) | Design decisions and the constraint behind each one. |

## Layout

```
pymol-molviz/
├── molviz.pml              # entry point
├── pymol_molviz/
│   ├── __init__.py         # command registration and system detection
│   ├── core.py             # palette, material, lighting, output
│   ├── membrane.py         # six membrane presets
│   └── protein.py          # eight protein presets
├── docs/
├── examples/               # ready sequences, run with @
└── legacy/                 # earlier scripts, unmaintained
```

## Examples

```
@/path/to/pymol-molviz/examples/figura_membrana.pml
@/path/to/pymol-molviz/examples/figura_peptideo.pml
@/path/to/pymol-molviz/examples/md_solvatada.pml
@/path/to/pymol-molviz/examples/diagnostico.pml
```

`diagnostico.pml` draws nothing. It lists residue names, atom names and the
atoms per residue ratio, to identify the nomenclature of an unknown system.

## License

MIT.
