/* ================================================
   마이골프트래블 - Main JavaScript
================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ===== HEADER SCROLL EFFECT =====
  const header = document.getElementById('header');
  let lastScroll = 0;
  window.addEventListener('scroll', () => {
    const currentScroll = window.scrollY;
    if (currentScroll > 10) {
      header.style.boxShadow = '0 4px 16px rgba(0,0,0,0.12)';
    } else {
      header.style.boxShadow = '0 1px 4px rgba(0,0,0,0.08)';
    }
    lastScroll = currentScroll;
  }, { passive: true });

  // ===== MOBILE NAV DRAWER =====
  const btnMenu = document.getElementById('btnMenu');
  const btnClose = document.getElementById('btnClose');
  const navDrawer = document.getElementById('navDrawer');
  const navOverlay = document.getElementById('navOverlay');

  function openNav() {
    navDrawer.classList.add('open');
    navOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeNav() {
    navDrawer.classList.remove('open');
    navOverlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  btnMenu?.addEventListener('click', openNav);
  btnClose?.addEventListener('click', closeNav);
  navOverlay?.addEventListener('click', closeNav);

  // Close nav on link click
  navDrawer.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeNav);
  });

  // ===== SEARCH BAR TOGGLE =====
  const btnSearch = document.getElementById('btnSearch');
  const searchBar = document.getElementById('searchBar');
  const searchInput = document.getElementById('searchInput');

  btnSearch?.addEventListener('click', () => {
    searchBar.classList.toggle('open');
    if (searchBar.classList.contains('open')) {
      searchInput?.focus();
    }
  });

  // Close search on outside click
  document.addEventListener('click', (e) => {
    if (!searchBar.contains(e.target) && !btnSearch.contains(e.target)) {
      searchBar.classList.remove('open');
    }
  });

  // ===== HERO SWIPER =====
  new Swiper('.heroSwiper', {
    loop: true,
    autoplay: { delay: 4000, disableOnInteraction: false },
    speed: 800,
    effect: 'fade',
    fadeEffect: { crossFade: true },
    pagination: { el: '.heroSwiper-pagination', clickable: true },
  });

  // ===== FEATURED SWIPER =====
  new Swiper('.featuredSwiper', {
    spaceBetween: 12,
    slidesPerView: 1.1,
    pagination: { el: '.featuredSwiper-pagination', clickable: true },
    autoplay: { delay: 3500, disableOnInteraction: false },
    breakpoints: {
      480: { slidesPerView: 1.3 },
      768: { slidesPerView: 2.2 },
    }
  });

  // ===== BEST PRODUCT SWIPERS =====
  ['bestSwiper1', 'bestSwiper2', 'bestSwiper3'].forEach(cls => {
    new Swiper(`.${cls}`, {
      spaceBetween: 12,
      slidesPerView: 1.1,
      breakpoints: {
        480: { slidesPerView: 1.3 },
        768: { slidesPerView: 2.2 },
        1200: { slidesPerView: 3 },
      }
    });
  });

  // ===== REVIEW SWIPER =====
  new Swiper('.reviewSwiper', {
    spaceBetween: 12,
    slidesPerView: 1.05,
    pagination: { el: '.reviewSwiper-pagination', clickable: true },
    autoplay: { delay: 4500, disableOnInteraction: false },
    breakpoints: {
      480: { slidesPerView: 1.2 },
      768: { slidesPerView: 2.1 },
    }
  });

  // ===== CATEGORY TABS =====
  const categoryTabs = document.getElementById('categoryTabs');
  if (categoryTabs) {
    categoryTabs.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        categoryTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const target = btn.dataset.tab;
        const section = document.getElementById(target);
        if (section) {
          const offset = 56 + 48; // header + sticky tabs
          const top = section.getBoundingClientRect().top + window.scrollY - offset;
          window.scrollTo({ top, behavior: 'smooth' });
        }
      });
    });
  }

  // ===== BEST PRODUCT TABS =====
  const bestTabs = document.getElementById('bestTabs');
  if (bestTabs) {
    bestTabs.querySelectorAll('.best-tab').forEach(btn => {
      btn.addEventListener('click', () => {
        bestTabs.querySelectorAll('.best-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        document.querySelectorAll('.best-list').forEach(list => list.classList.remove('active'));
        const targetId = `best-${btn.dataset.best}`;
        document.getElementById(targetId)?.classList.add('active');
      });
    });
  }

  // ===== DESTINATION CHIPS =====
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
      document.querySelectorAll('.chip').forEach(c => c.classList.remove('chip-active'));
      chip.classList.add('chip-active');
    });
  });

  // ===== SCROLL TO TOP =====
  const scrollTopBtn = document.getElementById('scrollTop');
  scrollTopBtn?.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // Show/hide scroll-to-top button
  window.addEventListener('scroll', () => {
    if (scrollTopBtn) {
      scrollTopBtn.style.display = window.scrollY > 300 ? 'flex' : 'none';
    }
  }, { passive: true });
  if (scrollTopBtn) scrollTopBtn.style.display = 'none';

  // ===== SCROLL ANIMATION (Intersection Observer) =====
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.product-card, .why-card, .event-card, .review-card').forEach(el => {
    el.classList.add('fade-in');
    observer.observe(el);
  });

  // ===== LAZY LOAD IMAGES =====
  if ('loading' in HTMLImageElement.prototype) {
    // Native lazy loading supported, nothing extra needed
  } else {
    // Fallback for older browsers
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    const imgObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src || img.src;
          imgObserver.unobserve(img);
        }
      });
    });
    lazyImages.forEach(img => imgObserver.observe(img));
  }

  // ===== PHONE LINK TRACKING =====
  document.querySelectorAll('a[href^="tel:"]').forEach(link => {
    link.addEventListener('click', () => {
      console.log('Phone call initiated');
      // Add analytics tracking here (e.g., gtag event)
    });
  });

  // ===== STICKY TAB SYNC ON SCROLL =====
  const sections = [
    { id: 'overseas', tab: 'overseas' },
    { id: 'japan', tab: 'japan' },
    { id: 'thailand', tab: 'thailand' },
    { id: 'domestic', tab: 'domestic' },
  ];

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const sectionId = entry.target.id;
        const match = sections.find(s => s.id === sectionId);
        if (match && categoryTabs) {
          categoryTabs.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === match.tab);
          });
        }
      }
    });
  }, { threshold: 0.4 });

  sections.forEach(({ id }) => {
    const el = document.getElementById(id);
    if (el) sectionObserver.observe(el);
  });

});
