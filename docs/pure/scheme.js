/* Espelha o esquema do Material para a classe que a Pure Design usa.
 *
 * Os dois marcam o modo em lugares diferentes: o Material escreve
 * data-md-color-scheme no <body>, e o tokens.css da Pure declara o modo
 * escuro em :root.dark, ou seja, uma classe no <html>. Sem esta ponte o
 * escuro fica pela metade: o Material troca as cores dele e os tokens da
 * linguagem continuam nos valores do modo claro.
 *
 * A alternativa seria copiar os valores escuros para um bloco
 * [data-md-color-scheme="slate"], e isso duplicaria a paleta inteira fora do
 * tokens.css, que e a unica fonte de verdade dela.
 */
(function () {
  var raiz = document.documentElement;

  function sincroniza() {
    var escuro = document.body.getAttribute("data-md-color-scheme") === "slate";
    raiz.classList.toggle("dark", escuro);
  }

  function liga() {
    sincroniza();
    new MutationObserver(sincroniza).observe(document.body, {
      attributes: true,
      attributeFilter: ["data-md-color-scheme"]
    });
  }

  if (document.body) {
    liga();
  } else {
    document.addEventListener("DOMContentLoaded", liga);
  }

  // navigation.instant troca o body sem recarregar a pagina.
  if (window.document$ && window.document$.subscribe) {
    window.document$.subscribe(sincroniza);
  }
})();
