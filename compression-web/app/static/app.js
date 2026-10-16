'use strict';
const $ = id => document.getElementById(id);
const supported = /\.(jpe?g|jfif|ppm|png|bmp|tiff?|webp)$/i;
let files = [], results = [], busy = false, stopped = false, ready = false;
let skipped = 0, phase = 'empty', currentFile = '', connection = 'connecting';
let maxBytes = 64 * 1024 * 1024, limits = null;
const panel = document.querySelector('.upload-panel');

function renderSelection() {
  panel.classList.toggle('has-files', files.length > 0);
  panel.classList.toggle('no-images', files.length === 0 && skipped > 0);
  $('upload-symbol').textContent = files.length ? '✓' : (skipped ? '!' : '↥');
  $('upload-title').textContent = t(files.length ? 'uploadSelected' : (skipped ? 'uploadEmpty' : 'uploadTitle'));
  $('upload-description').textContent = t(files.length ? 'uploadNext' : 'uploadDescription');
  const names = files.slice(0, 3).map(f => f.webkitRelativePath || f.name).join(' · ');
  $('upload-confirmation').textContent = files.length
    ? `${t('chosen', {count: files.length})} ${names}${files.length > 3 ? t('more', {count: files.length - 3}) : ''}${skipped ? ' · ' + t('skipped', {count: skipped}) : ''}`
    : (skipped ? t('unsupportedSelection', {count: skipped}) : '');
  if (busy) $('selection').textContent = stopped ? t('stopping') : `[${results.length + 1}/${files.length}] ${currentFile}`;
  else if (phase === 'complete') $('selection').textContent = t('completion', {state: t(stopped ? 'stopped' : 'finished'), done: results.length, total: files.length});
  else $('selection').textContent = phase === 'empty' ? t('noSelection') : t('chosen', {count: files.length}) + (skipped ? ' · ' + t('skipped', {count: skipped}) : '');
}
function renderStatus() {
  $('server-status').textContent = t(connection);
  $('limits').textContent = 'JPG · JFIF · PPM · PNG · BMP · TIFF · WebP' + (limits ? t('limits', {mb: limits.max_upload_mb, mp: limits.max_image_pixels / 1e6}) : '');
  $('start').disabled = busy || !ready || !files.length;
}
fetch('/health').then(r => { if (!r.ok) throw Error(); return r.json(); }).then(data => {
  ready = data.models_loaded; limits = data; maxBytes = data.max_upload_mb * 1024 * 1024;
  connection = ready ? 'ready' : 'connecting'; renderStatus();
}).catch(() => { connection = 'offline'; renderStatus(); });

function selectFiles(list) {
  if (busy) return;
  files = Array.from(list).filter(f => supported.test(f.name));
  skipped = list.length - files.length; phase = 'selected';
  renderSelection(); renderStatus(); $('progress').hidden = true;
}
$('files').addEventListener('change', e => selectFiles(e.target.files));
$('folder').addEventListener('change', e => selectFiles(e.target.files));
for (const name of ['dragenter', 'dragover']) panel.addEventListener(name, e => { e.preventDefault(); if (!busy) panel.classList.add('dragging'); });
panel.addEventListener('dragleave', () => panel.classList.remove('dragging'));
panel.addEventListener('drop', e => { e.preventDefault(); panel.classList.remove('dragging'); selectFiles(e.dataTransfer.files); });
$('stop').addEventListener('click', () => { stopped = true; $('stop').disabled = true; renderSelection(); });

function cell(row, text, className) {
  const td = document.createElement('td'); td.textContent = text;
  if (className) td.className = className;
  row.append(td); return td;
}
function errorText(result) { return t('error.' + (result.error_code || 'server'), result.error_params || {}); }
function confidenceText(result) {
  if (result.classification_diagnostics?.status === 'baseline') return t('confidenceUnsupported');
  // Avoid turning a near-one probability into a claim of absolute certainty.
  return result.confidence > 99.9 ? '>' + number(99.9, 1) + '%' : number(result.confidence, 3) + '%';
}
function addResult(result) {
  const row = document.createElement('tr');
  const name = cell(row, result.filename);
  if (result.thumbnail) {
    const img = document.createElement('img'); img.src = result.thumbnail; img.alt = ''; img.loading = 'lazy'; name.prepend(img);
  }
  if (!result.success) { const td = cell(row, errorText(result)); td.colSpan = 4; }
  else {
    const label = cell(row, ''); const badge = document.createElement('span');
    badge.className = 'badge ' + result.format.toLowerCase(); badge.textContent = result.format; label.append(badge);
    const confidence = cell(row, confidenceText(result));
    confidence.title = t('confidenceExplanation');
    if (result.classification_diagnostics?.status === 'baseline') {
      confidence.className = 'confidence-unsupported';
      const note = document.createElement('small'); note.textContent = t('confidenceBaseline'); confidence.append(note);
    }
    const quality = cell(row, number(result.predicted_quality, 1), 'quality');
    if (result.format === 'PPM') { const note = document.createElement('small'); note.textContent = t('ppmNote'); quality.append(note); }
    const details = document.createElement('details'); const summary = document.createElement('summary'); summary.textContent = t('featureDetails');
    const pre = document.createElement('pre');
    pre.textContent = `${t('probabilities')}:\n${JSON.stringify(result.probabilities, null, 2)}\n\n${t('indicators')}:\n${JSON.stringify(result.indicators, null, 2)}\n\n${t('width')}: ${result.width}\n${t('height')}: ${result.height}\n${t('duration')}: ${number(result.elapsed_seconds, 3)}`;
    if (result.classification_diagnostics) pre.textContent += `\n\n${t('confidenceDiagnostics')}:\n${JSON.stringify(result.classification_diagnostics, null, 2)}`;
    details.append(summary, pre); cell(row, '').append(details);
  }
  $('results').append(row);
}
function renderSummary() {
  const ok = results.filter(r => r.success);
  $('summary').textContent = t('summary', {total: results.length, jfif: ok.filter(r => r.format === 'JFIF').length, ppm: ok.filter(r => r.format === 'PPM').length, errors: results.length - ok.length});
  renderHistogram(results);
}
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
async function predict(file) {
  if (file.size >= maxBytes) return {success: false, error_code: 'upload_limit'};
  for (let attempt = 0; attempt < 150; attempt++) {
    const form = new FormData(); form.append('file', file);
    const response = await fetch('/api/predict', {method: 'POST', body: form});
    if (response.status === 429 && !stopped) { await pause(2000); continue; }
    let data;
    try { data = await response.json(); } catch (_) { return {success: false, error_code: 'http', error_params: {status: response.status}}; }
    if (!response.ok) return {success: false, error_code: data.error_code || 'http', error_params: data.error_params || {status: response.status}};
    return data;
  }
  return {success: false, error_code: 'busy'};
}
$('start').addEventListener('click', async () => {
  if (busy || !ready || !files.length) return;
  busy = true; stopped = false; results = []; phase = 'running';
  $('results').replaceChildren(); $('results-section').hidden = false; renderSummary(); renderStatus();
  $('files').disabled = true; $('folder').disabled = true;
  $('stop').hidden = false; $('stop').disabled = false;
  $('progress').hidden = false; $('progress').max = files.length; $('progress').value = 0;
  try {
    for (const file of files) {
      if (stopped) break;
      currentFile = file.webkitRelativePath || file.name; renderSelection();
      let result;
      try { result = await predict(file); } catch (_) { result = {success: false, error_code: 'network'}; }
      result.filename = currentFile; results.push(result); addResult(result); renderSummary(); $('progress').value = results.length;
    }
  } finally {
    busy = false; phase = 'complete'; $('files').disabled = false; $('folder').disabled = false; $('stop').hidden = true;
    renderStatus(); renderSelection();
  }
});
function download(content, type, extension) {
  const url = URL.createObjectURL(new Blob([content], {type}));
  const link = document.createElement('a'); link.href = url; link.download = `compression-results.${extension}`; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function exportResults() { return results.map(({thumbnail, error, ...r}) => r.success ? r : {...r, error: errorText(r)}); }
$('json').addEventListener('click', () => download(JSON.stringify(exportResults(), null, 2), 'application/json', 'json'));
$('csv').addEventListener('click', () => {
  const features = [...new Set(results.flatMap(r => Object.keys(r.indicators || {})))];
  const columns = ['filename', 'success', 'format', 'confidence', 'confidence_status', 'kernel_contribution_bound', 'predicted_quality', 'probability_JFIF', 'probability_PPM', 'width', 'height', 'elapsed_seconds', 'error', ...features];
  const quote = value => { let s = String(value ?? ''); if (/^[\s]*[=+\-@]/.test(s)) s = "'" + s; return '"' + s.replaceAll('"', '""') + '"'; };
  const rows = exportResults().map(r => ({...r, ...r.indicators, confidence_status: r.classification_diagnostics?.status, kernel_contribution_bound: r.classification_diagnostics?.kernel_contribution_bound, probability_JFIF: r.probabilities?.JFIF, probability_PPM: r.probabilities?.PPM}));
  download('\uFEFF' + [columns.map(quote).join(','), ...rows.map(r => columns.map(c => quote(r[c])).join(','))].join('\r\n'), 'text/csv;charset=utf-8', 'csv');
});
function refreshLanguage() {
  translatePage(); renderStatus(); renderSelection();
  $('results').replaceChildren(); results.forEach(addResult); renderSummary();
}
document.querySelectorAll('[data-language]').forEach(button => button.addEventListener('click', () => {
  language = button.dataset.language === 'pl' ? 'pl' : 'en';
  try { localStorage.setItem('compression-language', language); } catch (_) { /* Preference is optional. */ }
  refreshLanguage();
}));
refreshLanguage();
