// Illustrative pixels and their spectrum; independent of the inference models.
export function samplePixel(column, row, detailed = false) {
  const smooth = 110 + 70 * Math.sin(column * .64 + row * .48);
  return Math.round(Math.max(0, Math.min(255,
    smooth + (detailed ? 65 * Math.cos(row * 2.7 + column * 1.8) : 0))));
}

export function columnSignal(position, detailed = false) {
  const left = Math.min(6, Math.floor(position)), mix = position - left;
  return Array.from({length: 8}, (_, row) =>
    samplePixel(left, row, detailed) * (1 - mix) + samplePixel(left + 1, row, detailed) * mix);
}

export function spectrum(samples) {
  return samples.map((_, frequency) => {
    const coefficient = samples.reduce((sum, value, i) =>
      sum + value * Math.cos(Math.PI * (i + .5) * frequency / 8), 0)
      * (frequency === 0 ? Math.sqrt(1 / 8) : Math.sqrt(2 / 8));
    return Math.log1p(Math.abs(coefficient)) / Math.log1p(255 * Math.sqrt(8));
  });
}
