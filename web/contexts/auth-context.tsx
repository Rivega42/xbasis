'use client';

/**
 * Auth Context
 * 
 * Глобальное состояние авторизации для всего приложения.
 * Предоставляет:
 * - Текущего пользователя
 * - Методы login, logout, register
 * - Состояние загрузки
 * 
 * @example
 * // В компоненте:
 * const { user, login, logout, isLoading } = useAuth();
 * 
 * if (isLoading) return <Spinner />;
 * if (!user) return <Redirect to="/login" />;
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  User,
  login as apiLogin,
  register as apiRegister,
  logout as apiLogout,
  getCurrentUser,
  isAuthenticated,
  LoginData,
  RegisterData,
} from '@/lib/api';

// === Типы ===

interface AuthContextValue {
  // Текущий пользователь (null если не авторизован)
  user: User | null;
  
  // Идёт ли загрузка (проверка токена при старте)
  isLoading: boolean;
  
  // Авторизован ли пользователь
  isAuthenticated: boolean;
  
  // Методы авторизации
  login: (data: LoginData) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  
  // Обновить данные пользователя
  refreshUser: () => Promise<void>;
}

// Создаём контекст с undefined по умолчанию
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// === Provider ===

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  // Состояние
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Загрузить текущего пользователя
   * Вызывается при монтировании и после входа
   */
  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch {
      setUser(null);
    }
  }, []);

  /**
   * Вход в систему
   */
  const login = useCallback(async (data: LoginData) => {
    const response = await apiLogin(data);
    setUser(response.user);
  }, []);

  /**
   * Регистрация
   */
  const register = useCallback(async (data: RegisterData) => {
    const response = await apiRegister(data);
    setUser(response.user);
  }, []);

  /**
   * Выход из системы
   */
  const logout = useCallback(() => {
    apiLogout();
    setUser(null);
  }, []);

  /**
   * Проверяем авторизацию при загрузке приложения
   */
  useEffect(() => {
    const initAuth = async () => {
      setIsLoading(true);
      
      // Если есть токен - пробуем получить пользователя
      if (isAuthenticated()) {
        await refreshUser();
      }
      
      setIsLoading(false);
    };

    initAuth();
  }, [refreshUser]);

  // Значение контекста
  const value: AuthContextValue = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// === Hook ===

/**
 * Хук для доступа к контексту авторизации
 * 
 * @throws Error если используется вне AuthProvider
 * 
 * @example
 * function ProfileButton() {
 *   const { user, logout } = useAuth();
 *   
 *   if (!user) return <LoginButton />;
 *   
 *   return (
 *     <button onClick={logout}>
 *       {user.email} - Выйти
 *     </button>
 *   );
 * }
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth должен использоваться внутри AuthProvider');
  }
  
  return context;
}
