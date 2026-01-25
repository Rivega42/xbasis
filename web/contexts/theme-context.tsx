'use client';

/**
 * Theme Provider
 * 
 * Глобальное управление темой приложения.
 * Загружает тему из localStorage при старте.
 * Слушает изменения системной темы.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

// Типы
type Theme = 'light' | 'dark' | 'system';

interface ThemeContextValue {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: 'light' | 'dark'; // фактическая тема (без 'system')
}

// Контекст
const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

// Скрипт для предотвращения flash (вставляется в head)
const themeScript = `
  (function() {
    const theme = localStorage.getItem('theme') || 'system';
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (theme === 'dark' || (theme === 'system' && prefersDark)) {
      document.documentElement.classList.add('dark');
    }
  })();
`;

// Provider
interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>('system');
  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  // Применить тему к document
  const applyTheme = useCallback((newTheme: Theme) => {
    const root = document.documentElement;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    let resolved: 'light' | 'dark';
    
    if (newTheme === 'dark') {
      root.classList.add('dark');
      resolved = 'dark';
    } else if (newTheme === 'light') {
      root.classList.remove('dark');
      resolved = 'light';
    } else {
      // system
      if (prefersDark) {
        root.classList.add('dark');
        resolved = 'dark';
      } else {
        root.classList.remove('dark');
        resolved = 'light';
      }
    }
    
    setResolvedTheme(resolved);
  }, []);

  // Установить тему
  const setTheme = useCallback((newTheme: Theme) => {
    setThemeState(newTheme);
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  }, [applyTheme]);

  // Загрузка темы при монтировании
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    const initialTheme = savedTheme || 'system';
    
    setThemeState(initialTheme);
    applyTheme(initialTheme);
  }, [applyTheme]);

  // Слушаем изменения системной темы
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = () => {
      if (theme === 'system') {
        applyTheme('system');
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme, applyTheme]);

  const value: ThemeContextValue = {
    theme,
    setTheme,
    resolvedTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// Hook
export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  
  if (context === undefined) {
    throw new Error('useTheme должен использоваться внутри ThemeProvider');
  }
  
  return context;
}

// Компонент для вставки скрипта (предотвращает flash)
export function ThemeScript() {
  return (
    <script
      dangerouslySetInnerHTML={{ __html: themeScript }}
    />
  );
}
