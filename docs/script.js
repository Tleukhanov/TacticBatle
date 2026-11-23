// Lazy-load videos: set src only when the video enters the viewport.
const lazyVideos = document.querySelectorAll('video.lazy-video');
const videoObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      const v = e.target;
      const wrap = v.closest('.video-wrap');
      if (v.dataset.src && !v.src) {
        v.src = v.dataset.src;
        v.load();
        v.addEventListener('canplay', () => { if (wrap) wrap.classList.add('loaded'); }, { once: true });
        v.addEventListener('error', () => { if (wrap) wrap.classList.add('loaded'); }, { once: true });
      }
      videoObserver.unobserve(v);
    }
  });
}, { threshold: 0.25 });
lazyVideos.forEach(v => videoObserver.observe(v));

// Highlight nav link on scroll
const links = document.querySelectorAll('.nav a[href^="#"]');
const sections = [...links].map(a => document.querySelector(a.getAttribute('href'))).filter(Boolean);
const obs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    const id = '#' + e.target.id;
    const link = document.querySelector('.nav a[href="' + id + '"]');
    if (link) link.style.color = e.isIntersecting ? '#1fa855' : '';
  });
}, { threshold: 0.4 });
sections.forEach(s => obs.observe(s));
