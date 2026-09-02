# pymol-molviz

Visualization presets for PyMOL, aimed at molecular simulation systems: lipid
bilayers, proteins and peptides. The package splits the loaded system into
independent objects, applies a calibrated material and exposes numbered presets
that combine one representation per component.

Requirements: PyMOL 2.x, open-source or incentive. No external dependencies.

## Getting started

Three steps, in this order: load the system, load the protocol, apply a preset.
The order matters. The protocol splits whatever is already in the session, so
loading it before the structure leaves it with nothing to split.

### 1. Load the system

From the PyMOL command line. One line at a time: the Qt command bar is
single-line, so a multi-line paste becomes one command.

```
load /path/to/membrane.pdb
```

Anything PyMOL reads works the same way: a protein, a membrane, a solvated box,
a single frame of a trajectory.

```
load /path/to/protein.pdb
load /path/to/frame.pdb
```

From the PDB, without a local file:

```
fetch 4HHB, async=0
```

From the menu, `File > Open` does the same thing.

For a molecular dynamics frame, fix the periodic image before opening PyMOL,
or the protein may sit split across the box edges and the solvation shell comes
out empty:

```
gmx trjconv -s topol.tpr -f traj.xtc -o frame.pdb -pbc mol -center -dump 0
```

### 2. Load the protocol

```
run /path/to/pymol-molviz/molviz.pml
```

It splits the system into objects, prints the counts and applies a starting
preset: membrane if lipids are present, protein otherwise. The log names the
version and the directory it loaded from:

```
[molviz] v1.2.0 carregado de /path/to/pymol-molviz/pymol_molviz
```

Running it again always rereads from disk, so it doubles as the way to pick up
an edit. Add the same line to `~/.pymolrc` to have it in every session, and
then this step disappears: opening PyMOL is enough.

### 3. Apply a preset

```
preset_memb1
preset_prot1
```

Ten of each, listed below. Switching preset does not require reloading
anything: the split already happened, and each preset only changes
representation and colour.

Every preset takes an optional `paper` argument, the column width in
millimetres, which makes the scene come out ready for print in the same line:

```
preset_memb5 paper=85
```

Then colour, water and ions are adjustable without leaving the preset:

```
memb_color leaflet
memb_water off
prot_water shell, 6.0
```

And the figure goes out with:

```
mv_render figure.png, 2000, 1500, 300
```

### What the log tells you

Read the counts after step 2. `obj_lipid` with zero atoms means the residue
list does not cover the system; `examples/diagnostico.pml` lists what is
actually in the file. The protocol also reports two things it corrected on the
way in: atoms whose element it had to infer from the atom name, and residue
names that look like ions but are not.

## Install

No install step. Clone or unpack the repository anywhere; `molviz.pml` resolves
its own directory, so it works from any location.

Requirements: PyMOL 2.x or 3.x, open-source or incentive. No external
dependencies.

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

Every preset takes an optional `paper` argument: the column width in
millimetres. Without it the preset only sets representation and colour, so
lighting stays as it was and `mv_paper` can follow. With it the scene comes out
ready for print in one line: `preset_memb5 paper=85`.

| Command | Lipid | Ions | Water | Answers |
|---|---|---|---|---|
| `preset_memb1` | spheres at scale 0.55, coloured by chemical moiety | opaque spheres, scale 0.5 | translucent surface, 0.62 | general reading, layer organization |
| `preset_memb2` | spacefill at van der Waals radius, coloured by leaflet | real radius | translucent surface, 0.78 | occupied volume, the barrier |
| `preset_memb3` | sticks at radius 0.30, heads as spheres | opaque core plus solvation shell | translucent spheres | ion to polar head interaction |
| `preset_memb4` | translucent surface at 0.58 over thin sticks | spheres with inflated mesh | off | inserted peptide |
| `preset_memb5` | tails as a gaussian isosurface, heads as spheres | opaque spheres, scale 0.85 | gaussian field | illustration, large system |
| `preset_memb6` | lines at width 1.2, coloured by species, ambient occlusion off | dots | off | navigation, not a figure |
| `preset_memb7` | central slab in spacefill, coloured by moiety | spheres within 8 A of the slab | off | the bilayer interior, cross-section |
| `preset_memb8` | lipids contacting the protein in licorice, the rest ghosted | small spheres | off | annular lipids, protein-lipid contact |
| `preset_memb9` | one translucent surface per leaflet, phosphates as spheres | medium spheres | off | leaflet asymmetry and thickness |
| `preset_memb10` | dark tails as isosurface, light heads as spheres | off | off | reduction to one column, print in black and white |

`preset_memb5` is the lightest on large systems: it replaces thousands of tail
atoms with a single isosurface. Its isolevel is derived from the map histogram,
not fixed, and it falls back to thin sticks when the map comes out empty.
`preset_memb6` is for navigation, not for figures.

`preset_memb7` takes an `eixo` argument, 0 for x, 1 for y (default) and 2 for
z. The cut is a coordinate selection rather than the camera clipping plane, so
rotating the scene afterwards does not change what is exposed.

`preset_memb8` takes a radius in angstrom, default 5.0, and needs a protein in
the session. `preset_memb9` needs phosphates to find the midplane.

## Protein presets

| Command | Representation | Colour | Answers |
|---|---|---|---|
| `preset_prot1` | cartoon | secondary structure | domain topology |
| `preset_prot2` | cartoon under a translucent surface, 0.55 | secondary structure | binding site |
| `preset_prot3` | solid surface, solvent radius 1.4 | Kyte-Doolittle gradient | interaction face, amphipathicity |
| `preset_prot4` | spacefill at van der Waals radius | chain | complex architecture |
| `preset_prot5` | putty, thickness 0.6 to 3.5 | B-factor | flexibility |
| `preset_prot6` | all-atom sticks, radius 0.20 | formal charge | peptides |
| `preset_prot7` | cartoon plus water and ions within 4.0 A | secondary structure | MD box, solvation shell |
| `preset_prot8` | surface inside the solvent volume | formal charge | the simulated system as a whole |
| `preset_prot9` | surface, solvent field, twelve box edges | formal charge | box dimensions, solute to solvent ratio |
| `preset_prot10` | translucent cartoon, contact side chains in opaque licorice | secondary structure; contact carbons by residue class, rest by element | where two chains, or protein and ligand, touch |

`prot_auto` picks between `preset_prot1` and `preset_prot6` by residue count,
with the cutoff at 60. `preset_prot3` writes to the B-factor column;
`prot_restore_b` puts the original values back. `preset_prot5` reads the
B-factor column as deposited, which inverts on predicted models carrying pLDDT.

`preset_prot7` takes the shell radius, default 4.0.

`preset_prot10` takes the contact radius (default 4.5) and an optional chain
pair: `preset_prot10 cadeias=A C`. With more than two chains it shows the pair
with the largest contact and hides the rest, because a tetramer puts three
different interfaces in one frame and none of them reads. Surface is the wrong
representation for this question: a closed surface hides the contact area,
which sits between the two parts, and translucent it becomes a mass where
nothing is legible. Cartoon lets you see through, and licorice shows the side
chain, which is where the interaction happens.

`preset_prot9` draws the box from the extent of what is loaded, not from a
CRYST1 record, which MD frames often lack. It prints the dimensions for the
caption.

## Colour, water and ions

```
memb_color   moiety | leaflet | type | depth
memb_water   off | surface | spheres | field
memb_split
memb_protein
prot_color   ss | chain | charge | hydro | bfactor | rainbow
prot_water   off | shell | spheres | surface | field
prot_ions    off | spheres | vdw | halo | mesh | shell
prot_split
prot_auto
prot_restore_b
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
mv_reload
```

`mv_reload` re-imports the package from disk. Running `molviz.pml` again does
not: `import` finds the package already in `sys.modules` and hands back what is
in memory, so an edit appears to have no effect and a preset keeps printing the
previous version's message.

Ambient occlusion is on in every preset except `preset_memb6`, which turns it
off to keep navigation responsive. `ambient_occlusion_scale` is the sampling
distance in angstrom; PyMOL defaults to 25, which is calibrated for spheres and
saturates on a protein surface, where wide cavities come out as black patches.
The levels here sample between 8 and 22. Measured in both regimes: on membrane
spheres 12 and 25 render indistinguishably, and on a surface only the lower
value is usable. It does not reach cartoon: PyMOL bakes it
into sphere and surface geometry only, so a cartoon-based preset carries no
contact relief.

Each level sets several parameters at once. `mv_realism` overrides
`mv_shadows`, which overrides `mv_ao`: apply them from general to specific.
`mv_paper` takes a column width in millimetres, turns off cast shadows, sets
orthoscopic projection and prints the target resolution.

`mv_grayscale` rewrites every named colour in use to its own BT.601 luminance
and puts the originals back on the way out. PyMOL has no grayscale setting, so
a gradient applied by `spectrum` stays coloured and the log says how many
colours it could not reach.

## Gallery

[`docs/gallery.md`](docs/gallery.md) shows all twenty presets in three
orientations each, rendered from the two systems in this repository, with the
command line under every image.

```
load prot/4hhb.pdb
load memb/bilbo_preview.pdb
```

`prot/4hhb.pdb` is haemoglobin from the RCSB: four chains, four haems, 221
waters. `memb/bilbo_preview.pdb` is a mixed bilayer of six lipid species plus
cardiolipin, 64k atoms, written with a zero B column, which is what a molecular
dynamics frame looks like.

To rebuild the images after changing a preset:

```
/Applications/PyMOL.app/Contents/MacOS/PyMOL -cq tests/make_gallery.py
```

It skips what already exists in `docs/img`, so it can be interrupted and
resumed.

## Tests

```
/Applications/PyMOL.app/Contents/MacOS/PyMOL -cq tests/run_presets.py
```

Runs all twenty presets against four synthetic systems and checks that
B-factors survive, `gaussian_resolution` is restored, promised surfaces exist
and ambient occlusion lands where it should. See [`tests/`](tests/).

## Documentation

Written in Portuguese.

| File | Content |
|---|---|
| [`docs/passo-a-passo.md`](docs/passo-a-passo.md) | Numbered flows, command by command. Start here. |
| [`docs/gallery.md`](docs/gallery.md) | Every preset in three orientations, with the command that produces it. |
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
