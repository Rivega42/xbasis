'use client';

/**
 * Theme Toggle
 * 
 * Компонент для переключения темы.
 * Компактная версия для header.
 */

import { Sun, Moon, Monitor } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/contexts';
import { cn } from '@/lib/utils';

export function ThemeToggle() {
  const { theme, setTheme, resolvedTheme } = useTheme();

  // Cycle through themes: light -> dark -> system -> light
  function cycleTheme() {
    if (theme === 'light') setTheme('dark');
    else if (theme === 'dark') setTheme('system');
    else setTheme('light');
  }

  const Icon = theme === 'system' ? Monitor : resolvedTheme === 'dark' ? Moon : Sun;

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={cycleTheme}
      className="h-9 w-9"
      title={`Тема: ${theme === 'system' ? 'системная' : theme === 'dark' ? 'тёмная' : 'светлая'}`}
    >
      <Icon className="h-4 w-4" />
    </Button>
  );
}

/**
 * Theme Toggle с выпадающим меню
 * Для Settings страницы или более детального выбора
 */
export function ThemeSelect() {
  const { theme, setTheme } = useTheme();

  const themes = [
    { id: 'light' as const, label: 'Светлая', icon: Sun },
    { id: 'dark' as const, label: 'Тёмная', icon: Moon },
    { id: 'system' as const, label: 'Системная', icon: Monitor },
  ];

  return (
    <div className="grid grid-cols-3 gap-2">
      {themes.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => setTheme(id)}
          className={cn(
            'flex flex-col items-center gap-2 rounded-lg border p-4 transition-colors',
            theme === id ? 'border-primary bg-primary/5' : 'hover:bg-muted'
          )}
        >
          <Icon className="h-5 w-5" />
          <span className="text-sm">{label}</span>
        </button>
      ))}
    </div>
  );
}
