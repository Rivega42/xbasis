/**
 * API методы для работы с проектами
 * 
 * CRUD операции, деплой, переменные окружения
 */

import { get, post, put, del } from './client';

// === Типы ===

export type ProjectType = 'web' | 'api' | 'bot' | 'static';
export type ProjectStatus = 'draft' | 'building' | 'deployed' | 'failed' | 'archived';

export interface Project {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  type: ProjectType;
  status: ProjectStatus;
  owner_id: number;
  repo_url: string | null;
  branch: string;
  preview_url: string | null;
  production_url: string | null;
  custom_domain: string | null;
  railway_project_id: string | null;
  context_summary: string | null;
  created_at: string;
  updated_at: string;
  last_deployed_at: string | null;
}

export interface CreateProjectData {
  name: string;
  description?: string;
  type: ProjectType;
}

export interface UpdateProjectData {
  name?: string;
  description?: string;
  custom_domain?: string;
}

export interface Deployment {
  id: number;
  project_id: number;
  environment: 'preview' | 'production';
  status: 'pending' | 'building' | 'live' | 'failed' | 'cancelled';
  url: string | null;
  commit_sha: string | null;
  build_logs: string | null;
  created_at: string;
  finished_at: string | null;
}

// === API методы ===

/**
 * Получить список всех проектов пользователя
 */
export async function getProjects(): Promise<Project[]> {
  return get<Project[]>('/projects', true);
}

/**
 * Получить проект по ID
 */
export async function getProject(id: number): Promise<Project> {
  return get<Project>(`/projects/${id}`, true);
}

/**
 * Создать новый проект
 * 
 * @param data - название, описание, тип
 * @returns Созданный проект
 */
export async function createProject(data: CreateProjectData): Promise<Project> {
  return post<Project>('/projects', data, true);
}

/**
 * Обновить проект
 */
export async function updateProject(id: number, data: UpdateProjectData): Promise<Project> {
  return put<Project>(`/projects/${id}`, data, true);
}

/**
 * Удалить проект
 */
export async function deleteProject(id: number): Promise<void> {
  return del(`/projects/${id}`, true);
}

/**
 * Получить переменные окружения проекта
 */
export async function getProjectEnv(id: number): Promise<Record<string, string>> {
  const response = await get<{ env_vars: Record<string, string> }>(`/projects/${id}/env`, true);
  return response.env_vars;
}

/**
 * Обновить переменные окружения проекта
 */
export async function updateProjectEnv(id: number, envVars: Record<string, string>): Promise<void> {
  return put(`/projects/${id}/env`, envVars, true);
}

// === Деплой ===

/**
 * Запустить деплой проекта
 * 
 * @param id - ID проекта
 * @param environment - 'preview' или 'production'
 */
export async function deployProject(
  id: number,
  environment: 'preview' | 'production' = 'preview'
): Promise<Deployment> {
  return post<Deployment>(`/deploy/${id}/deploy`, { environment }, true);
}

/**
 * Получить историю деплоев проекта
 */
export async function getDeployments(projectId: number): Promise<Deployment[]> {
  return get<Deployment[]>(`/deploy/${projectId}/deployments`, true);
}

/**
 * Получить конкретный деплой
 */
export async function getDeployment(projectId: number, deploymentId: number): Promise<Deployment> {
  return get<Deployment>(`/deploy/${projectId}/deployments/${deploymentId}`, true);
}

/**
 * Отменить деплой
 */
export async function cancelDeployment(projectId: number, deploymentId: number): Promise<void> {
  return del(`/deploy/${projectId}/deployments/${deploymentId}`, true);
}
