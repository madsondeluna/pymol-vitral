# Adaptacao

Pontos que provavelmente precisarao de edicao ao mudar de sistema ou de force
field. Todos ficam no topo do arquivo correspondente, para que adaptar seja
editar um dicionario e nao varrer o codigo.

## Cores

`PALETTE`, em `pymol_molviz/core.py`, define todas as cores em RGB explicito.
A definicao e explicita, e nao por nome do PyMOL, porque a percepcao das cores
nomeadas varia com o gamma do display.

`CHAIN_CYCLE` e `TYPE_CYCLE` sao os ciclos usados para cadeia e para especie
lipidica.

## Nomenclatura de lipideos

Em `pymol_molviz/membrane.py`:

- `LIPID_RESN` — residuos reconhecidos como lipideo
- `INNER_LEAFLET_RESN` — especies tipicamente do folheto citoplasmatico
- `STEROL_RESN` — esteroides
- `CG_NAMES` — nomes de particula Martini para cabeca, fosfato e glicerol

As camadas em all-atom sao definidas por criterio quimico e nao por nome, e por
isso funcionam em CHARMM, Berger e Slipids sem edicao:

- **cabeca** — nitrogenio quaternario ou amina, mais os carbonos vizinhos
- **fosfato** — fosforo, mais os oxigenios ligados
- **glicerol** — oxigenios de ester restantes, mais os carbonos adjacentes
- **cauda** — o complemento

A deteccao de coarse-grained usa a razao atomos por residuo lipidico, com corte
em 25: na Martini um POPC tem cerca de 12 particulas, em all-atom sem
hidrogenios tem 52.

## Escalas e grupos de residuo

Em `pymol_molviz/protein.py`:

- `KD` — escala Kyte-Doolittle. Trocar por outra escala de hidrofobicidade e
  substituir este dicionario.
- `BASIC`, `ACIDIC`, `POLAR`, `APOLAR` — grupos de residuo por carga. Mova
  `HIS` de `BASIC` para `POLAR` se preferir tratar a histidina como neutra em
  pH fisiologico.
- `PEPTIDE_CUTOFF` — numero de residuos abaixo do qual `prot_auto` escolhe o
  preset all-atom. Padrao 60.

## Descobrir a nomenclatura de um sistema desconhecido

```
@/caminho/pymol-molviz/examples/diagnostico.pml
```

Ele lista os residuos mais frequentes, os nomes de atomo por residuo e a razao
atomos por residuo, que indica se o sistema e coarse-grained ou all-atom.

## Adicionar um preset

Presets sao funcoes sem argumento obrigatorio que seguem sempre a mesma
estrutura:

```python
def preset9():
    """Docstring: o que mostra e a que pergunta responde."""
    if not prepare():
        return
    _reset()
    # ... representacoes e cor ...
    _finish("preset_memb9: descricao curta")
```

Depois adicione ao dicionario em `register()`, no fim do modulo. O `_reset()`
limpa representacoes e objetos derivados; o `_finish()` faz o rebuild que assa
a oclusao ambiente e enquadra a cena.
