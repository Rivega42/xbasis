'use client';

/**
 * Хуки для работы с авторизацией
 */

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts';

/**
 * Хук для защищённых страниц
 * 
 * Редиректит на /login если пользователь не авторизован
 * 
 * @param redirectTo - куда редиректить (по умолчанию /login)
 * @returns { user, isLoading }
 * 
 * @example
 * function DashboardPage() {
 *   const { user, isLoading } = useRequireAuth();
 *   
 *   if (isLoading) return <Spinner />;
 *   // user гарантированно существует здесь
 *   
 *   return <div>Привет, {user.name}!</div>;
 * }
 */
export function useRequireAuth(redirectTo = '/login') {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Ждём пока закончится проверка авторизации
    if (isLoading) return;
    
    // Если не авторизован - редирект
    if (!user) {
      router.push(redirectTo);
    }
  }, [user, isLoading, router, redirectTo]);

  return { user, isLoading };
}

/**
 * Хук для гостевых страниц (login, register)
 * 
 * Редиректит на /dashboard если пользователь уже авторизован
 * 
 * @param redirectTo - куда редиректить (по умолчанию /dashboard)
 * @returns { isLoading }
 * 
 * @example
 * function LoginPage() {
 *   const { isLoading } = useGuestOnly();
 *   
 *   if (isLoading) return <Spinner />;
 *   // Пользователь точно не авторизован
 *   
 *   return <LoginForm />;
 * }
 */
export function useGuestOnly(redirectTo = '/dashboard') {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Ждём пока закончится проверка
    if (isLoading) return;
    
    // Если уже авторизован - редирект в dashboard
    if (user) {
      router.push(redirectTo);
    }
  }, [user, isLoading, router, redirectTo]);

  return { isLoading };
}
