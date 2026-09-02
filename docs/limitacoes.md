# Limitações e problemas comuns

São limitações do PyMOL, não do pacote. Conhecê-las evita perder tempo tentando
ajustar o que não tem ajuste.

## Iluminação

**A oclusão ambiente não atua sobre cartoon.** Vale para esferas e superfícies.
Numa cena com peptídeo inserido, a membrana ganha sombra de contato e o cartoon
não. Se a diferença ficar evidente, represente o peptídeo em `spheres` ou
`surface`.

**Sombras projetadas só aparecem após `ray`.** Nunca no viewport. Calibrar no
olho, pela tela, não funciona.

**A oclusão é assada na geometria.** Mudar sua escala exige `rebuild`. Os
comandos do pacote já o executam; ajustes manuais não.

**Transparência não projeta sombra**, por escolha do pacote. Com
`ray_transparency_shadows` ligado, uma superfície de água cobrindo a caixa
escurece tudo por baixo e o resultado é uma cena uniformemente cinza.

## Estrutura e dados

**O PyMOL não infere estrutura secundária de partículas coarse-grained.** O
cartoon de um peptídeo Martini vem sem hélice nem folha. Em all-atom sem
registros HELIX e SHEET, `prot_split` roda `dss` automaticamente.

**`prot_color hydro` sobrescreve a coluna de fator B**, porque o PyMOL não tem
campo genérico por átomo para gradiente. Os valores originais são salvos no
`prot_split`; `prot_restore_b` desfaz.

**`preset_prot5` interpreta a coluna B como desordem.** Em modelo predito ela
costuma carregar pLDDT, cuja escala significa o oposto: vermelho grosso passaria
a marcar região confiável, não flexível. Confira a origem do arquivo.

**A separação de folhetos assume a normal da membrana em z**, usando o centro de
massa dos fosfatos como plano médio. Em vesícula ou membrana com curvatura
acentuada o critério não vale.

**His fica no grupo básico** em `prot_color charge`, por convenção, embora esteja
majoritariamente neutra em pH 7,4.

## Memória e desempenho

**`cmd.create` copia todos os estados.** A divisão em objetos duplica a memória
de uma trajetória inteira. Em MD longa, carregue apenas o frame de interesse
antes de rodar o pacote.

**Superfície de água é cara.** Com dezenas de milhares de moléculas, tanto
`surface` quanto `field` levam dezenas de segundos e tornam a navegação lenta.
Use `preset_memb6` para enquadrar a cena, e só depois aplique o preset final.

## Problemas comuns

**`Error: name conflicts with an object`**
Uma seleção não pode ter o mesmo nome de um objeto já carregado. O pacote usa
prefixos (`obj_`, `lip_`, `wat_`) justamente por isso. Se ocorrer com um objeto
seu, renomeie com `set_name antigo, novo`.

**A isosuperfície não aparece e o PyMOL diz `Invalid selection name`**
O `isosurface` não gerou triângulo nenhum, e objeto vazio não é registrado. O
nível não interceptou o mapa. O pacote deriva o nível do histograma justamente
para evitar isso; num uso manual, verifique a faixa com
`cmd.get_volume_histogram("map_wat", 8)`.

**`prot_water shell` retorna zero átomos**
O mais provável não é ausência de água, mas imagem periódica: a proteína está
numa borda da caixa e as águas vizinhas estão do outro lado. Corrija fora do
PyMOL, com `gmx trjconv -pbc mol -center`, antes de carregar.

**A tela fica coberta de pontos rosa**
São indicadores de seleção. O pacote desliga com
`set auto_show_selections, off`; num uso manual, rode o comando ou `deselect`.

**O material parece chapado**
Provavelmente a oclusão ambiente está ligada mas invisível por `ambient` baixo.
Rode `mv_ao medium`, que ajusta o balanço inteiro.

**Colar várias linhas na barra de comando não funciona**
O campo da interface Qt é de linha única: uma colagem multilinha vira um comando
só. Copie uma linha por vez, ou salve o bloco num arquivo e use `run` sobre ele,
`@arquivo.pml` ou `File > Run Script`.

**Comentário no fim da linha quebra o comando**
`#` só é comentário quando abre a linha. Escrito depois de um comando, ele entra
no argumento: `set sphere_scale, 0.55 # nota` faz o PyMOL tentar converter
`0.55 # nota` em número e falhar.

**O script não encontra o arquivo**
Confirme o caminho de dentro do PyMOL:

```
import os, glob; print(glob.glob(os.path.expanduser("~/Downloads/*.pml")))
```
