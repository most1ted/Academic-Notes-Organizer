// script.js - Full account page with add-course feature (no frameworks)

document.addEventListener('DOMContentLoaded', () => {
  // UI elements
  const navToggle = document.getElementById('navToggle');
  const mobileMenu = document.getElementById('mobileMenu');
  const coursesGrid = document.getElementById('coursesGrid');
  const summaryText = document.getElementById('summaryText');
  const searchInput = document.getElementById('searchInput');
  const filterSelect = document.getElementById('filterSelect');
  const emptyState = document.getElementById('emptyState');
  const drawer = document.getElementById('courseDrawer');
  const drawerContent = document.getElementById('drawerContent');
  const addBtn = document.getElementById('addCourseBtn');
  const addModal = document.getElementById('addCourseModal');
  const addForm = document.getElementById('addCourseForm');
  const fileInput = document.getElementById('courseMedia');
  const preview = document.getElementById('mediaPreview');
  const msg = document.getElementById('addCourseMessage');
  const submitBtn = document.getElementById('addCourseSubmit');
  const yearEl = document.getElementById('year');

  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Mobile toggle
  navToggle && navToggle.addEventListener('click', () => {
    const expanded = navToggle.getAttribute('aria-expanded') === 'true';
    navToggle.setAttribute('aria-expanded', String(!expanded));
    if (mobileMenu) mobileMenu.hidden = expanded;
  });

  // Render initial skeletons
  renderSkeletons(6);

  // Reduced motion flag
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // IntersectionObserver for reveal animations
  const io = (!reducedMotion && 'IntersectionObserver' in window) ? new IntersectionObserver((entries, obs) => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        en.target.classList.add('in-view');
        obs.unobserve(en.target);
      }
    });
  }, { threshold: 0.06 }) : null;

  // Fetch courses (mock)
  const userId = getUserIdFromContext() || 'user-123';
  fetchUserCourses(userId).then(courses => {
    window.__courses = courses || [];
    renderCoursesList(window.__courses);
    summaryText.textContent = `Showing ${window.__courses.length} course${window.__courses.length !== 1 ? 's' : ''}`;
    const deep = readCourseFromURL();
    if (deep) openCourse(deep);
  }).catch(err => {
    console.error(err);
    summaryText.textContent = 'Failed to load courses. Try again later.';
    coursesGrid.innerHTML = '';
  });

  // Search & Filter
  let sTimer = null;
  searchInput.addEventListener('input', () => {
    clearTimeout(sTimer);
    sTimer = setTimeout(applyFilters, 220);
  });
  filterSelect.addEventListener('change', applyFilters);

  // Drawer open/close (delegated)
  coursesGrid.addEventListener('click', (e) => {
    const card = e.target.closest('.card[data-id]');
    if (card) openCourse(card.dataset.id);
  });
  coursesGrid.addEventListener('keydown', (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && e.target && e.target.classList.contains('card')) {
      e.preventDefault();
      openCourse(e.target.dataset.id);
    }
  });

  // Drawer dismiss via backdrop / close / Escape
  document.addEventListener('click', (e) => {
    if (e.target && e.target.dataset && e.target.dataset.dismiss !== undefined) closeDrawer();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (addModal && addModal.getAttribute('aria-hidden') === 'false') closeAddModal();
      else closeDrawer();
    }
  });

  // Add-course modal open/close
  addBtn && addBtn.addEventListener('click', openAddModal);
  addModal && addModal.addEventListener('click', (e) => {
    if (e.target && e.target.dataset && e.target.dataset.dismiss !== undefined) closeAddModal();
  });

  // file preview & validation
  const MAX_FILE_BYTES = 5 * 1024 * 1024;
  const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/gif'];

  fileInput && fileInput.addEventListener('change', (e) => {
    preview.innerHTML = '';
    msg.textContent = '';
    const f = e.target.files && e.target.files[0];
    if (!f) return;
    if (!ALLOWED_TYPES.includes(f.type)) {
      msg.textContent = 'Unsupported file type. Allowed: PDF, JPG, PNG, GIF.';
      fileInput.value = '';
      return;
    }
    if (f.size > MAX_FILE_BYTES) {
      msg.textContent = 'File too large. Max 5 MB.';
      fileInput.value = '';
      return;
    }
    if (f.type === 'application/pdf') {
      const badge = document.createElement('div');
      badge.className = 'pdf-badge';
      badge.textContent = f.name;
      preview.appendChild(badge);
    } else if (f.type.startsWith('image/')) {
      const img = document.createElement('img');
      img.alt = f.name;
      img.src = URL.createObjectURL(f);
      img.onload = () => URL.revokeObjectURL(img.src);
      preview.appendChild(img);
    } else {
      preview.textContent = f.name;
    }
  });

  // Add-course form submit
  addForm && addForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    msg.textContent = '';
    submitBtn.disabled = true;

    const courseId = (addForm.courseId.value || '').trim();
    const title = (addForm.title.value || '').trim();
    const description = (addForm.description.value || '').trim();
    const file = fileInput.files && fileInput.files[0];

    if (!courseId || !/^[\w\-]+$/.test(courseId)) {
      msg.textContent = 'Please enter a valid course ID (letters, numbers, underscores, hyphens).';
      submitBtn.disabled = false;
      return;
    }
    if (!title) {
      msg.textContent = 'Please enter a course title.';
      submitBtn.disabled = false;
      return;
    }

    try {
      msg.textContent = 'Uploading...';

      // Replace simulateUpload with real upload flow in production
      const uploaded = await simulateUpload(file);

      const newCourse = {
        id: courseId,
        title,
        instructor: 'You',
        status: 'In Progress',
        progress: 0,
        description,
        media: uploaded, // { url, type, name } or null
        createdAt: new Date().toISOString()
      };

      window.__courses = window.__courses || [];
      window.__courses.unshift(newCourse);

      if (typeof renderCoursesList === 'function') renderCoursesList(window.__courses);

      msg.textContent = 'Course added.';
      setTimeout(() => closeAddModal(), 450);
    } catch (err) {
      console.error(err);
      msg.textContent = 'Failed to add course. Try again.';
      submitBtn.disabled = false;
    }
  });

  // ---------------- Functions ----------------

  function renderSkeletons(n = 4) {
    coursesGrid.innerHTML = '';
    emptyState.hidden = true;
    for (let i = 0; i < n; i++) {
      const div = document.createElement('div');
      div.className = 'skeleton';
      coursesGrid.appendChild(div);
    }
  }

  function renderCoursesList(courses) {
    coursesGrid.innerHTML = '';
    const filtered = applyQuery(courses, getSearchValue(), filterSelect.value);
    if (!filtered.length) {
      emptyState.hidden = false;
      summaryText.textContent = `Showing 0 courses`;
      return;
    }
    emptyState.hidden = true;
    filtered.forEach(course => {
      const card = buildCourseCard(course);
      coursesGrid.appendChild(card);
      if (io) io.observe(card);
      requestAnimationFrame(() => {
        const bar = card.querySelector('.progress > span');
        if (bar) bar.style.width = `${Math.max(6, Math.min(100, course.progress))}%`;
      });
    });
    summaryText.textContent = `Showing ${filtered.length} of ${courses.length} course${courses.length !== 1 ? 's' : ''}`;
  }

  function buildCourseCard(course) {
    const el = document.createElement('article');
    el.className = 'card reveal';
    el.tabIndex = 0;
    el.setAttribute('role', 'button');
    el.dataset.id = course.id;
    el.innerHTML = `
      <div class="card-top">
        <div>
          <h3 class="card-title">${escapeHtml(course.title)}</h3>
          <div class="card-meta">${escapeHtml(course.instructor)}</div>
        </div>
        <div style="text-align:right">
          <div class="card-meta">${escapeHtml(course.status)}</div>
          <div style="font-weight:700">${course.progress}%</div>
        </div>
      </div>
      <div class="progress" aria-hidden="true"><span style="width:0"></span></div>
    `;
    return el;
  }

  function getSearchValue() {
    return (searchInput.value || '').trim().toLowerCase();
  }
  function applyFilters() {
    const courses = window.__courses || [];
    renderCoursesList(courses);
  }
  function applyQuery(courses, q, status) {
    let arr = Array.isArray(courses) ? courses.slice() : [];
    if (status && status !== 'all') arr = arr.filter(c => normalize(c.status) === status);
    if (q) arr = arr.filter(c => (c.title + ' ' + c.instructor + ' ' + (c.tags || []).join(' ')).toLowerCase().includes(q));
    return arr;
  }

  function openCourse(id) {
    const course = (window.__courses || []).find(c => c.id === id);
    if (!course) return;
    drawerContent.innerHTML = buildCourseDetailHtml(course);
    showDrawer();
    updateURLWithCourse(course.id);
  }
  function buildCourseDetailHtml(course) {
    let mediaHtml = '';
    if (course.media && course.media.type) {
      if (course.media.type === 'application/pdf') {
        mediaHtml = `<div class="pdf-badge" style="margin-top:.6rem">${escapeHtml(course.media.name)}</div>`;
      } else if (course.media.url) {
        mediaHtml = `<img style="max-width:100%;margin-top:.6rem;border-radius:8px" src="${escapeHtml(course.media.url)}" alt="${escapeHtml(course.media.name)}">`;
      }
    }
    return `
      <h2 id="drawerTitle">${escapeHtml(course.title)}</h2>
      <p class="card-meta">By ${escapeHtml(course.instructor)} • ${escapeHtml(course.status)} • ${course.progress}% complete</p>
      <hr>
      <p>${escapeHtml(course.description)}</p>
      ${mediaHtml}
      <div style="margin-top:1rem;display:flex;gap:.5rem;flex-wrap:wrap">
        <a class="btn-primary" href="#resume-${encodeURIComponent(course.id)}">Resume</a>
        <button id="viewSyllabus" class="btn-ghost">View syllabus</button>
      </div>
    `;
  }
  function showDrawer() {
    drawer.setAttribute('aria-hidden', 'false');
    setTimeout(() => {
      drawerContent.focus();
    }, 120);
  }
  function closeDrawer() {
    if (!drawer) return;
    drawer.setAttribute('aria-hidden', 'true');
    removeCourseFromURL();
  }

  // ---------------- Add modal helpers ----------------
  function openAddModal() {
    if (!addModal) return;
    addModal.setAttribute('aria-hidden', 'false');
    setTimeout(() => {
      const first = addForm.querySelector('#courseId');
      if (first) first.focus();
    }, 80);
    document.addEventListener('keydown', trapTabInAddModal);
  }
  function closeAddModal() {
    if (!addModal) return;
    addModal.setAttribute('aria-hidden', 'true');
    addForm.reset();
    preview.innerHTML = '';
    msg.textContent = '';
    submitBtn.disabled = false;
    document.removeEventListener('keydown', trapTabInAddModal);
    if (addBtn) addBtn.focus();
  }
  function trapTabInAddModal(e) {
    if (e.key !== 'Tab') return;
    const focusable = addModal.querySelectorAll('a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])');
    if (!focusable.length) return;
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault(); last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault(); first.focus();
    }
  }

  // ---------------- URL helpers ----------------
  function updateURLWithCourse(courseId) {
    try {
      const u = new URL(location.href);
      u.searchParams.set('course', courseId);
      history.pushState({ course: courseId }, '', u.toString());
    } catch (e) {
      location.hash = `course=${courseId}`;
    }
  }
  function removeCourseFromURL() {
    try {
      const u = new URL(location.href);
      u.searchParams.delete('course');
      history.pushState({}, '', u.toString());
    } catch (e) {
      if (location.hash && location.hash.startsWith('#course=')) location.hash = '';
    }
  }
  function readCourseFromURL() {
    try {
      const u = new URL(location.href);
      return u.searchParams.get('course');
    } catch (e) {
      if (location.hash && location.hash.startsWith('#course=')) return location.hash.split('=')[1];
      return null;
    }
  }

  // ---------------- Mock upload & fetch (replace with real API) ----------------
  function fetchUserCourses(userId) {
    return new Promise((resolve) => {
      setTimeout(() => resolve(mockFetchCourses(userId)), 550 + Math.random() * 600);
    });
  }
  function mockFetchCourses(userId) {
    const all = [
      { id: 'c1', title: 'Modern JavaScript: From Fundamentals to Advanced', instructor: 'Alice Dev', status: 'In Progress', progress: 48, description: 'Deep dive into modern JS, async patterns, and tooling.', tags: ['javascript','frontend'] },
      { id: 'c2', title: 'UI Design Principles', instructor: 'Ben Designer', status: 'Completed', progress: 100, description: 'Design fundamentals and accessibility best practices.', tags: ['design','ux'] },
      { id: 'c3', title: 'Backend APIs with Node.js', instructor: 'Clara Server', status: 'In Progress', progress: 22, description: 'Building scalable APIs and authentication strategies.', tags: ['node','backend'] },
      { id: 'c4', title: 'Data Structures & Algorithms', instructor: 'Drew Algo', status: 'Archived', progress: 8, description: 'Essential algorithms and problem-solving techniques.', tags:['algorithms'] },
      { id: 'c5', title: 'State Management in React', instructor: 'Eve React', status: 'In Progress', progress: 65, description: 'Patterns and best practices for predictable UI state.', tags:['react'] },
      { id: 'c6', title: 'Intro to Machine Learning', instructor: 'Frank ML', status: 'Completed', progress: 100, description: 'Supervised learning, evaluation, and pipelines.', tags:['ml'] },
    ];
    return all.filter((_, i) => (i % 2 === 0) || userId.endsWith('3'));
  }

  // simulate upload (creates object URL for images, returns null for no file)
  function simulateUpload(file) {
    return new Promise((resolve) => {
      if (!file) {
        setTimeout(() => resolve(null), 350 + Math.random() * 400);
        return;
      }
      setTimeout(() => {
        const url = file.type === 'application/pdf' ? null : URL.createObjectURL(file);
        resolve({ url, type: file.type, name: file.name });
      }, 700 + Math.random() * 700);
    });
  }

  // ---------------- Utilities ----------------
  function escapeHtml(s) { return String(s).replace(/[&<>"']/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c])); }
  function normalize(s) { return String(s || '').toLowerCase().replace(/\s+/g, ''); }
  function getUserIdFromContext() { try { const p = new URLSearchParams(location.search); return p.get('user'); } catch(e){ return null; } }

  // expose for debugging
  window._accountPage = { openCourse, closeDrawer, openAddModal, closeAddModal };

});