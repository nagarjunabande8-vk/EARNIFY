document.addEventListener('DOMContentLoaded', () => {

  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen);
    });
  }

  document.querySelectorAll('.flash').forEach((el) => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.3s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 300);
    }, 4000);
  });

  const signupForm = document.querySelector('#signup-form');
  if (signupForm) {
    const password = document.querySelector('#password');
    const confirm = document.querySelector('#confirm_password');
    const hint = document.querySelector('#password-hint');

    const checkMatch = () => {
      if (!confirm.value) {
        hint.textContent = '';
        return true;
      }
      const matches = password.value === confirm.value;
      hint.textContent = matches ? '' : 'Passwords do not match yet.';
      return matches;
    };

    password.addEventListener('input', checkMatch);
    confirm.addEventListener('input', checkMatch);

    signupForm.addEventListener('submit', (e) => {
      if (!checkMatch()) {
        e.preventDefault();
      }
    });
  }


  const coverLetter = document.querySelector('#cover_letter');
  const counter = document.querySelector('#char-count');
  if (coverLetter && counter) {
    const updateCount = () => {
      counter.textContent = `${coverLetter.value.length} characters`;
    };
    coverLetter.addEventListener('input', updateCount);
    updateCount();
  }
});
