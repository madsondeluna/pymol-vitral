# Adaptação

Pontos que provavelmente precisarão de edição ao mudar de sistema ou de force
field. Todos ficam no topo do arquivo correspondente, para que adaptar seja
editar um dicionário e não varrer o código.

## Cores

`PALETTE`, em `pymol_vitral/core.py`, define todas as cores em RGB explícito. A
definição é explícita, e não por nome do PyMOL, porque a percepção das cores
nomeadas varia com o gamma do display.

`CHAIN_CYCLE` e `TYPE_CYCLE` são os ciclos usados para cadeia e para espécie
lipídica.

## Nomenclatura de lipídeos

Em `pymol_vitral/membrane.py`:

- **`LIPID_RESN`**: resíduos reconhecidos como lipídeo
- **`INNER_LEAFLET_RESN`**: espécies tipicamente do folheto citoplasmático
- **`STEROL_RESN`**: esteroides
- **`CG_NAMES`**: nomes de partícula Martini para cabeça, fosfato e glicerol

As camadas em all-atom são definidas por critério químico e não por nome, e por
isso funcionam em CHARMM, Berger e Slipids sem edição:

- **cabeça**: nitrogênio quaternário ou amina, mais os carbonos vizinhos
- **fosfato**: fósforo, mais os oxigênios ligados
- **glicerol**: oxigênios de éster restantes, mais os carbonos adjacentes
- **cauda**: o complemento

A detecção de coarse-grained usa a razão átomos por resíduo lipídico, com corte
em 25: na Martini um POPC tem cerca de 12 partículas, em all-atom sem
hidrogênios tem 52.

## Escalas e grupos de resíduo

Em `pymol_vitral/protein.py`:

- **`KD`**: escala Kyte-Doolittle. Trocar por outra escala de hidrofobicidade é
  substituir este dicionário.
- **`BASIC`, `ACIDIC`, `POLAR`, `APOLAR`**: grupos de resíduo por carga. Mova
  `HIS` de `BASIC` para `POLAR` se preferir tratar a histidina como neutra em pH
  fisiológico.
- **`PEPTIDE_CUTOFF`**: número de resíduos abaixo do qual `prot_auto` escolhe o
  preset all-atom. Padrão 60.

## Descobrir a nomenclatura de um sistema desconhecido

```
@/caminho/pymol-vitral/examples/diagnostico.pml
```

Ele lista os resíduos mais frequentes, os nomes de átomo por resíduo e a razão
átomos por resíduo, que indica se o sistema é coarse-grained ou all-atom.

## Adicionar um preset

Presets são funções sem argumento obrigatório que seguem sempre a mesma
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

Depois adicione ao dicionário em `register()`, no fim do módulo. O `_reset()`
limpa representações e objetos derivados; o `_finish()` faz o rebuild que assa a
oclusão ambiente e enquadra a cena.
