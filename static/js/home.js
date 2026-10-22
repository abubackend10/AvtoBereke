document.querySelectorAll('[data-recommended-carousel]').forEach(carousel => {
  const viewport = carousel.querySelector('[data-carousel-viewport]');
  const pages = [...carousel.querySelectorAll('[data-carousel-page]')];
  const dots = [...carousel.querySelectorAll('[data-carousel-dot]')];
  const previousButton = carousel.querySelector('[data-carousel-prev]');
  const nextButton = carousel.querySelector('[data-carousel-next]');

  if (!viewport || pages.length < 2) return;

  let currentPage = 0;
  let scrollFrame = null;
  const mobileCarousel = window.matchMedia('(max-width: 768px)');

  const getPageScrollPosition = page =>
    viewport.scrollLeft + page.getBoundingClientRect().left - viewport.getBoundingClientRect().left;

  const updateViewportHeight = () => {
    if (!mobileCarousel.matches) {
      viewport.style.height = '';
      return;
    }

    viewport.style.height = `${pages[currentPage].scrollHeight}px`;
  };

  const updateControls = pageIndex => {
    currentPage = Math.max(0, Math.min(pageIndex, pages.length - 1));
    updateViewportHeight();
    dots.forEach((dot, index) => {
      const isActive = index === currentPage;
      dot.classList.toggle('is-active', isActive);
      if (isActive) {
        dot.setAttribute('aria-current', 'true');
      } else {
        dot.removeAttribute('aria-current');
      }
    });
    if (previousButton) previousButton.disabled = currentPage === 0;
    if (nextButton) nextButton.disabled = currentPage === pages.length - 1;
  };

  const showPage = pageIndex => {
    const nextPage = Math.max(0, Math.min(pageIndex, pages.length - 1));
    viewport.scrollTo({
      left: getPageScrollPosition(pages[nextPage]),
      behavior: 'smooth',
    });
    updateControls(nextPage);

    const viewportTop = viewport.getBoundingClientRect().top;
    const headerHeight = document.querySelector('.header')?.getBoundingClientRect().height ?? 0;
    if (viewportTop < headerHeight || viewportTop >= window.innerHeight) {
      viewport.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' });
    }
  };

  const getCurrentPage = () => {
    let nearestPage = 0;
    let nearestDistance = Infinity;
    pages.forEach((page, index) => {
      const distance = Math.abs(getPageScrollPosition(page) - viewport.scrollLeft);
      if (distance < nearestDistance) {
        nearestDistance = distance;
        nearestPage = index;
      }
    });
    return nearestPage;
  };

  viewport.addEventListener('scroll', () => {
    if (scrollFrame !== null) cancelAnimationFrame(scrollFrame);
    scrollFrame = requestAnimationFrame(() => {
      updateControls(getCurrentPage());
      scrollFrame = null;
    });
  }, { passive: true   });

  window.addEventListener('resize', updateViewportHeight, { passive: true });
  if ('ResizeObserver' in window) {
    const pageResizeObserver = new ResizeObserver(updateViewportHeight);
    pages.forEach(page => {
      page.querySelectorAll('.car').forEach(card => pageResizeObserver.observe(card));
    });
  }
  updateViewportHeight();

  dots.forEach((dot, index) => dot.addEventListener('click', () => showPage(index)));
  previousButton?.addEventListener('click', () => showPage(currentPage - 1));
  nextButton?.addEventListener('click', () => showPage(currentPage + 1));
  viewport.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault();
      showPage(currentPage - 1);
    } else if (event.key === 'ArrowRight') {
      event.preventDefault();
      showPage(currentPage + 1);
    }
  });
});

// ==========================================
// 3. Анимированные счётчики (сохраняют все знаки: +, /, %, и т.д.)
// ==========================================
const counters = document.querySelectorAll('.counter');
if (counters.length) {
  const run = el => {
    // Берём исходный текст из data-target или из самoго элемента (например, "500+" или "24/7")
    const originalText = (el.dataset.target || el.textContent).trim();
    
    // Выделяем первое найденное число
    const match = originalText.match(/\d+/);
    if (!match) return; // Если чисел нет, ничего не анимируем

    const target = Number(match[0]);
    const numberIndex = match.index;
    const numberLength = match[0].length;

    // Разбиваем строку на части: ДО числа и ПОСЛЕ числа
    const prefix = originalText.slice(0, numberIndex);
    const suffix = originalText.slice(numberIndex + numberLength);

    const duration = 1800;
    const start = performance.now();

    const step = t => {
      const progress = Math.min((t - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 4);
      const currentNumber = progress === 1 ? target : Math.floor(target * eased);
      
      // Склеиваем префикс + анимированное число + суффикс (знаки)
      el.textContent = `${prefix}${currentNumber.toLocaleString('ru-RU')}${suffix}`;
      
      if (progress < 1) requestAnimationFrame(step);
    };

    requestAnimationFrame(step);
  };

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    counters.forEach(counter => {
      counter.textContent = counter.dataset.target || counter.textContent;
    });
  } else if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          run(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });
    counters.forEach(counter => io.observe(counter));
  } else {
    counters.forEach(run);
  }
}
