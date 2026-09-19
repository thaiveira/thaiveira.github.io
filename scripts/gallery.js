document.addEventListener('DOMContentLoaded', () => {
  const images = Array.from(document.querySelectorAll('.gallery img'));
  if (images.length === 0) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const supportsViewTransitions = typeof document.startViewTransition === 'function';

  images.forEach((img) => {
    if (!img.hasAttribute('loading')) img.loading = 'lazy';
  });

  let current = 0;

  const dialog = document.createElement('dialog');
  dialog.className = 'lightbox-dialog';
    dialog.innerHTML = `
    <figure class="lightbox-figure">
      <img src="" alt="">
      <button class="lightbox-close" aria-label="Fechar">×</button>
      <button class="lightbox-prev" aria-label="Anterior">←</button>
      <button class="lightbox-next" aria-label="Próxima">→</button>
    </figure>
  `;
  document.body.appendChild(dialog);

  const imgEl = dialog.querySelector('.lightbox-figure img');
  document.body.appendChild(dialog);

  const imgEl = dialog.querySelector('.lightbox-figure img');
  const counterEl = dialog.querySelector('.lightbox-counter');
  const closeBtn = dialog.querySelector('.lightbox-close');
  const prevBtn = dialog.querySelector('.lightbox-prev');
  const nextBtn = dialog.querySelector('.lightbox-next');

  function preload(index) {
    if (index < 0 || index >= images.length) return;
    new Image().src = images[index].getAttribute('src');
  }

  function render(index) {
    current = (index + images.length) % images.length;
    const src = images[current].getAttribute('src');
    imgEl.setAttribute('src', src);
    imgEl.setAttribute('alt', images[current].getAttribute('alt') || '');
    counterEl.textContent = `${current + 1} / ${images.length}`;
    preload(current - 1);
    preload(current + 1);
  }

  function withViewTransition(fn) {
    if (supportsViewTransitions && !reduceMotion) {
      document.startViewTransition(fn);
    } else {
      fn();
    }
  }

  function open(index) {
    const thumb = images[index];
    thumb.style.viewTransitionName = 'lightbox-hero';

    withViewTransition(() => {
      render(index);
      imgEl.style.viewTransitionName = 'lightbox-hero';
      dialog.showModal();
    });

    setTimeout(() => { thumb.style.viewTransitionName = ''; }, 400);
  }

  function close() {
    const thumb = images[current];
    thumb.style.viewTransitionName = 'lightbox-hero';
    imgEl.style.viewTransitionName = 'lightbox-hero';

    withViewTransition(() => {
      dialog.close();
    });

    setTimeout(() => {
      thumb.style.viewTransitionName = '';
      imgEl.style.viewTransitionName = '';
    }, 400);
  }

  function show(index) {
    if (supportsViewTransitions && !reduceMotion) {
      document.startViewTransition(() => render(index));
    } else {
      render(index);
    }
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

  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) close();
  });

  dialog.addEventListener('cancel', (e) => {
    e.preventDefault();
    close();
  });

  document.addEventListener('keydown', (e) => {
    if (!dialog.open) return;
    if (e.key === 'ArrowLeft') show(current - 1);
    if (e.key === 'ArrowRight') show(current + 1);
  });

  let touchStartX = null;
  dialog.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].clientX;
  }, { passive: true });

  dialog.addEventListener('touchend', (e) => {
    if (touchStartX === null) return;
    const deltaX = e.changedTouches[0].clientX - touchStartX;
    const THRESHOLD = 40;
    if (deltaX > THRESHOLD) show(current - 1);
    else if (deltaX < -THRESHOLD) show(current + 1);
    touchStartX = null;
  }, { passive: true });
});