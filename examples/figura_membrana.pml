# Figura de membrana para periodico, coluna simples.
# Pre-requisitos: estrutura carregada e molviz.pml executado.

preset_memb5
memb_color leaflet

# Enquadre a cena com o mouse antes de continuar. E o unico passo que nenhum
# script faz por voce, e o que mais afeta o resultado.

mv_paper 85
mv_extent obj_lipid

# Teste de impressao em preto e branco, antes do render final.
mv_grayscale 1
ray 1000, 750
mv_grayscale 0

mv_render figura_membrana.png, 1004, 753, 300
