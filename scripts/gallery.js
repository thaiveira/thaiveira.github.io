document.addEventListener('DOMContentLoaded', () => {
  const images = Array.from(document.querySelectorAll('.gallery img'));
  if (images.length === 0) return;

  let current = 0;

  const overlay = document.createElement('div');
  overlay.className = 'lightbox-overlay';
  overlay.innerHTML = `
    <button class="lightbox-close" aria-label="Fechar">×</button>
    <button class="lightbox-prev" aria-label="Anterior">←</button>
    <figure class="lightbox-figure">
      <img src="" alt="">
    </figure>
    <button class="lightbox-next" aria-label="Próxima">→</button>
    <div class="lightbox-counter"></div>
  `;
  document.body.appendChild(overlay);

  const imgEl = overlay.querySelector('.lightbox-figure img');
  const counterEl = overlay.querySelector('.lightbox-counter');
  const closeBtn = overlay.querySelector('.lightbox-close');
  const prevBtn = overlay.querySelector('.lightbox-prev');
  const nextBtn = overlay.querySelector('.lightbox-next');

  function show(index) {
    current = (index + images.length) % images.length;
    const src = images[current].getAttribute('src');
    imgEl.setAttribute('src', src);
    imgEl.setAttribute('alt', images[current].getAttribute('alt') || '');
    counterEl.textContent = `${current + 1} / ${images.length}`;
  }

  function open(index) {
    show(index);
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function close() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  images.forEach((img, index) => {
    img.setAttribute('tabindex', '0');
    img.setAttribute('role', 'button');
    img.addEventListener('click', () => open(index));
    img.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        open(index);
      }
    });
  });

  closeBtn.addEventListener('click', close);
  prevBtn.addEventListener('click', () => show(current - 1));
  nextBtn.addEventListener('click', () => show(current + 1));

  // clicar fora da imagem fecha
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) close();
  });

  document.addEventListener('keydown', (e) => {
    if (!overlay.classList.contains('is-open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });
});
