// Tiny enhancement: highlight nav link on scroll
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
