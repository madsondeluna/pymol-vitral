# Duas faces de um peptideo, para avaliar anfipaticidade.
# Pre-requisitos: peptideo carregado e vitral.pml executado.

# Face de carga
preset_prot6
orient obj_prot
mv_paper 85
mv_render peptideo_carga_frente.png, 1004, 753, 300

turn y, 180
mv_render peptideo_carga_verso.png, 1004, 753, 300

# Mesma orientacao, superficie de hidrofobicidade. Se as duas faces se separam
# nos dois esquemas, a anfipaticidade e real; se so aparece em um, investigue.
turn y, 180
preset_prot3
mv_render peptideo_hidro_frente.png, 1004, 753, 300

turn y, 180
mv_render peptideo_hidro_verso.png, 1004, 753, 300

prot_restore_b
