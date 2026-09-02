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

**A cabeça do lipídeo é definida por posição, não por química**
Nitrogênio só existe em colina e etanolamina, então PC e PE são as únicas
espécies com cabeça detectável quimicamente. Para o resto vale a posição: é
cabeça o que fica além do fosfato do próprio lipídeo, na direção do solvente.
A comparação é por molécula e não contra o z médio do folheto, porque com a
média as moléculas mais afundadas perdem a cabeça inteira.

Dois casos ficam de fora, e nenhum é falha de implementação:

- **Cabeça dobrada.** Se o glicerol da cabeça está voltado para dentro, ele não
  está além do fosfato e não é marcado. Aparece em estrutura não minimizada.
- **Cardiolipina.** O glicerol central fica entre os dois fosfatos, portanto
  mais interno que eles por construção química. Nenhum critério posicional a
  alcança.

Cobertura medida num sistema misto de 200 lipídeos com seis espécies mais
cardiolipina: 84 por cento com cabeça marcada, contra 29 por cento pelo
critério de nitrogênio sozinho.

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

**`preset_memb5` para com `Error: failed to get map state`**
O mapa gaussiano saiu vazio. `map_new` do tipo `gaussian` tira a largura da
gaussiana de cada átomo do fator B, e com a coluna B toda em 0.00 nada é
depositado na grade. É exatamente o que um PDB escrito por dinâmica molecular
traz. Nem `map_new` nem `isosurface` reclamam: o erro só aparece no histograma,
e a mensagem não diz nada sobre a causa. O pacote agora escreve um B temporário
e o devolve átomo a átomo, então isso está resolvido do lado dele. Num uso
manual de `map_new`, confira `cmd.get_extent("nome_do_mapa")`: uma caixa
unitária de -0.5 a 0.5 é mapa vazio.

**`mv_grayscale` não é um ajuste do PyMOL**
Não existe `set grayscale`. O comando converte cada cor nomeada em uso para a
luminância dela e devolve as originais depois. A consequência: um gradiente
aplicado por `spectrum`, como o de fator B do `preset_prot5`, usa cores sem
nome e continua colorido no teste. O log diz quantas ficaram de fora.

**A isosuperfície não aparece e o PyMOL diz `Invalid selection name`**
O `isosurface` não gerou triângulo nenhum, e objeto vazio não é registrado. O
nível não interceptou o mapa. O pacote deriva o nível do histograma justamente
para evitar isso; num uso manual, verifique a faixa com
`cmd.get_volume_histogram("map_wat", 8)`.

**`prot_water shell` retorna zero átomos**
O mais provável não é ausência de água, mas imagem periódica: a proteína está
numa borda da caixa e as águas vizinhas estão do outro lado. Corrija fora do
PyMOL, com `gmx trjconv -pbc mol -center`, antes de carregar.

**Carbono virou cálcio, oxigênio virou oganessônio**
O PDB não traz as colunas 77-78, onde mora o elemento, então o PyMOL adivinha
pelo nome do átomo, por prefixo de duas letras: `CA` vira cálcio, `CD` vira
cádmio, `OG` vira oganessônio, `SO` vira um símbolo que não existe. São nomes
normais de átomo em campo de força, então isso atinge qualquer saída de
dinâmica molecular escrita sem esse campo.

O estrago não é cosmético. O raio de van der Waals passa a ser o do elemento
errado, e com ele mudam spacefill, superfície e o mapa gaussiano; as seleções
por `elem C` e `elem O` que definem as camadas do lipídeo perdem esses átomos;
e a cor por elemento sai trocada. O `split` corrige na entrada e diz quantos
átomos ajustou. Fora dele, `mv_fix_elements` faz o mesmo em qualquer seleção.

**Cardiolipina classificada como cloreto**
`CL` é ao mesmo tempo o resname do cloreto e o da cardiolipina em CHARMM. Uma
lista de resíduos de íon que contenha `CL` manda as cardiolipinas inteiras para
`obj_ions`: num sistema real isso foram 28 moléculas, 6748 átomos, que sumiram
da membrana e viraram esferas de íon.

A propriedade que separa os dois é a contagem: íon é monoatômico, cardiolipina
tem 241 átomos por resíduo. O `split` mede isso antes de classificar e avisa no
log quando descarta um homônimo. A mesma armadilha vale para `CA`, `MG` e `ZN`
como nome de resíduo.

**Manchas quase pretas espalhadas pela cena**
É o interior das esferas cortadas pelo plano de recorte da câmera. Assim que a
câmera aproxima o bastante para cortar as esferas da frente, o PyMOL pinta a
superfície de corte com `ray_interior_color`, cujo padrão é `grey20`. Numa
bicamada densa isso lê como sujeira, ou como buraco na geometria.

As duas suspeitas óbvias estão erradas, e vale saber para não perder tempo:
subir `ambient` para 0.60 não muda nada, desligar `ray_shadow` não muda nada, e
nenhum átomo da cena tem cor escura. O teste que decide é pintar o próprio
ajuste de amarelo: se as manchas ficam amarelas, é ele.

O pacote usa `ray_interior_color, default` desde a versão 1.3.1, que faz o
corte herdar a cor do próprio átomo.

**Manchas pretas na superfície da proteína**
Oclusão ambiente saturada. `ambient_occlusion_scale` é a distância de
amostragem em angstrom, e o padrão 25 do PyMOL vale para esfera: as cavidades
de uma superfície molecular são mais largas que isso, ficam totalmente ocluídas
e saem pretas, em manchas que parecem defeito de geometria. Os níveis do pacote
amostram entre 8 e 22 desde a versão 1.1.0. Num uso manual, baixe a escala
antes de suspeitar da malha.

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

**Editei o código e nada mudou**
`run molviz.pml` de novo não recarrega. O `import` encontra o pacote já em
`sys.modules` e devolve o que está na memória, sem ler o disco e sem avisar. O
sintoma é uma edição que não surte efeito, ou um preset que imprime a mensagem
da versão anterior. Use `mv_reload`, que apaga as entradas do pacote em
`sys.modules` e importa de novo. Numa sessão antiga, que ainda não tem esse
comando, são duas linhas:

```
/import sys; [sys.modules.pop(m) for m in list(sys.modules) if m.startswith('pymol_molviz')]
run /caminho/pymol-molviz/molviz.pml
```

**Comentário no fim da linha quebra o comando**
`#` só é comentário quando abre a linha. Escrito depois de um comando, ele entra
no argumento: `set sphere_scale, 0.55 # nota` faz o PyMOL tentar converter
`0.55 # nota` em número e falhar.

**O script não encontra o arquivo**
Confirme o caminho de dentro do PyMOL:

```
import os, glob; print(glob.glob(os.path.expanduser("~/Downloads/*.pml")))
```
