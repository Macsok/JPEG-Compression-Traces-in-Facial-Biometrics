'use strict';

// Apply the saved theme before the page is painted, without depending on language.
(() => {
  let theme = 'light';
  try { if (localStorage.getItem('compression-theme') === 'dark') theme = 'dark'; } catch (_) { /* Storage is optional. */ }
  document.documentElement.dataset.theme = theme;
  document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('[data-theme-choice]');
    const updateButtons = () => buttons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.themeChoice === document.documentElement.dataset.theme));
    });
    updateButtons();
    buttons.forEach(button => button.addEventListener('click', () => {
      const selected = button.dataset.themeChoice === 'dark' ? 'dark' : 'light';
      document.documentElement.dataset.theme = selected;
      updateButtons();
      try { localStorage.setItem('compression-theme', selected); } catch (_) { /* Storage is optional. */ }
    }));
  });
})();
