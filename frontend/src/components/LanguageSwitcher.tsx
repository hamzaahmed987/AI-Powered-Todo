/**
 * Language Switcher Component
 * Allows users to switch between English and Urdu.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { Language, languages, getLanguage, setLanguage, initLanguage } from '../i18n';

interface LanguageSwitcherProps {
  className?: string;
}

export default function LanguageSwitcher({ className = '' }: LanguageSwitcherProps) {
  const [currentLang, setCurrentLang] = useState<Language>('en');

  useEffect(() => {
    // Initialize language on mount
    const timer = setTimeout(() => {
      const lang = initLanguage();
      setCurrentLang(lang);
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  const handleLanguageChange = (lang: Language) => {
    setLanguage(lang);
    setCurrentLang(lang);
    // Trigger re-render across app (in production, use Context or state management)
    window.dispatchEvent(new CustomEvent('languageChange', { detail: lang }));
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {(Object.keys(languages) as Language[]).map((lang) => (
        <button
          key={lang}
          onClick={() => handleLanguageChange(lang)}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
            currentLang === lang
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'
          }`}
          aria-label={`Switch to ${languages[lang].name}`}
        >
          {languages[lang].nativeName}
        </button>
      ))}
    </div>
  );
}
