(() => {
  const LEFT_KEY = 'investor-masters-hide-left-sidebar';
  const RIGHT_KEY = 'investor-masters-hide-right-sidebar';

  function applyState() {
    const hideLeft = localStorage.getItem(LEFT_KEY) === '1';
    const hideRight = localStorage.getItem(RIGHT_KEY) === '1';
    document.body.classList.toggle('hide-left-sidebar', hideLeft);
    document.body.classList.toggle('hide-right-sidebar', hideRight);

    const leftBtn = document.querySelector('[data-sidebar-toggle="left"]');
    const rightBtn = document.querySelector('[data-sidebar-toggle="right"]');
    if (leftBtn) {
      leftBtn.classList.toggle('is-active', hideLeft);
      leftBtn.textContent = hideLeft ? '显示左栏' : '隐藏左栏';
    }
    if (rightBtn) {
      rightBtn.classList.toggle('is-active', hideRight);
      rightBtn.textContent = hideRight ? '显示右栏' : '隐藏右栏';
    }
  }

  function ensureControls() {
    if (document.querySelector('.sidebar-toggle-bar')) return;
    const bar = document.createElement('div');
    bar.className = 'sidebar-toggle-bar';
    bar.innerHTML = `
      <button class="sidebar-toggle-btn" data-sidebar-toggle="left" type="button">隐藏左栏</button>
      <button class="sidebar-toggle-btn" data-sidebar-toggle="right" type="button">隐藏右栏</button>
    `;
    document.body.appendChild(bar);
    bar.addEventListener('click', (event) => {
      const target = event.target;
      if (!(target instanceof HTMLButtonElement)) return;
      const side = target.dataset.sidebarToggle;
      if (side === 'left') {
        const next = !(localStorage.getItem(LEFT_KEY) === '1');
        localStorage.setItem(LEFT_KEY, next ? '1' : '0');
      }
      if (side === 'right') {
        const next = !(localStorage.getItem(RIGHT_KEY) === '1');
        localStorage.setItem(RIGHT_KEY, next ? '1' : '0');
      }
      applyState();
    });
  }

  function boot() {
    if (!document.body) return;
    ensureControls();
    applyState();
  }

  document.addEventListener('astro:page-load', boot);
  document.addEventListener('DOMContentLoaded', boot);
})();
