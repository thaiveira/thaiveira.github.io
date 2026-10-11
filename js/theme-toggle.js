(function () {
  const STORAGE_KEY = 'thaiveira-theme';
  const root = document.documentElement;

  function applyTheme(theme) {
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else {
      root.removeAttribute('data-theme');
    }
  }

  let saved = null;
  try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) {}
  if (saved === 'dark') applyTheme('dark');

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.createElement('button');
    btn.className = 'theme-toggle';
    btn.setAttribute('aria-label', 'Alternar tema claro/escuro');
    btn.setAttribute('title', 'Alternar tema claro/escuro');

    const img = document.createElement('img');
    document.body.prepend(btn);
    btn.appendChild(img);

    function isDark() {
      return root.getAttribute('data-theme') === 'dark';
    }

    function syncIcon() {
      img.src = isDark() ? 'imagens/icon.png' : 'imagens/icon-moon.png';
      img.alt = isDark() ? 'Estrela em pixel art' : 'Lua crescente em pixel art';
    }

    syncIcon();

    btn.addEventListener('click', () => {
      const next = isDark() ? 'light' : 'dark';
      applyTheme(next);
      try { localStorage.setItem(STORAGE_KEY, next); } catch (e) {}
      syncIcon();
    });
  });
})();