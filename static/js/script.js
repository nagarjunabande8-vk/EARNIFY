document.addEventListener('DOMContentLoaded', () => {

  /* ---------- Mobile Nav Toggle ---------- */
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', isOpen);
    });
    document.addEventListener('click', (e) => {
      if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
        navLinks.classList.remove('open');
        navToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---------- Flash Message Auto-Dismiss ---------- */
  document.querySelectorAll('.flash').forEach((el) => {
    const closeBtn = el.querySelector('.flash-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(-8px)';
        setTimeout(() => el.remove(), 200);
      });
    }
    setTimeout(() => {
      if (el.parentNode) {
        el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        el.style.opacity = '0';
        el.style.transform = 'translateY(-8px)';
        setTimeout(() => el.remove(), 300);
      }
    }, 5000);
  });

  /* ---------- Password Show/Hide Toggle ---------- */
  document.querySelectorAll('.password-toggle').forEach((btn) => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input');
      if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
      } else {
        input.type = 'password';
        btn.textContent = '👁';
      }
    });
  });

  /* ---------- Signup Form Validation ---------- */
  const signupForm = document.querySelector('#signup-form');
  if (signupForm) {
    const password = document.querySelector('#password');
    const confirm = document.querySelector('#confirm_password');
    const hint = document.querySelector('#password-hint');

    const checkMatch = () => {
      if (!confirm || !confirm.value) {
        if (hint) hint.textContent = '';
        return true;
      }
      const matches = password.value === confirm.value;
      if (hint) {
        hint.textContent = matches ? '✓ Passwords match' : '✗ Passwords do not match';
        hint.className = 'form-hint ' + (matches ? '' : 'error');
      }
      return matches;
    };

    if (password) password.addEventListener('input', checkMatch);
    if (confirm) confirm.addEventListener('input', checkMatch);

    signupForm.addEventListener('submit', (e) => {
      if (!checkMatch()) {
        e.preventDefault();
      }
    });
  }

  /* ---------- Cover Letter Character Counter ---------- */
  const coverLetter = document.querySelector('#cover_letter');
  const counter = document.querySelector('#char-count');
  if (coverLetter && counter) {
    const updateCount = () => {
      counter.textContent = `${coverLetter.value.length} characters`;
    };
    coverLetter.addEventListener('input', updateCount);
    updateCount();
  }

  /* ---------- Filter Sidebar Mobile Toggle ---------- */
  const filterToggle = document.querySelector('.filter-toggle');
  const filterSidebar = document.querySelector('.filter-sidebar');
  if (filterToggle && filterSidebar) {
    filterToggle.addEventListener('click', () => {
      filterSidebar.classList.toggle('collapsed');
    });
  }

  /* ---------- Sort Select Auto-Submit ---------- */
  const sortSelect = document.querySelector('.sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      const form = sortSelect.closest('form');
      if (form) {
        form.submit();
      } else {
        const url = new URL(window.location);
        url.searchParams.set('sort', sortSelect.value);
        window.location.href = url.toString();
      }
    });
  }

  /* ---------- Skills Tag Input ---------- */
  const skillsInput = document.querySelector('#skills_required');
  if (skillsInput && skillsInput.dataset.tagInput === 'true') {
    const wrapper = document.createElement('div');
    wrapper.className = 'tag-input-wrapper';
    skillsInput.parentNode.insertBefore(wrapper, skillsInput);
    wrapper.appendChild(skillsInput);

    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'skill-tags';
    tagsContainer.style.marginTop = '8px';
    wrapper.appendChild(tagsContainer);

    const updateTags = () => {
      tagsContainer.innerHTML = '';
      const skills = skillsInput.value.split(',').map(s => s.trim()).filter(Boolean);
      skills.forEach(skill => {
        const tag = document.createElement('span');
        tag.className = 'skill-tag';
        tag.textContent = skill;
        tagsContainer.appendChild(tag);
      });
    };

    skillsInput.addEventListener('input', updateTags);
    updateTags();
  }

  /* ---------- Role Card Selection ---------- */
  document.querySelectorAll('.role-card').forEach(card => {
    card.addEventListener('click', () => {
      const radio = card.querySelector('input[type="radio"]');
      if (radio) {
        radio.checked = true;
        radio.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
  });
});
