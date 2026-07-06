document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.category-btn');
  const grids = document.querySelectorAll('.services-grid');

  function switchTab(tab) {
    tabs.forEach((t) => t.classList.remove('active'));
    tab.classList.add('active');

    const target = tab.dataset.category;
    grids.forEach((grid) => {
      grid.style.display = 'none';
      grid.classList.remove('active');
    });

    if (!target) return;

    const activeGrid = document.getElementById(target);
    if (activeGrid) {
      activeGrid.style.display = 'grid';
      setTimeout(() => activeGrid.classList.add('active'), 10);
    }
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => switchTab(tab));
  });

  const cards = document.querySelectorAll('.service-card');
  cards.forEach((card) => {
    const inner = card.querySelector('.flip-card-inner');
    if (!inner) return;

    card.addEventListener('mouseenter', () => {
      if (!inner.classList.contains('clicked')) {
        inner.classList.add('flipping');
        inner.style.transform = 'perspective(1000px) rotateY(180deg)';
      }
    });

    card.addEventListener('mouseleave', () => {
      if (!inner.classList.contains('clicked')) {
        inner.classList.remove('flipping');
        inner.style.transform = 'perspective(1000px) rotateY(0deg)';
      }
    });

    card.addEventListener('click', () => {
      inner.classList.toggle('clicked');
      if (inner.classList.contains('clicked')) {
        inner.classList.add('flipping');
        inner.style.transform = 'perspective(1000px) rotateY(180deg)';
      } else {
        inner.classList.remove('flipping');
        inner.style.transform = 'perspective(1000px) rotateY(0deg)';
      }
    });
  });

  const firstTab = document.querySelector('.category-btn.active');
  if (firstTab) switchTab(firstTab);
});
