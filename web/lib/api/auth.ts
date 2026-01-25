/**
 * API методы для авторизации
 * 
 * Регистрация, вход, выход, получение профиля
 */

import { post, get, saveTokens, clearTokens } from './client';

// === Типы ===

export interface User {
  id: number;
  email: string;
  name: string | null;
  plan: 'free' | 'pro' | 'team' | 'enterprise';
  tokens_balance: number;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
}

export interface RegisterData {
  email: string;
  password: string;
  name?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

// === API методы ===

/**
 * Регистрация нового пользователя
 * 
 * @param data - email, password, name (опционально)
 * @returns Данные пользователя и токены
 */
export async function register(data: RegisterData): Promise<AuthResponse> {
  const response = await post<AuthResponse>('/auth/register', data);
  
  // Сохраняем токены автоматически
  saveTokens(response.tokens.access_token, response.tokens.refresh_token);
  
  return response;
}

/**
 * Вход в систему
 * 
 * @param data - email и password
 * @returns Данные пользователя и токены
 */
export async function login(data: LoginData): Promise<AuthResponse> {
  const response = await post<AuthResponse>('/auth/login', data);
  
  // Сохраняем токены автоматически
  saveTokens(response.tokens.access_token, response.tokens.refresh_token);
  
  return response;
}

/**
 * Выход из системы
 * Удаляет токены из localStorage
 */
export function logout(): void {
  clearTokens();
}

/**
 * Получить текущего пользователя
 * 
 * @returns Данные пользователя или null если не авторизован
 */
export async function getCurrentUser(): Promise<User | null> {
  try {
    return await get<User>('/auth/me', true);
  } catch {
    return null;
  }
}

/**
 * Проверить, авторизован ли пользователь
 * (есть ли токен в localStorage)
 */
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
}
