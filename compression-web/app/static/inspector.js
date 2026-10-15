'use strict';

// The sample is an illustration; it never reads or changes prediction state.
(() => {
  const figure = document.querySelector('.inspection-figure');
  const carriage = document.getElementById('inspection-carriage');
  if (!figure || !carriage) return;
  const slider = document.getElementById('inspection-column');
  const play = document.getElementById('inspection-play');
  const readout = document.getElementById('inspection-readout');
  const columns = [...figure.querySelectorAll('[data-pixel-column]')];
  const [vx, vy] = carriage.dataset.vector.split(',').map(Number);
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let position = 0, target = 0, elapsed = 0, last = 0, frame = 0;
  let visible = false, paused = reduced.matches, interacting = false;

  function updateControl() {
    play.dataset.i18n = reduced.matches ? 'figureStill' : paused ? 'figurePlay' : 'figurePause';
    play.disabled = reduced.matches;
    play.textContent = t(play.dataset.i18n);
    play.setAttribute('aria-pressed', String(paused));
  }
  function draw() {
    carriage.setAttribute('transform', `translate(${position*14.4*vx} ${position*14.4*vy})`);
    const column = Math.max(0, Math.min(7, Math.round(position)));
    readout.value = `${String(column+1).padStart(2,'0')} / 08`;
    columns.forEach((el, index) => el.classList.toggle('is-active', index === column));
    if (!interacting) slider.value = String(column+1);
  }
  function tick(now) {
    frame = 0;
    if (!visible || document.hidden) { last = 0; return; }
    const dt = last ? Math.min((now-last)/1000, 1/30) : 0;
    last = now;
    const touring = !paused && !interacting && !reduced.matches;
    if (touring) { elapsed += dt; target = 3.5 - 3.5*Math.cos(elapsed*Math.PI/7); }
    position = reduced.matches ? target : position + (target-position)*(1-Math.exp(-dt/.18));
    if (Math.abs(position-target) < .001) position = target;
    draw();
    if (touring || position !== target) frame = requestAnimationFrame(tick);
  }
  function run() {
    if (!frame && visible && !document.hidden) { last = 0; frame = requestAnimationFrame(tick); }
  }
  slider.addEventListener('input', () => {
    paused = true; target = Number(slider.value)-1;
    updateControl(); run();
  });
  slider.addEventListener('focus', () => { interacting = true; });
  slider.addEventListener('blur', () => { interacting = false; run(); });
  play.addEventListener('click', () => {
    paused = !paused;
    elapsed = Math.acos(Math.max(-1,Math.min(1,1-position/3.5)))*7/Math.PI;
    updateControl(); run();
  });
  reduced.addEventListener('change', () => { paused = reduced.matches; updateControl(); run(); });
  new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    if (!visible && frame) { cancelAnimationFrame(frame); frame = 0; }
    run();
  }).observe(figure);
  document.addEventListener('visibilitychange', run);
  const syncTheme = () => { figure.dataset.theme = document.documentElement.dataset.theme; };
  new MutationObserver(syncTheme).observe(document.documentElement, {attributes:true, attributeFilter:['data-theme']});
  syncTheme(); updateControl(); draw();
})();
