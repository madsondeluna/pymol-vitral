## Rebuilding the images

The figures above come from the two systems in this repository. To regenerate
them after changing a preset:

```
/Applications/PyMOL.app/Contents/MacOS/PyMOL -cq tests/make_gallery.py
```

It renders each preset from the side and from the top, in orthoscopic
projection, and skips what already exists in `docs/img`, so it can be
interrupted and resumed. Delete the files you want redone.

Framing is set per system, because the two shapes are different: a bilayer is
wide and thin and fills the width of the frame, so it takes a 6 A margin, while
a globular protein takes 3 A or it would come out too small to show detail.
Both use `complete=1`, which is what guarantees the geometry is not clipped.

## Tests

```
/Applications/PyMOL.app/Contents/MacOS/PyMOL -cq tests/run_presets.py
```

Runs all twenty presets against four synthetic systems and checks that
B-factors survive, `gaussian_resolution` is restored, promised surfaces exist
and ambient occlusion lands where it should. See `tests/` in the repository.


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

