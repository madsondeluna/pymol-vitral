/* Indice dos presets: uma linha por preset, com fio separando.
 *
 * Cartao foi o formato errado aqui. Um cartao promete uma unidade autonoma,
 * e dez deles em grade competem com as figuras logo abaixo, que sao o
 * conteudo de verdade. A lista e um indice: densa, alinhada em colunas, e
 * some quando nao se esta procurando nada.
 *
 * A grade e derivada do proprio conteudo, e nao escrita a mao no markdown.
 * Duplicar os vinte cartoes no texto criaria uma segunda lista para manter em
 * sincronia com a primeira, e as duas divergiriam no primeiro preset novo.
 */
(function () {
  var base = (document.querySelector('link[href*="pure/tokens.css"]') || {}).href || "";
  var sprite = base.replace("tokens.css", "icons.svg");

  function monta() {
    document.querySelectorAll(".preset-index").forEach(function (g) { g.remove(); });

    var grupos = {};
    document.querySelectorAll('.md-typeset h3[id^="preset_"]').forEach(function (h) {
      var nome = h.id.split("-")[0];
      var familia = nome.indexOf("memb") > -1 ? "memb" : "prot";
      (grupos[familia] = grupos[familia] || []).push({ h: h, nome: nome });
    });

    Object.keys(grupos).forEach(function (familia) {
      var itens = grupos[familia];
      var ancora = itens[0].h;
      // a grade entra antes do primeiro preset da familia
      var grade = document.createElement("nav");
      grade.className = "preset-index";
      grade.setAttribute("aria-label", familia === "memb"
        ? "Membrane presets index" : "Protein presets index");

      itens.forEach(function (item, i) {
        var titulo = item.h.textContent.replace(/\s*¶\s*$/, "");
        var rotulo = titulo.replace(item.nome, "").trim();
        var p = item.h.nextElementSibling;
        var desc = p && p.tagName === "P" ? p.textContent.trim() : "";

        var a = document.createElement("a");
        a.className = "preset-row";
        a.href = "#" + item.h.id;
        a.innerHTML =
          '<span class="preset-row__num num">' + String(i + 1).padStart(2, "0") + "</span>" +
          '<span class="preset-row__cmd">' + item.nome + "</span>" +
          '<span class="preset-row__role">' + rotulo + "</span>" +
          '<span class="preset-row__desc">' + desc + "</span>" +
          '<svg class="icon icon-sm preset-row__go" aria-hidden="true">' +
            '<use href="' + sprite + '#chevron-right"/></svg>';
        grade.appendChild(a);
      });

      ancora.parentNode.insertBefore(grade, ancora);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", monta);
  } else {
    monta();
  }
  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(monta);
  }
})();
