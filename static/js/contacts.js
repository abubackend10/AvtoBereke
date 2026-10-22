document.querySelectorAll('.map--loading').forEach(map => {
  const iframe = map.querySelector('iframe');
  if (!iframe) return;

  iframe.addEventListener('load', () => map.classList.remove('map--loading'), { once: true });
});
