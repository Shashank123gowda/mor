// Simple entrance animations for greeting on homepage
window.addEventListener('DOMContentLoaded', () => {
  const greeting = document.querySelector('.greeting');
  if (greeting) {
    greeting.style.opacity = '0';
    greeting.style.transform = 'translateY(-8px) scale(0.98)';
    requestAnimationFrame(() => {
      greeting.style.transition = 'all 800ms cubic-bezier(.19,1,.22,1)';
      greeting.style.opacity = '1';
      greeting.style.transform = 'translateY(0) scale(1)';
    });
  }
});