'use client';

/**
 * Error Boundary
 * 
 * Ловит ошибки в дочерних компонентах и показывает fallback UI.
 * Использует React Error Boundary pattern для class component
 * + wrapper для использования в App Router.
 */

import React, { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

// === Типы ===

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

// === Class Component (React требует class для Error Boundary) ===

class ErrorBoundaryClass extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Логируем ошибку
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Вызываем callback если передан
    this.props.onError?.(error, errorInfo);
    
    // Здесь можно отправить ошибку в систему мониторинга
    // например: Sentry.captureException(error);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      // Кастомный fallback
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Дефолтный fallback
      return (
        <div className="min-h-[400px] flex items-center justify-center p-4">
          <Card className="max-w-md w-full">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
                <AlertTriangle className="h-6 w-6 text-destructive" />
              </div>
              <CardTitle>Что-то пошло не так</CardTitle>
              <CardDescription>
                Произошла непредвиденная ошибка. Попробуйте обновить страницу.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Детали ошибки (только в dev) */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="rounded-lg bg-muted p-3">
                  <p className="text-xs font-mono text-muted-foreground break-all">
                    {this.state.error.message}
                  </p>
                </div>
              )}
              
              <div className="flex flex-col gap-2 sm:flex-row">
                <Button 
                  onClick={this.handleReset} 
                  className="flex-1"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Попробовать снова
                </Button>
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => window.location.href = '/dashboard'}
                >
                  <Home className="mr-2 h-4 w-4" />
                  На главную
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// === Экспорт ===

export { ErrorBoundaryClass as ErrorBoundary };

// === Хук для использования с Suspense ===

/**
 * Компонент-обёртка для удобного использования
 * 
 * @example
 * <ErrorBoundaryWrapper>
 *   <MyComponent />
 * </ErrorBoundaryWrapper>
 */
export function ErrorBoundaryWrapper({ 
  children,
  onError,
}: { 
  children: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}) {
  return (
    <ErrorBoundaryClass onError={onError}>
      {children}
    </ErrorBoundaryClass>
  );
}

// === Fallback компоненты ===

/**
 * Минималистичный fallback для небольших секций
 */
export function ErrorFallbackSmall({ 
  onRetry 
}: { 
  onRetry?: () => void 
}) {
  return (
    <div className="flex flex-col items-center justify-center p-4 text-center">
      <AlertTriangle className="h-8 w-8 text-destructive mb-2" />
      <p className="text-sm text-muted-foreground mb-2">
        Не удалось загрузить
      </p>
      {onRetry && (
        <Button variant="ghost" size="sm" onClick={onRetry}>
          <RefreshCw className="mr-2 h-3 w-3" />
          Повторить
        </Button>
      )}
    </div>
  );
}

/**
 * Fallback для полной страницы
 */
export function ErrorFallbackPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-lg w-full">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
            <AlertTriangle className="h-8 w-8 text-destructive" />
          </div>
          <CardTitle className="text-2xl">Упс! Ошибка</CardTitle>
          <CardDescription>
            Что-то пошло не так. Наша команда уже работает над исправлением.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col gap-2">
            <Button onClick={() => window.location.reload()}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Обновить страницу
            </Button>
            <Button 
              variant="outline"
              onClick={() => window.location.href = '/'}
            >
              <Home className="mr-2 h-4 w-4" />
              Вернуться на главную
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
