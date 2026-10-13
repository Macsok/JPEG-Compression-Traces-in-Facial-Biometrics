'use strict';

function renderHistogram(results) {
  const minimum = 10, maximum = 95, binWidth = 5;
  const count = (maximum - minimum) / binWidth;
  const bins = {JFIF: Array(count).fill(0), PPM: Array(count).fill(0)};
  let outside = 0, included = 0;
  for (const result of results) {
    if (!result.success || !Object.hasOwn(bins, result.format) || !Number.isFinite(result.predicted_quality)) continue;
    const quality = result.predicted_quality;
    if (quality < minimum || quality > maximum) { outside++; continue; }
    // Intervals [10,15), …, [90,95]; exactly 95 belongs to the final bin.
    bins[result.format][Math.min(count - 1, Math.floor((quality - minimum) / binWidth))]++;
    included++;
  }

  const svgNS = 'http://www.w3.org/2000/svg';
  function node(tag, attributes = {}, text) {
    const element = document.createElementNS(svgNS, tag);
    for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
    if (text !== undefined) element.textContent = text;
    return element;
  }
  const width = 900, height = 370;
  const left = 75, right = 25, top = 25, bottom = 70;
  const plotWidth = width - left - right, plotHeight = height - top - bottom;
  const peak = Math.max(1, ...bins.JFIF, ...bins.PPM);
  const rawStep = peak / 5;
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const step = Math.max(1, [1, 2, 5, 10].find(n => n * magnitude >= rawStep) * magnitude);
  const ceiling = Math.ceil(peak / step) * step;
  const x = quality => left + (quality - minimum) / (maximum - minimum) * plotWidth;
  const y = amount => top + plotHeight - amount / ceiling * plotHeight;
  const svg = node('svg', {viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-labelledby': 'histogram-title histogram-description'});
  svg.append(node('title', {id: 'histogram-title'}, t('histTitle')));
  svg.append(node('desc', {id: 'histogram-description'}, t('histDescription', {jfif: bins.JFIF.reduce((a, b) => a + b, 0), ppm: bins.PPM.reduce((a, b) => a + b, 0)})));

  for (let tick = 0; tick <= ceiling; tick += step) {
    svg.append(node('line', {x1: left, x2: width - right, y1: y(tick), y2: y(tick), class: 'histogram-grid'}));
    svg.append(node('text', {x: left - 12, y: y(tick) + 4, 'text-anchor': 'end'}, number(tick)));
  }
  for (let quality = minimum; quality <= maximum; quality += binWidth) {
    svg.append(node('text', {x: x(quality), y: height - bottom + 24, 'text-anchor': 'middle'}, quality));
  }
  for (let index = 0; index < count; index++) {
    const start = minimum + index * binWidth;
    const interval = `[${start}, ${start + binWidth}${index === count - 1 ? ']' : ')'}`;
    for (const format of ['JFIF', 'PPM']) {
      const value = bins[format][index];
      if (!value) continue;
      svg.append(node('rect', {
        x: x(start) + 1, y: y(value), width: plotWidth / count - 2,
        height: y(0) - y(value), class: `histogram-bar ${format.toLowerCase()}`,
      }));
    }
    // A shared hover target reports both counts, even when one bar covers another.
    const target = node('rect', {
      x: x(start), y: top, width: plotWidth / count, height: plotHeight,
      fill: 'transparent', tabindex: '0',
      'aria-label': t('histBin', {interval, jfif: bins.JFIF[index], ppm: bins.PPM[index]}),
    });
    target.append(node('title', {}, t('histBin', {interval, jfif: bins.JFIF[index], ppm: bins.PPM[index]})));
    svg.append(target);
  }
  svg.append(node('line', {x1: left, x2: left, y1: top, y2: y(0), class: 'histogram-axis'}));
  svg.append(node('line', {x1: left, x2: width - right, y1: y(0), y2: y(0), class: 'histogram-axis'}));
  svg.append(node('text', {x: left + plotWidth / 2, y: height - 14, 'text-anchor': 'middle', class: 'histogram-axis-label'}, t('histX')));
  svg.append(node('text', {transform: `translate(20 ${top + plotHeight / 2}) rotate(-90)`, 'text-anchor': 'middle', class: 'histogram-axis-label'}, t('histY')));
  if (!included) svg.append(node('text', {x: left + plotWidth / 2, y: top + plotHeight / 2, 'text-anchor': 'middle'}, t('histEmpty')));
  document.getElementById('histogram').replaceChildren(svg);
  document.getElementById('histogram-note').textContent = t('histNote', {count: included}) + (outside ? t('histOutside', {count: outside}) : '') + t('histHover');
}
