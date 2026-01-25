'use client';

/**
 * Providers
 * 
 * Объединяет все провайдеры контекстов в один компонент.
 * Используется в корневом layout для обёртки всего приложения.
 */

import { AuthProvider, ToastProvider, ThemeProvider } from '@/contexts';

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          {children}
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
