# Limitacoes e problemas comuns

Sao limitacoes do PyMOL, nao do pacote. Conhece-las evita perder tempo tentando
ajustar o que nao tem ajuste.

## Iluminacao

**A oclusao ambiente nao atua sobre cartoon.** Vale para esferas e superficies.
Numa cena com peptideo inserido, a membrana ganha sombra de contato e o cartoon
nao. Se a diferenca ficar evidente, represente o peptideo em `spheres` ou
`surface`.

**Sombras projetadas so aparecem apos `ray`.** Nunca no viewport. Calibrar "no
olho" pela tela nao funciona.

**A oclusao e assada na geometria.** Mudar sua escala exige `rebuild`. Os
comandos do pacote ja o executam; ajustes manuais nao.

**Transparencia nao projeta sombra**, por escolha do pacote. Com
`ray_transparency_shadows` ligado, uma superficie de agua cobrindo a caixa
escurece tudo por baixo e o resultado e uma cena uniformemente cinza.

## Estrutura e dados

**O PyMOL nao infere estrutura secundaria de particulas coarse-grained.** O
cartoon de um peptideo Martini vem sem helice nem folha. Em all-atom sem
registros HELIX/SHEET, `prot_split` roda `dss` automaticamente.

**`prot_color hydro` sobrescreve a coluna de fator B**, porque o PyMOL nao tem
campo generico por atomo para gradiente. Os valores originais sao salvos no
`prot_split`; `prot_restore_b` desfaz.

**`preset_prot5` interpreta a coluna B como desordem.** Em modelo predito ela
costuma carregar pLDDT, cuja escala significa o oposto: vermelho grosso
passaria a marcar regiao confiavel, nao flexivel. Confira a origem do arquivo.

**A separacao de folhetos assume a normal da membrana em z**, usando o centro
de massa dos fosfatos como plano medio. Em vesicula ou membrana com curvatura
acentuada o criterio nao vale.

**His fica no grupo basico** em `prot_color charge`, por convencao, embora
esteja majoritariamente neutra em pH 7,4.

## Memoria e desempenho

**`cmd.create` copia todos os estados.** A divisao em objetos duplica a memoria
de uma trajetoria inteira. Em MD longa, carregue apenas o frame de interesse
antes de rodar o pacote.

**Superficie de agua e cara.** Com dezenas de milhares de moleculas, tanto
`surface` quanto `field` levam dezenas de segundos e tornam a navegacao lenta.
Use `preset_memb6` para enquadrar a cena, e so depois aplique o preset final.

## Problemas comuns

**`Error: name conflicts with an object`**
Uma selecao nao pode ter o mesmo nome de um objeto ja carregado. O pacote usa
prefixos (`obj_`, `lip_`, `wat_`) justamente por isso. Se ocorrer com um objeto
seu, renomeie com `set_name antigo, novo`.

**A isosuperficie nao aparece e o PyMOL diz `Invalid selection name`**
O `isosurface` nao gerou triangulo nenhum, e objeto vazio nao e registrado. O
nivel nao interceptou o mapa. O pacote deriva o nivel do histograma justamente
para evitar isso; num uso manual, verifique a faixa com
`cmd.get_volume_histogram("map_wat", 8)`.

**`prot_water shell` retorna zero atomos**
O mais provavel nao e ausencia de agua, mas imagem periodica: a proteina esta
numa borda da caixa e as aguas vizinhas estao do outro lado. Corrija fora do
PyMOL, com `gmx trjconv -pbc mol -center`, antes de carregar.

**A tela fica coberta de pontos rosa**
Sao indicadores de selecao. O pacote desliga com
`set auto_show_selections, off`; num uso manual, rode o comando ou `deselect`.

**O material parece chapado**
Provavelmente a AO esta ligada mas invisivel por `ambient` baixo. Rode
`mv_ao medium`, que ajusta o balanco inteiro.

**Colar varias linhas na barra de comando nao funciona**
O campo da interface Qt e de linha unica: uma colagem multilinha vira um
comando so. Use `run` sobre um arquivo, ou `File > Run Script`.

**O script nao encontra o arquivo**
Confirme o caminho de dentro do PyMOL:

```
import os, glob; print(glob.glob(os.path.expanduser("~/Downloads/*.pml")))
```
