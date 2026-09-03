/* Alternador de modo: um botao, dois estados.
 *
 * A linguagem tem quatro modos, mas uma pagina de documentacao nao e um
 * portfolio: aqui o controle disputa espaco com a busca e com o titulo, e
 * quatro pilulas empurram os dois. Claro e escuro cobrem o uso real, e o
 * icone diz para onde o clique leva, nao onde se esta.
 *
 * A classe vai no <html>, que e onde tokens.css declara os modos. O Material
 * segue sem saber de nada, porque cada variavel dele aponta para um token.
 * O modo tambem entra na URL, para um link abrir no modo em que foi copiado.
 */
(function () {
  var CHAVE = "pure-mode";
  var raiz = document.documentElement;
  var base = (document.querySelector('link[href*="pure/tokens.css"]') || {}).href || "";
  var sprite = base.replace("tokens.css", "icons.svg");

  function escuro() { return raiz.classList.contains("dark"); }

  function aplica(modo, guarda) {
    raiz.classList.toggle("dark", modo === "dark");
    if (guarda) {
      try { localStorage.setItem(CHAVE, modo); } catch (e) {}
      var url = new URL(location.href);
      if (modo === "dark") { url.searchParams.set("mode", "dark"); }
      else { url.searchParams.delete("mode"); }
      history.replaceState(null, "", url);
    }
    pinta();
  }

  function pinta() {
    var b = document.querySelector(".pure-mode-toggle");
    if (!b) return;
    var vaiPara = escuro() ? "Light" : "Dark";
    b.setAttribute("aria-label", "Switch to " + vaiPara.toLowerCase() + " mode");
    b.setAttribute("title", vaiPara);
    b.innerHTML = '<svg class="icon" aria-hidden="true"><use href="' +
                  sprite + "#" + (escuro() ? "sun" : "moon") + '"/></svg>';
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", getComputedStyle(raiz).getPropertyValue("--bg").trim());
  }

  function inicial() {
    var daUrl = new URLSearchParams(location.search).get("mode");
    if (daUrl !== null) return daUrl === "dark" ? "dark" : "";
    try {
      var salvo = localStorage.getItem(CHAVE);
      if (salvo !== null) return salvo === "dark" ? "dark" : "";
    } catch (e) {}
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "";
  }

  function monta() {
    var alvo = document.querySelector(".md-header__inner");
    if (!alvo) return;
    var antigo = alvo.querySelector(".pure-mode-toggle");
    if (antigo) antigo.remove();

    var b = document.createElement("button");
    b.type = "button";
    b.className = "pure-mode-toggle";
    b.addEventListener("click", function () {
      aplica(escuro() ? "" : "dark", true);
    });
    // Depois do link do repositorio, no fim da barra: e o ultimo controle da
    // direita, e antes da busca ele separava o titulo do campo.
    alvo.appendChild(b);
    pinta();
  }

  aplica(inicial(), false);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", monta);
  } else {
    monta();
  }
  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(monta);
  }
})();
