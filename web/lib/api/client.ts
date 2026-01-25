/**
 * API Клиент для ShipKit
 * 
 * Обёртка над fetch с автоматической обработкой:
 * - JWT токенов (добавление в заголовки)
 * - Обновление токенов при истечении
 * - Обработка ошибок
 * - Типизация ответов
 */

// Базовый URL API (из переменных окружения или localhost)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Типы ошибок API
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(data?.detail || statusText);
    this.name = 'ApiError';
  }
}

// Тип для опций запроса
interface RequestOptions extends RequestInit {
  // Нужна ли авторизация для этого запроса
  auth?: boolean;
}

/**
 * Получить access token из localStorage
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * Получить refresh token из localStorage
 */
export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('refresh_token');
}

/**
 * Сохранить токены в localStorage
 */
export function saveTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
}

/**
 * Удалить токены из localStorage (при выходе)
 */
export function clearTokens(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

/**
 * Обновить access token используя refresh token
 * Возвращает true если обновление успешно
 */
async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Refresh token тоже истёк - нужен повторный вход
      clearTokens();
      return false;
    }

    const data = await response.json();
    saveTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

/**
 * Основная функция для API запросов
 * 
 * @param endpoint - путь API (например: '/auth/login')
 * @param options - опции fetch + флаг auth
 * @returns Promise с данными ответа
 * 
 * @example
 * // GET запрос без авторизации
 * const plans = await apiClient('/billing/plans');
 * 
 * @example
 * // POST запрос с авторизацией
 * const project = await apiClient('/projects', {
 *   method: 'POST',
 *   auth: true,
 *   body: JSON.stringify({ name: 'My Project' })
 * });
 */
export async function apiClient<T = any>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { auth = false, headers: customHeaders, ...fetchOptions } = options;

  // Формируем заголовки
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...customHeaders,
  };

  // Добавляем токен авторизации если нужно
  if (auth) {
    const token = getAccessToken();
    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }
  }

  // Выполняем запрос
  let response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  });

  // Если 401 (Unauthorized) и есть refresh token - пробуем обновить
  if (response.status === 401 && auth) {
    const refreshed = await refreshAccessToken();
    
    if (refreshed) {
      // Повторяем запрос с новым токеном
      const newToken = getAccessToken();
      (headers as Record<string, string>)['Authorization'] = `Bearer ${newToken}`;
      
      response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...fetchOptions,
        headers,
      });
    }
  }

  // Обрабатываем ответ
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = null;
    }
    throw new ApiError(response.status, response.statusText, errorData);
  }

  // Для 204 No Content возвращаем null
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// === Удобные методы для типичных запросов ===

/**
 * GET запрос
 */
export function get<T = any>(endpoint: string, auth = false): Promise<T> {
  return apiClient<T>(endpoint, { method: 'GET', auth });
}

/**
 * POST запрос
 */
export function post<T = any>(endpoint: string, data: any, auth = false): Promise<T> {
  return apiClient<T>(endpoint, {
    method: 'POST',
    auth,
    body: JSON.stringify(data),
  });
}

/**
 * PUT запрос
 */
export function put<T = any>(endpoint: string, data: any, auth = false): Promise<T> {
  return apiClient<T>(endpoint, {
    method: 'PUT',
    auth,
    body: JSON.stringify(data),
  });
}

/**
 * DELETE запрос
 */
export function del<T = any>(endpoint: string, auth = false): Promise<T> {
  return apiClient<T>(endpoint, { method: 'DELETE', auth });
}
