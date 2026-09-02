# tests

Suíte de fumaça dos presets. Roda da raiz do repositório:

```
/Applications/PyMOL.app/Contents/MacOS/PyMOL -cq tests/run_presets.py
```

`make_systems.py` gera quatro sistemas sintéticos em `tests/systems/`, que o
runner recria a cada execução e o `.gitignore` mantém fora do repositório.
Nenhum é fisicamente realista: cada um existe para exercitar um caminho de
código que já quebrou.

| Sistema | Exercita |
|---|---|
| `membrana.pdb` | bicamada POPC com água e íons, 33 átomos por lipídeo, acima do corte de coarse-grained |
| `membrana_peptideo.pdb` | a mesma bicamada com uma hélice inserida, para `preset_memb8` e `memb_protein` |
| `peptideo.pdb` | peptídeo sem água e sem identificador de cadeia, que é onde moravam três dos defeitos |
| `complexo_solvatado.pdb` | duas cadeias com água e íons, para `preset_prot7`, `preset_prot9` e a interface do `preset_prot10` |

Os fatores B saem 0.00, como a dinâmica molecular escreve. Foi essa forma que
deixou o mapa gaussiano do `preset_memb5` vazio.

O runner não verifica aparência. Ele checa o que já falhou na prática: o preset
roda sem exceção, os fatores B voltam iguais aos que entraram,
`gaussian_resolution` é restaurada, o preset que promete isosuperfície cria o
objeto, e a oclusão ambiente fica ligada onde deve ficar.
