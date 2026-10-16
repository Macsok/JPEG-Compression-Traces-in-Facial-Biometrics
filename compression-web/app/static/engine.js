'use strict';

// A decorative instrument with one shared scan model, independent of inference.
(() => {
  const scene = document.getElementById('engine-scene');
  const camera = document.getElementById('engine-camera');
  const bridge = document.getElementById('engine-bridge');
  if (!scene || !camera || !bridge) return;
  const slider = document.getElementById('engine-column');
  const output = document.getElementById('engine-readout');
  const pause = document.getElementById('engine-pause');
  const toggle = document.getElementById('engine-toggle');
  const settings = document.getElementById('engine-settings');
  const dock = document.querySelector('.engine-dock');
  const presets = [...document.querySelectorAll('[data-engine-view]')];
  const columns = [...scene.querySelectorAll('[data-engine-column]')];
  const die = [...scene.querySelectorAll('[data-engine-die]')];
  const channels = [...scene.querySelectorAll('[data-engine-output]')];
  const packets = [...scene.querySelectorAll('[data-track]')].map(dot => {
    const path = document.getElementById(dot.dataset.track);
    return {dot, path, length:path.getTotalLength(), phase:Number(dot.dataset.phase)};
  });
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)');
  const [vx,vy] = bridge.dataset.vector.split(',').map(Number);
  let paused = false;
  try { paused = localStorage.getItem('compression-engine-paused') === 'true'; } catch (_) { /* Optional preference. */ }
  let position=0, target=0, phase=0, packetClock=0, frame=0, last=0, previousDraw=0, activeColumn=-1;
  let focus=0, focusTarget=0, pointerX=0, pointerY=0, x=0, y=0;
  let manual=false, sliderFocused=false, forceDraw=true;
  let compactZone=false;
  const views=[{x:0,y:0,s:1},{x:-100,y:30,s:1.12},{x:-65,y:-75,s:1.08}];
  let pose={...views[0]};
  let cameraTransform='';
  const follow=(a,b,dt,tau=.4)=>Math.abs(a-b)<.001 ? b : a+(b-a)*(1-Math.exp(-dt/tau));
  const isMoving=()=>!paused && !reduced.matches;

  function controls() {
    pause.dataset.i18n=reduced.matches ? 'figureStill' : paused ? 'enginePlay' : 'enginePause';
    pause.textContent=t(pause.dataset.i18n);
    pause.disabled=reduced.matches;
    pause.setAttribute('aria-pressed',String(paused || reduced.matches));
    dock.dataset.paused=String(!isMoving());
  }
  function syncTheme() { scene.dataset.theme=document.documentElement.dataset.theme; }
  function syncViewButtons() {
    presets.forEach((button,i)=>button.setAttribute('aria-pressed',String(i===Math.round(focusTarget))));
  }
  function pageFocus() {
    const workspaceTop=document.getElementById('workspace').getBoundingClientRect().top;
    const compact=innerWidth<=760 && workspaceTop<innerHeight*.85;
    if (compact!==compactZone) { compactZone=compact; collapse(compact); }
    if (reduced.matches || paused) return;
    const workspace=workspaceTop+scrollY;
    focusTarget=Math.max(0,Math.min(2,scrollY/Math.max(1,workspace*.85)));
    syncViewButtons(); run();
  }
  function collapse(value) {
    settings.hidden=value;
    toggle.setAttribute('aria-expanded',String(!value));
    toggle.textContent=value ? '+' : '−';
    toggle.dataset.i18nAria=toggle.dataset.i18nTitle=value ? 'engineShowControls' : 'engineHideControls';
    toggle.setAttribute('aria-label',t(toggle.dataset.i18nAria));
    toggle.title=t(toggle.dataset.i18nTitle);
  }
  function draw(dt) {
    const animate=isMoving();
    if (animate && !manual && !sliderFocused) {
      phase+=dt;
      target=3.5-3.5*Math.cos(phase*Math.PI/8);
    }
    position=reduced.matches ? target : follow(position,target,dt,.18);
    bridge.setAttribute('transform',`translate(${position*14.6*vx} ${position*14.6*vy})`);
    const current=Math.max(0,Math.min(7,Math.round(position)));
    if (current!==activeColumn || forceDraw) {
      activeColumn=current;
      output.value=`${String(current+1).padStart(2,'0')} / 08`;
      columns.forEach((el,i)=>el.classList.toggle('active',i===current));
      die.forEach((el,i)=>el.classList.toggle('active',i===current));
      channels.forEach((el,i)=>el.classList.toggle('active',i===current));
      if (!sliderFocused) slider.value=String(current+1);
    }
    focus=reduced.matches ? focusTarget : follow(focus,focusTarget,dt,.6);
    const lo=Math.min(1,Math.floor(focus)), mix=focus-lo;
    const desired={};
    for(const key of ['x','y','s']) desired[key]=views[lo][key]+(views[lo+1][key]-views[lo][key])*mix;
    x=reduced.matches ? 0 : follow(x,animate ? pointerX : 0,dt,.7);
    y=reduced.matches ? 0 : follow(y,animate ? pointerY : 0,dt,.7);
    pose=desired;
    const transform=`translate(${(pose.x+x).toFixed(3)} ${(pose.y+y).toFixed(3)}) translate(500 400) scale(${pose.s.toFixed(4)}) translate(-500 -400)`;
    if (transform!==cameraTransform) { camera.setAttribute('transform',transform); cameraTransform=transform; }
    if (animate) {
      // Pulses travel on actual etched paths; fade before either terminal.
      packetClock+=dt/2.8;
      for(const {dot,path,length,phase:offset} of packets) {
        const p=(packetClock+offset)%1;
        const point=path.getPointAtLength(p*length);
        dot.setAttribute('cx',point.x); dot.setAttribute('cy',point.y);
        dot.setAttribute('opacity',String(Math.sin(Math.PI*p)**2*.8));
      }
    } else if (forceDraw && reduced.matches) {
      packets.forEach(({dot})=>dot.setAttribute('opacity','0'));
    }
    forceDraw=false;
    return animate || Math.abs(position-target)>.001 || (!reduced.matches && Math.abs(focus-focusTarget)>.001) || Math.abs(x)>.01 || Math.abs(y)>.01;
  }
  function tick(now) {
    frame=0;
    if (document.hidden) { last=0; return; }
    // Cap ambient work to 30 fps, independently of a 120/144 Hz display.
    if (now-previousDraw<31 && !forceDraw) { frame=requestAnimationFrame(tick); return; }
    const dt=last ? Math.min((now-last)/1000,.1) : 1/30;
    previousDraw=now; last=now;
    if (draw(dt)) frame=requestAnimationFrame(tick);
  }
  function run() { if (!frame && !document.hidden) { last=0; frame=requestAnimationFrame(tick); } }
  slider.addEventListener('input',()=>{
    manual=true; target=Number(slider.value)-1;
    forceDraw=true; run();
  });
  slider.addEventListener('focus',()=>{ sliderFocused=true; });
  slider.addEventListener('blur',()=>{ sliderFocused=false; });
  pause.addEventListener('click',()=>{
    paused=!paused;
    if (!paused) { manual=false; phase=Math.acos(Math.max(-1,Math.min(1,1-position/3.5)))*8/Math.PI; }
    try { localStorage.setItem('compression-engine-paused',String(paused)); } catch (_) { /* Optional preference. */ }
    forceDraw=true; controls(); run();
  });
  toggle.addEventListener('click',()=>collapse(!settings.hidden));
  presets.forEach(button=>button.addEventListener('click',()=>{
    focusTarget=Number(button.dataset.engineView);
    // In reduced motion, an explicit camera choice changes immediately.
    forceDraw=true; run();
    syncViewButtons();
  }));
  addEventListener('pointermove',event=>{
    if (!isMoving() || !finePointer.matches) return;
    pointerX=(event.clientX/innerWidth-.5)*14;
    pointerY=(event.clientY/innerHeight-.5)*10;
  },{passive:true});
  addEventListener('scroll',pageFocus,{passive:true});
  addEventListener('resize',pageFocus,{passive:true});
  document.addEventListener('visibilitychange',()=>{
    if (document.hidden) { cancelAnimationFrame(frame); frame=0; last=0; }
    else { forceDraw=true; run(); }
  });
  reduced.addEventListener('change',()=>{
    pointerX=pointerY=0; focus=focusTarget=0; forceDraw=true;
    controls(); syncViewButtons(); run();
  });
  new MutationObserver(syncTheme).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
  syncTheme(); controls(); pageFocus(); draw(0); run();
})();
