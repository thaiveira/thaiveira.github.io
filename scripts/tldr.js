(function () {
  document.addEventListener("DOMContentLoaded", function () {
    var alvo = document.getElementById("tldr");
    if (!alvo) return;

    var prompt =
      "Abra esta URL com busca na web e leia o artigo completo: " + location.href +
      "\n\nDepois de ler o conteúdo real do artigo resuma os pontos mais importantes e a conclusão.";

    var link = "https://claude.ai/new?q=" + encodeURIComponent(prompt);
    alvo.innerHTML = 'Clique <a href="' + link + '">aqui</a> se precisa de leitura via IA.';
  });
})();