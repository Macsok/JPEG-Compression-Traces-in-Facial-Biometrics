import assert from 'node:assert/strict';
import { test } from 'node:test';
import { spectrum } from '../app/static/engine-signal.mjs';

test('constant signals contain only DC; full-white DC reaches the scale maximum', () => {
  assert.deepEqual(spectrum(Array(8).fill(0)), Array(8).fill(0));
  const white = spectrum(Array(8).fill(255));
  assert.ok(Math.abs(white[0] - 1) < 1e-12);
  assert.ok(white.slice(1).every(value => value < 1e-12));
});

test('a cosine basis signal activates only its own frequency', () => {
  const samples = Array.from({length: 8}, (_, i) => Math.cos(Math.PI * (i + .5) * 3 / 8));
  const levels = spectrum(samples);
  const expected = Math.log1p(2) / Math.log1p(255 * Math.sqrt(8));
  assert.ok(Math.abs(levels[3] - expected) < 1e-12);
  assert.ok(levels.every((value, i) => i === 3 || value < 1e-12));
});
