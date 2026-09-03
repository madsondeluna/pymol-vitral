/* Reescreve o rotulo dos presets no sumario da esquerda.
 *
 * O titulo de cada preset carrega comando e descricao na mesma frase, o que
 * serve ao corpo do texto e nao a uma coluna de 240px: "preset_prot1 cartoon
 * by secondary structure" quebra em tres linhas, e vinte itens assim viram
 * uma parede sem hierarquia.
 *
 * Aqui os dois se separam: o comando em mono, que e o que se procura, e a
 * descricao em uma linha truncada, que e o que confirma a escolha. O titulo
 * na pagina nao muda.
 */
(function () {
  function encurta() {
    document.querySelectorAll('.md-nav__link[href*="#preset_"]').forEach(function (a) {
      if (a.querySelector(".toc-cmd")) return;
      var alvo = a.querySelector(".md-ellipsis") || a;
      var texto = alvo.textContent.trim();
      // O comando vem num <code>, entao o texto sai colado ao que segue:
      // "preset_prot1cartoon by secondary structure". O espaco e opcional.
      var m = texto.match(/^(preset_(?:memb|prot)\d+)\s*(.*)$/);
      if (!m) return;
      alvo.innerHTML = '<span class="toc-cmd">' + m[1] + "</span>" +
                       '<span class="toc-desc">' + m[2] + "</span>";
      a.classList.add("toc-preset");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", encurta);
  } else {
    encurta();
  }
  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(encurta);
  }
})();
