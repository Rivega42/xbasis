/**
 * API методы для биллинга
 * 
 * Планы, подписки, покупка токенов, статистика
 */

import { get, post } from './client';

// === Типы ===

export interface Plan {
  id: string;
  name: string;
  price: number;  // в центах
  interval: 'monthly' | 'yearly';
  tokens: number;
  projects: number;
  features: string[];
}

export interface BillingUsage {
  plan: string;
  tokens_balance: number;
  tokens_used_this_month: number;
  projects_count: number;
  projects_limit: number;
}

export interface CheckoutResponse {
  checkout_url: string;
}

export interface TokenPackage {
  tokens: number;
  price: number;  // в центах
}

// === API методы ===

/**
 * Получить список доступных планов
 */
export async function getPlans(): Promise<Plan[]> {
  return get<Plan[]>('/billing/plans');
}

/**
 * Создать сессию оплаты для подписки
 * 
 * @param planId - ID плана (pro, team)
 * @returns URL для редиректа на страницу оплаты Paddle
 */
export async function createCheckout(planId: string): Promise<CheckoutResponse> {
  return post<CheckoutResponse>('/billing/checkout', { plan_id: planId }, true);
}

/**
 * Купить дополнительные токены
 * 
 * @param tokens - количество токенов (10000, 50000, 100000)
 * @returns URL для оплаты
 */
export async function buyTokens(tokens: number): Promise<CheckoutResponse> {
  return post<CheckoutResponse>('/billing/tokens/buy', { tokens }, true);
}

/**
 * Получить статистику использования
 */
export async function getBillingUsage(): Promise<BillingUsage> {
  return get<BillingUsage>('/billing/usage', true);
}

/**
 * Отменить подписку
 */
export async function cancelSubscription(): Promise<void> {
  return post('/billing/cancel', {}, true);
}

// === Вспомогательные функции ===

/**
 * Форматировать цену для отображения
 * 
 * @param cents - цена в центах
 * @returns Строка вида "$29.00"
 */
export function formatPrice(cents: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(cents / 100);
}

/**
 * Доступные пакеты токенов
 */
export const TOKEN_PACKAGES: TokenPackage[] = [
  { tokens: 10_000, price: 500 },    // $5
  { tokens: 50_000, price: 2000 },   // $20
  { tokens: 100_000, price: 3500 },  // $35
];

/**
 * Получить название плана на русском
 */
export function getPlanDisplayName(planId: string): string {
  const names: Record<string, string> = {
    free: 'Бесплатный',
    pro: 'Pro',
    team: 'Team',
    enterprise: 'Enterprise',
  };
  return names[planId] || planId;
}
