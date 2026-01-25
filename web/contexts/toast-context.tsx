'use client';

/**
 * Toast Context
 * 
 * Система уведомлений (toast) для всего приложения.
 * 
 * @example
 * const { toast } = useToast();
 * 
 * // Успех
 * toast({ title: 'Сохранено!', type: 'success' });
 * 
 * // Ошибка
 * toast({ title: 'Ошибка', description: 'Что-то пошло не так', type: 'error' });
 */

import React, { createContext, useContext, useState, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

// === Типы ===

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface Toast {
  id: string;
  title: string;
  description?: string;
  type: ToastType;
}

interface ToastOptions {
  title: string;
  description?: string;
  type?: ToastType;
  duration?: number;  // в миллисекундах
}

interface ToastContextValue {
  toasts: Toast[];
  toast: (options: ToastOptions) => void;
  dismiss: (id: string) => void;
}

// Создаём контекст
const ToastContext = createContext<ToastContextValue | undefined>(undefined);

// === Иконки и стили по типу ===

const toastConfig = {
  success: {
    icon: CheckCircle,
    className: 'bg-green-50 border-green-200 text-green-800',
    iconClassName: 'text-green-500',
  },
  error: {
    icon: AlertCircle,
    className: 'bg-red-50 border-red-200 text-red-800',
    iconClassName: 'text-red-500',
  },
  info: {
    icon: Info,
    className: 'bg-blue-50 border-blue-200 text-blue-800',
    iconClassName: 'text-blue-500',
  },
  warning: {
    icon: AlertTriangle,
    className: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    iconClassName: 'text-yellow-500',
  },
};

// === Provider ===

interface ToastProviderProps {
  children: React.ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  /**
   * Показать toast уведомление
   */
  const toast = useCallback((options: ToastOptions) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: Toast = {
      id,
      title: options.title,
      description: options.description,
      type: options.type || 'info',
    };

    setToasts((prev) => [...prev, newToast]);

    // Автоматически скрываем через duration (по умолчанию 5 сек)
    const duration = options.duration ?? 5000;
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, duration);
  }, []);

  /**
   * Закрыть toast по ID
   */
  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const value: ToastContextValue = {
    toasts,
    toast,
    dismiss,
  };

  return (
    <ToastContext.Provider value={value}>
      {children}
      
      {/* Toast контейнер */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
        {toasts.map((t) => {
          const config = toastConfig[t.type];
          const Icon = config.icon;
          
          return (
            <div
              key={t.id}
              className={cn(
                'flex items-start gap-3 rounded-lg border p-4 shadow-lg animate-slide-in',
                config.className
              )}
            >
              <Icon className={cn('h-5 w-5 shrink-0 mt-0.5', config.iconClassName)} />
              <div className="flex-1 min-w-0">
                <div className="font-medium">{t.title}</div>
                {t.description && (
                  <div className="mt-1 text-sm opacity-90">{t.description}</div>
                )}
              </div>
              <button
                onClick={() => dismiss(t.id)}
                className="shrink-0 opacity-50 hover:opacity-100"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

// === Hook ===

/**
 * Хук для показа toast уведомлений
 * 
 * @example
 * const { toast } = useToast();
 * 
 * async function handleSave() {
 *   try {
 *     await saveData();
 *     toast({ title: 'Сохранено!', type: 'success' });
 *   } catch (error) {
 *     toast({ 
 *       title: 'Ошибка сохранения', 
 *       description: error.message,
 *       type: 'error' 
 *     });
 *   }
 * }
 */
export function useToast(): ToastContextValue {
  const context = useContext(ToastContext);
  
  if (context === undefined) {
    throw new Error('useToast должен использоваться внутри ToastProvider');
  }
  
  return context;
}
