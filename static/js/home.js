// script.js
document.addEventListener('DOMContentLoaded', function () {
  // Mobile nav toggle
  const toggle = document.querySelector('.nav-toggle');
  const menu = document.getElementById('nav-menu');
  toggle && toggle.addEventListener('click', function () {
    const expanded = this.getAttribute('aria-expanded') === 'true';
    this.setAttribute('aria-expanded', String(!expanded));
    menu.classList.toggle('open');
  });

  // Set current year
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Reveal-on-scroll using IntersectionObserver
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (!prefersReducedMotion && 'IntersectionObserver' in window) {
    const reveals = document.querySelectorAll('.reveal');
    const io = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    }, { root: null, rootMargin: '0px 0px -10% 0px', threshold: 0.08 });

    reveals.forEach(el => io.observe(el));
  } else {
    // If reduced motion preferred or IO not supported, make elements visible
    document.querySelectorAll('.reveal').forEach(el => el.classList.add('in-view'));
  }

  // Optional: subtle parallax on mousemove for hero shapes (respect reduce motion)
  if (!prefersReducedMotion) {
    const hero = document.querySelector('.hero-visual');
    if (hero) {
      let raf = null;
      const state = {x:0, y:0};
      const onMove = (e) => {
        const rect = hero.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = (e.clientX - cx) / rect.width;
        const dy = (e.clientY - cy) / rect.height;
        state.x = dx;
        state.y = dy;
        if (!raf) raf = requestAnimationFrame(() => {
          // move the mock notes slightly using CSS transform - only transform property
          hero.querySelectorAll('.note-mock').forEach((el, idx) => {
            const depth = (idx + 1) * 4; // different parallax depth
            el.style.transform = `translate3d(${state.x * depth}px, ${-Math.abs(state.y) * depth}px, 0) rotate(${getRotation(el)}deg)`;
          });
          raf = null;
        });
      };
      const getRotation = (el) => {
        // extract original rotation value from style transform if present, fallback to 0
        const st = getComputedStyle(el).transform;
        // We won't parse matrix; just return 0 for simplicity and keep CSS rotations
        return 0;
      };
      hero.addEventListener('mousemove', onMove);
      hero.addEventListener('mouseleave', () => {
        // reset transforms
        hero.querySelectorAll('.note-mock').forEach(el => {
          el.style.transform = '';
        });
      });
    }
  }
});