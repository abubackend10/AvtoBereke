// ==========================================
// 1. Мобильное меню
// ==========================================
const burger = document.getElementById('burger');
const nav = document.getElementById('nav');

if (burger && nav) {
  burger.addEventListener('click', () => {
    const isOpen = burger.classList.toggle('open');
    nav.classList.toggle('open', isOpen);
    burger.setAttribute('aria-expanded', String(isOpen));
  });

  nav.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      burger.classList.remove('open');
      nav.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    });
  });
}

// ==========================================
// 2. Эффект скролла шапки (Header)
// ==========================================
const header = document.querySelector('.header');
if (header) {
  const updateHeader = () => header.classList.toggle('is-scrolled', window.scrollY > 16);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });
}

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

// ==========================================
// 4. Пересчёт Валют и Переключение Языков
// ==========================================
const CURRENCIES = {
  usd: { code: 'USD', symbol: '$', rate: 1, pos: 'before', ph: '30,000' },
  kgs: { code: 'KGS', symbol: '⃀', rate: 89.5, pos: 'after', ph: '2,500,000' },
  rub: { code: 'RUB', symbol: '₽', rate: 92, pos: 'after', ph: '2,500,000' }
};

const getSavedCurrency = () => localStorage.getItem('avtobereke_currency') || 'usd';

const getCurrentLanguage = () => {
  const pathSegments = window.location.pathname.split('/');
  const langInPath = pathSegments[1];
  if (['ru', 'ky', 'uz'].includes(langInPath)) {
    return langInPath;
  }
  return document.documentElement.lang || 'ru';
};

function formatPrice(usdPrice, currKey) {
  const curr = CURRENCIES[currKey] || CURRENCIES.usd;
  const converted = Math.round(usdPrice * curr.rate);
  const formatted = converted.toLocaleString('en-US');
  return curr.pos === 'before' ? `${curr.symbol}${formatted}` : `${formatted} ${curr.symbol}`;
}

function updateSettingsBtnLabel() {
  const lbl = document.getElementById('settingsBtnText');
  if (lbl) {
    const c = (getSavedCurrency() || 'usd').toUpperCase();
    const l = getCurrentLanguage().toUpperCase();
    lbl.textContent = `${c} · ${l}`;
  }
}

let onCurrencyChangeCallback = null;

function applyCurrency(currKey) {
  const curr = CURRENCIES[currKey] || CURRENCIES.usd;

  // Обновляем карточки авто
  document.querySelectorAll('.car').forEach(car => {
    const rawUsd = Number(car.dataset.price);
    if (!isNaN(rawUsd)) {
      const priceEl = car.querySelector('.car__price') || car.querySelector('.car__foot strong');
      if (priceEl) {
        priceEl.textContent = formatPrice(rawUsd, currKey);
      }
    }
  });

  // Обновляем элементы с data-usd (на странице авто)
  document.querySelectorAll('[data-usd]').forEach(el => {
    const rawUsd = Number(el.dataset.usd);
    if (!isNaN(rawUsd)) {
      el.textContent = formatPrice(rawUsd, currKey);
    }
  });

  // Подсветка активной валюты в модалке
  document.querySelectorAll('#currOptions .settings-opt').forEach(btn => {
    btn.classList.toggle('is-active', btn.dataset.curr === currKey);
  });

  updateSettingsBtnLabel();

  if (typeof onCurrencyChangeCallback === 'function') {
    onCurrencyChangeCallback();
  }
}

function highlightActiveLanguage() {
  const currentLang = getCurrentLanguage();
  document.querySelectorAll('#langOptions .settings-opt').forEach(btn => {
    btn.classList.toggle('is-active', btn.dataset.lang === currentLang);
  });
}

// ==========================================
// 5. Модальное окно настроек
// ==========================================
const settingsModal = document.getElementById('settingsModal');

const openModal = () => {
  if (settingsModal) {
    settingsModal.classList.add('is-open');
    settingsModal.setAttribute('aria-hidden', 'false');
  }
};

const closeModal = () => {
  if (settingsModal) {
    settingsModal.classList.remove('is-open');
    settingsModal.setAttribute('aria-hidden', 'true');
  }
};

document.addEventListener('click', e => {
  if (e.target.closest('#openSettingsBtn') || e.target.closest('#openSettingsBtnMobile') || e.target.closest('[data-open-settings]')) {
    e.preventDefault();
    openModal();
  }
  if (e.target.closest('#closeSettingsBtn') || e.target.closest('#saveSettingsBtn') || e.target.closest('#settingsModalBackdrop')) {
    e.preventDefault();
    closeModal();
  }
});

window.addEventListener('keydown', e => {
  if (e.key === 'Escape' && settingsModal && settingsModal.classList.contains('is-open')) {
    closeModal();
  }
});

// Переключение языка через URL-префиксы Django (/ru/, /ky/, /uz/)
document.querySelectorAll('#langOptions .settings-opt').forEach(btn => {
  btn.addEventListener('click', () => {
    const lang = btn.dataset.lang;
    const currentPath = window.location.pathname;
    const pathSegments = currentPath.split('/');

    if (['ru', 'ky', 'uz'].includes(pathSegments[1])) {
      pathSegments[1] = lang;
    } else {
      pathSegments.splice(1, 0, lang);
    }
    window.location.href = pathSegments.join('/') + window.location.search;
  });
});

// Переключение валюты
document.querySelectorAll('#currOptions .settings-opt').forEach(btn => {
  btn.addEventListener('click', () => {
    const curr = btn.dataset.curr;
    localStorage.setItem('avtobereke_currency', curr);
    applyCurrency(curr);
  });
});

// Инициализация при загрузке страницы
highlightActiveLanguage();
updateSettingsBtnLabel();
applyCurrency(getSavedCurrency());