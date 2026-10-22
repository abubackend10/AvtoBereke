// Shared image loading
const imageSkeletons = document.querySelectorAll('.image-loading .image-skeleton');

function finishImageLoading(event) {
  if (!event.target.matches('.image-skeleton')) return;
  event.target.closest('.image-loading')?.classList.remove('image-loading');
}

document.addEventListener('load', finishImageLoading, true);
document.addEventListener('error', finishImageLoading, true);

imageSkeletons.forEach(image => {
  if (image.complete) {
    image.closest('.image-loading')?.classList.remove('image-loading');
  }
});

// Header scroll state
const header = document.querySelector('.header');
if (header) {
  const updateHeader = () => header.classList.toggle('is-scrolled', window.scrollY > 16);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });
}

// Currency and language settings
const CURRENCIES = {
  usd: { symbol: '$', rate: 1, pos: 'before' },
  kgs: { symbol: 'сом', rate: 89.5, pos: 'after' },
  rub: { symbol: '₽', rate: 92, pos: 'after' }
};

const EXCHANGE_RATE_CACHE_KEY = 'avtobereke_exchange_rates';
const EXCHANGE_RATE_CACHE_TTL = 24 * 60 * 60 * 1000;

const getSavedCurrency = () => localStorage.getItem('avtobereke_currency') || 'usd';

function setExchangeRates(rates) {
  CURRENCIES.kgs.rate = rates.KGS;
  CURRENCIES.rub.rate = rates.RUB;
}

function getCachedExchangeRates() {
  try {
    const cached = JSON.parse(localStorage.getItem(EXCHANGE_RATE_CACHE_KEY) || 'null');
    if (
      !cached ||
      cached.base !== 'USD' ||
      !Number.isFinite(cached.updatedAt) ||
      !Number.isFinite(cached.rates?.KGS) ||
      !Number.isFinite(cached.rates?.RUB) ||
      cached.rates.KGS <= 0 ||
      cached.rates.RUB <= 0
    ) {
      return null;
    }

    return {
      rates: cached.rates,
      isFresh: Date.now() - cached.updatedAt >= 0 && Date.now() - cached.updatedAt < EXCHANGE_RATE_CACHE_TTL
    };
  } catch (error) {
    console.warn('Не удалось прочитать сохранённый курс валют:', error);
    return null;
  }
}

async function refreshExchangeRates() {
  try {
    const response = await fetch('https://open.er-api.com/v6/latest/USD', { cache: 'no-store' });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const rates = { KGS: Number(data.rates?.KGS), RUB: Number(data.rates?.RUB) };
    if (data.result !== 'success' || data.base_code !== 'USD' || rates.KGS <= 0 || rates.RUB <= 0 || !Number.isFinite(rates.KGS) || !Number.isFinite(rates.RUB)) {
      throw new Error('Источник вернул некорректные курсы USD/KGS/RUB');
    }

    setExchangeRates(rates);
    applyCurrency(getSavedCurrency());

    try {
      localStorage.setItem(EXCHANGE_RATE_CACHE_KEY, JSON.stringify({
        base: 'USD',
        rates,
        updatedAt: Date.now()
      }));
    } catch (error) {
      console.warn('Не удалось сохранить курс валют в кэш браузера:', error);
    }
  } catch (error) {
    console.error('Не удалось обновить курсы валют; используются последние доступные значения:', error);
  }
}

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
    const currentLanguage = getCurrentLanguage();
    const l = currentLanguage === 'ky' ? 'KG' : currentLanguage.toUpperCase();
    lbl.textContent = `${c} · ${l}`;
  }
}

function applyCurrency(currKey) {
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
}

function highlightActiveLanguage() {
  const currentLanguage = getCurrentLanguage();
  document.querySelectorAll('#langOptions .settings-opt').forEach(button => {
    button.classList.toggle('is-active', button.dataset.lang === currentLanguage);
  });
}

const languageButtons = document.querySelectorAll('#langOptions .settings-opt');
const selectedLanguageInput = document.getElementById('selectedLanguageInput');
const languageForm = document.getElementById('langForm');

languageButtons.forEach(button => {
  button.addEventListener('click', () => {
    languageButtons.forEach(item => item.classList.remove('is-active'));
    button.classList.add('is-active');
    if (selectedLanguageInput) {
      selectedLanguageInput.value = button.dataset.lang;
    }
  });
});

document.getElementById('saveSettingsBtn')?.addEventListener('click', () => {
  languageForm?.submit();
});

const settingsModal = document.getElementById('settingsModal');

const openModal = () => {
  if (!settingsModal) return;
  settingsModal.classList.add('is-open');
  settingsModal.setAttribute('aria-hidden', 'false');
};

const closeModal = () => {
  if (!settingsModal) return;
  settingsModal.classList.remove('is-open');
  settingsModal.setAttribute('aria-hidden', 'true');
};

document.addEventListener('click', event => {
  const target = event.target;
  if (!(target instanceof Element)) return;

  if (target.closest('#openSettingsBtn, #openSettingsBtnMobile, [data-open-settings]')) {
    event.preventDefault();
    openModal();
  }

  if (target.closest('#closeSettingsBtn, #saveSettingsBtn, #settingsModalBackdrop')) {
    event.preventDefault();
    closeModal();
  }
});

window.addEventListener('keydown', event => {
  if (event.key === 'Escape' && settingsModal?.classList.contains('is-open')) {
    closeModal();
  }
});

document.querySelectorAll('#currOptions .settings-opt').forEach(button => {
  button.addEventListener('click', () => {
    const currency = button.dataset.curr;
    if (!currency) return;
    localStorage.setItem('avtobereke_currency', currency);
    applyCurrency(currency);
  });
});

highlightActiveLanguage();
updateSettingsBtnLabel();
const cachedExchangeRates = getCachedExchangeRates();
if (cachedExchangeRates) {
  setExchangeRates(cachedExchangeRates.rates);
}
applyCurrency(getSavedCurrency());
if (!cachedExchangeRates || !cachedExchangeRates.isFresh) {
  refreshExchangeRates();
}