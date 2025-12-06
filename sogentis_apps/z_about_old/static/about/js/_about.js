function toggleDetail(id) {
  const card = document.getElementById(id).closest('.about-card');
  const detail = document.getElementById(id);
  const indicator = card.querySelector('.toggle-indicator');

  card.classList.toggle('open');
  if (detail.style.display === 'block') {
    detail.style.display = 'none';
    indicator.textContent = '+';
  } else {
    detail.style.display = 'block';
    indicator.textContent = '−';
  }
}
