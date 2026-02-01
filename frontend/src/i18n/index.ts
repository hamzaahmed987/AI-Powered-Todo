/**
 * Internationalization (i18n) setup for multi-language support.
 * Supports English (en) and Urdu (ur).
 */

import en from './locales/en.json';
import ur from './locales/ur.json';

export type Language = 'en' | 'ur';

export const languages: Record<Language, { name: string; nativeName: string; dir: 'ltr' | 'rtl' }> = {
  en: { name: 'English', nativeName: 'English', dir: 'ltr' },
  ur: { name: 'Urdu', nativeName: 'اردو', dir: 'rtl' },
};

const translations: Record<Language, typeof en> = {
  en,
  ur,
};

let currentLanguage: Language = 'en';

/**
 * Get the current language.
 */
export function getLanguage(): Language {
  return currentLanguage;
}

/**
 * Set the current language.
 */
export function setLanguage(lang: Language): void {
  currentLanguage = lang;
  // Update document direction for RTL languages
  if (typeof document !== 'undefined') {
    document.documentElement.lang = lang;
    document.documentElement.dir = languages[lang].dir;
  }
  // Persist to localStorage
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('language', lang);
  }
}

/**
 * Initialize language from localStorage or browser settings.
 */
export function initLanguage(): Language {
  if (typeof localStorage !== 'undefined') {
    const saved = localStorage.getItem('language') as Language;
    if (saved && languages[saved]) {
      setLanguage(saved);
      return saved;
    }
  }
  // Default to browser language if supported
  if (typeof navigator !== 'undefined') {
    const browserLang = navigator.language.split('-')[0] as Language;
    if (languages[browserLang]) {
      setLanguage(browserLang);
      return browserLang;
    }
  }
  return 'en';
}

/**
 * Get a translation by key path.
 * @param key Dot-separated key path (e.g., 'tasks.title')
 * @param params Optional parameters for interpolation
 */
export function t(key: string, params?: Record<string, string | number>): string {
  const keys = key.split('.');
  let value: unknown = translations[currentLanguage];

  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = (value as Record<string, unknown>)[k];
    } else {
      // Fallback to English
      value = translations.en;
      for (const fallbackKey of keys) {
        if (value && typeof value === 'object' && fallbackKey in value) {
          value = (value as Record<string, unknown>)[fallbackKey];
        } else {
          return key; // Return key if not found
        }
      }
      break;
    }
  }

  if (typeof value !== 'string') {
    return key;
  }

  // Simple interpolation: replace {{param}} with params[param]
  if (params) {
    return value.replace(/\{\{(\w+)\}\}/g, (_, paramKey) => {
      return params[paramKey]?.toString() ?? `{{${paramKey}}}`;
    });
  }

  return value;
}

/**
 * React hook for translations (use with useEffect to handle language changes).
 */
export function useTranslation() {
  return {
    t,
    language: currentLanguage,
    setLanguage,
    languages,
    isRTL: languages[currentLanguage].dir === 'rtl',
  };
}

export default { t, getLanguage, setLanguage, initLanguage, languages, useTranslation };
