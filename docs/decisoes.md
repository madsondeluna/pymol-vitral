# Decisões de projeto

Cada decisão abaixo existe por uma restrição concreta do PyMOL ou dos formatos
de simulação, não por preferência.

## Seleções por critério químico, não por nome de átomo

A nomenclatura de átomos varia entre CHARMM, Berger, Slipids e Martini; a
topologia não varia. As camadas de um lipídeo são definidas por elemento e
conectividade, e o módulo cai para nomes Martini apenas quando detecta um
sistema coarse-grained pela razão átomos por resíduo.

## Objetos, não seleções

Seleção serve para aplicar comandos; objeto tem ponto de enable próprio no
painel lateral. A divisão em objetos é o que permite mostrar e ocultar
componentes com um clique, sem redigitar nada.

## Nível de isosuperfície derivado do histograma

Um nível fixo falha em silêncio quando a resolução gaussiana muda: o
`isosurface` não gera triângulo nenhum, e objeto vazio não é registrado pelo
PyMOL. O nível de `preset_memb5` sai do histograma do mapa recém-criado.

## Fatores B preservados

Colorir por hidrofobicidade exige escrever na coluna B, já que o PyMOL não tem
campo genérico por átomo para gradiente contínuo. Os valores originais são
salvos no split, e `prot_restore_b` os devolve.

## Um material, vários níveis

Oclusão ambiente e sombra projetada competem pelo mesmo orçamento de luz. Subir
uma sem baixar a outra produz uma cena lavada, então os comandos de ajuste
alteram vários parâmetros em conjunto em vez de expor cada um isoladamente.
