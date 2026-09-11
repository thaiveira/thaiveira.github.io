// effects.js — pequenos toques "indie web" inspirados em ellesho.me/page
// Sem dependências externas. Seguro para rodar em qualquer página do site.

document.addEventListener('DOMContentLoaded', () => {
  const bg = document.querySelector('.background');
  if (bg) {
    const stars = ['✦', '✧', '⋆', '˚', '✶'];
    const total = window.innerWidth < 600 ? 10 : 18;
    for (let i = 0; i < total; i++) {
      const s = document.createElement('span');
      s.className = 'sparkle';
      s.textContent = stars[Math.floor(Math.random() * stars.length)];
      s.style.left = Math.random() * 100 + 'vw';
      s.style.top = Math.random() * 100 + 'vh';
      s.style.animationDelay = (Math.random() * 2) + 's';
      bg.appendChild(s);
    }
  }

  // rastro discreto de estrelinhas ao mover o mouse (throttled)
  let last = 0;
  window.addEventListener('mousemove', (e) => {
    const now = Date.now();
    if (now - last < 90) return;
    last = now;
    const star = document.createElement('span');
    star.className = 'cursor-star';
    star.textContent = '·';
    star.style.left = e.clientX + 'px';
    star.style.top = e.clientY + 'px';
    document.body.appendChild(star);
    setTimeout(() => star.remove(), 700);
  });
});
