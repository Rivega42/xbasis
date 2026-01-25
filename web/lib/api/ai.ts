/**
 * API методы для AI ассистента
 * 
 * Чат, модели, использование токенов
 */

import { get, post } from './client';

// === Типы ===

export interface AIModel {
  id: string;
  name: string;
  provider: 'anthropic' | 'openai';
  input_price: number;  // цена за 1M токенов
  output_price: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  project_id?: number;
  messages: ChatMessage[];
  model?: string;
  max_tokens?: number;
}

export interface ChatResponse {
  id: string;
  content: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

export interface AIUsage {
  tokens_used_today: number;
  tokens_balance: number;
  plan: string;
}

// === API методы ===

/**
 * Получить список доступных AI моделей
 */
export async function getModels(): Promise<AIModel[]> {
  return get<AIModel[]>('/ai/models', true);
}

/**
 * Отправить сообщение в AI чат
 * 
 * @param request - сообщения, модель, project_id (опционально)
 * @returns Ответ от AI
 * 
 * @example
 * const response = await chat({
 *   messages: [{ role: 'user', content: 'Создай REST API' }],
 *   model: 'claude-sonnet-4-20250514',
 *   project_id: 1
 * });
 */
export async function chat(request: ChatRequest): Promise<ChatResponse> {
  return post<ChatResponse>('/ai/chat', request, true);
}

/**
 * Получить статистику использования AI
 */
export async function getAIUsage(): Promise<AIUsage> {
  return get<AIUsage>('/ai/usage', true);
}

// === Вспомогательные функции ===

/**
 * Форматировать количество токенов для отображения
 * 
 * @example
 * formatTokens(1500) // "1.5K"
 * formatTokens(1500000) // "1.5M"
 */
export function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) {
    return `${(tokens / 1_000_000).toFixed(1)}M`;
  }
  if (tokens >= 1_000) {
    return `${(tokens / 1_000).toFixed(1)}K`;
  }
  return tokens.toString();
}

/**
 * Рассчитать примерную стоимость запроса
 * 
 * @param inputTokens - токены ввода
 * @param outputTokens - токены вывода
 * @param model - модель (для получения цен)
 */
export function estimateCost(
  inputTokens: number,
  outputTokens: number,
  inputPrice: number,
  outputPrice: number
): number {
  const inputCost = (inputTokens / 1_000_000) * inputPrice;
  const outputCost = (outputTokens / 1_000_000) * outputPrice;
  return inputCost + outputCost;
}
