/* ================================================
   상품 상세 페이지 JavaScript
================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ===== GALLERY SWIPER =====
  const gallerySwiper = new Swiper('.gallerySwiper', {
    loop: false,
    speed: 400,
    on: {
      slideChange() {
        const counter = document.getElementById('galleryCounter');
        if (counter) {
          counter.textContent = `${this.realIndex + 1} / ${this.slides.length}`;
        }
      }
    }
  });

  document.getElementById('galleryPrev')?.addEventListener('click', () => gallerySwiper.slidePrev());
  document.getElementById('galleryNext')?.addEventListener('click', () => gallerySwiper.slideNext());

  // ===== COURSE SWIPER =====
  new Swiper('.courseSwiper', {
    spaceBetween: 12,
    slidesPerView: 1.1,
    pagination: { el: '.courseSwiper-pagination', clickable: true },
    breakpoints: {
      480: { slidesPerView: 1.4 },
      768: { slidesPerView: 2.2 },
      1200: { slidesPerView: 3 },
    }
  });

  // ===== HOTEL SWIPER =====
  new Swiper('.hotelSwiper', {
    loop: true,
    autoplay: { delay: 3000, disableOnInteraction: false },
    speed: 500,
  });

  // ===== PACKAGE SELECTION =====
  const packages = {
    '2n3d': { price: 560000, label: '560,000원' },
    '3n4d': { price: 790000, label: '790,000원' },
    '4n5d': { price: 1050000, label: '1,050,000원' },
  };
  let selectedPkg = '2n3d';
  let peopleCount = 2;

  function updatePrice() {
    const pkg = packages[selectedPkg];
    const total = pkg.price * peopleCount;
    document.getElementById('pkgPriceDisplay').textContent = pkg.label;
    document.getElementById('peopleDisplay').textContent = `${peopleCount}명`;
    document.getElementById('totalPrice').textContent =
      total.toLocaleString('ko-KR') + '원~';
  }

  document.querySelectorAll('.package-option').forEach(opt => {
    opt.addEventListener('click', () => {
      document.querySelectorAll('.package-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      selectedPkg = opt.querySelector('input').value;
      updatePrice();
    });
  });

  // People counter
  document.getElementById('peopleMinus')?.addEventListener('click', () => {
    if (peopleCount > 1) {
      peopleCount--;
      document.getElementById('peopleCount').textContent = peopleCount;
      updatePrice();
    }
  });
  document.getElementById('peoplePlus')?.addEventListener('click', () => {
    if (peopleCount < 20) {
      peopleCount++;
      document.getElementById('peopleCount').textContent = peopleCount;
      updatePrice();
    }
  });

  // Initial date
  const dateInput = document.getElementById('departDate');
  if (dateInput) {
    const today = new Date();
    today.setDate(today.getDate() + 14);
    dateInput.min = new Date().toISOString().split('T')[0];
    dateInput.value = today.toISOString().split('T')[0];
  }

  // ===== DETAIL TABS =====
  const dtabs = document.querySelectorAll('.dtab');
  dtabs.forEach(tab => {
    tab.addEventListener('click', () => {
      dtabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const target = tab.dataset.target;
      const section = document.getElementById(target);
      if (section) {
        const offset = parseInt(getComputedStyle(document.documentElement)
          .getPropertyValue('--header-h')) + 50;
        const top = section.getBoundingClientRect().top + window.scrollY - offset;
        window.scrollTo({ top, behavior: 'smooth' });
      }
    });
  });

  // Sync tabs on scroll
  const sectionIds = ['itinerary', 'includes', 'course-info', 'hotel-info', 'reviews'];
  const sectionEls = sectionIds.map(id => document.getElementById(id)).filter(Boolean);

  const tabObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        dtabs.forEach(tab => {
          tab.classList.toggle('active', tab.dataset.target === id);
        });
      }
    });
  }, { threshold: 0.3, rootMargin: '-100px 0px -60% 0px' });

  sectionEls.forEach(el => tabObserver.observe(el));

  // ===== TIPS ACCORDION =====
  document.querySelectorAll('.tip-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.tip-item');
      const isOpen = item.classList.contains('open');
      // Close all
      document.querySelectorAll('.tip-item').forEach(i => i.classList.remove('open'));
      // Open clicked
      if (!isOpen) item.classList.add('open');
    });
  });
  // Open first by default
  document.querySelector('.tip-item')?.classList.add('open');

  // ===== RESERVE MODAL =====
  const modalOverlay = document.getElementById('modalOverlay');
  const modalClose = document.getElementById('modalClose');

  function openModal() {
    modalOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeModal() {
    modalOverlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  document.getElementById('btnReserve')?.addEventListener('click', openModal);
  document.getElementById('stickyReserve')?.addEventListener('click', openModal);
  modalClose?.addEventListener('click', closeModal);
  modalOverlay?.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeModal();
  });

  // Form submit
  document.getElementById('reserveForm')?.addEventListener('submit', (e) => {
    e.preventDefault();
    alert('예약 신청이 완료되었습니다!\n담당자가 확인 후 빠르게 연락드리겠습니다.\n감사합니다 😊');
    closeModal();
  });

  // ===== STICKY BOTTOM / SCROLL TOP =====
  const stickyBottom = document.querySelector('.sticky-bottom');
  window.addEventListener('scroll', () => {
    const scrolled = window.scrollY;
    if (stickyBottom) {
      stickyBottom.style.transform = scrolled > 50
        ? 'translateX(-50%)'
        : 'translateX(-50%)';
    }
  }, { passive: true });

  // ===== SCROLL ANIMATION =====
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.day-item, .course-card, .review-item, .why-card').forEach(el => {
    el.classList.add('fade-in');
    observer.observe(el);
  });

});
