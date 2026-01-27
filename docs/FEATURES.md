# xBasis Features

> Реестр всех функций проекта

## 📊 Прогресс

### MVP v1 (Basic) — 100% ✅

| Модуль | Готово | Всего | % |
|--------|--------|-------|---|
| Auth | 5 | 5 | 100% ✅ |
| Billing | 6 | 6 | 100% ✅ |
| Dashboard | 5 | 5 | 100% ✅ |
| Projects | 7 | 7 | 100% ✅ |
| AI Gateway | 6 | 6 | 100% ✅ |
| Deploy | 5 | 5 | 100% ✅ |
| Landing | 4 | 4 | 100% ✅ |
| **TOTAL** | **62** | **62** | **100%** |

### MVP v2 (Live Preview + DB) — 79%

| Модуль | Готово | Всего | % |
|--------|--------|-------|---|
| Sandbox API | 2 | 2 | 100% ✅ |
| Database API | 2 | 2 | 100% ✅ |
| Live Preview UI | 3 | 3 | 100% ✅ |
| Database Panel UI | 4 | 4 | 100% ✅ |
| Code Editor | 3 | 3 | 100% ✅ |
| Infrastructure | 0 | 4 | 0% |
| **TOTAL** | **15** | **19** | **79%** |

### MVP v3 (AI Skills System) — 0% 🔄

| Модуль | Готово | Всего | % |
|--------|--------|-------|---|
| Skills Loader | 0 | 3 | 0% |
| Context Builder | 0 | 4 | 0% |
| Hooks System | 0 | 3 | 0% |
| Project Templates | 0 | 4 | 0% |
| **TOTAL** | **0** | **14** | **0%** |

---

## 🚀 ROADMAP

### Phase 1: Frontend Components ✅ DONE
- LivePreview component
- DatabasePanel component
- CodeEditor component
- Project IDE Page

### Phase 2: Infrastructure 🔲 PLANNED
- Docker Setup
- Routing & SSL
- Servers (РФ, 152-ФЗ)

### Phase 3: Payments 🔲 PLANNED
- ЮKassa интеграция
- Планы подписки

### Phase 4: AI Skills System 🔄 IN PROGRESS
- Skills система для AI генерации
- Context Builder для проектов
- Hooks для валидации кода
- Project Templates с preset'ами

---

## 🤖 AI Skills System (Phase 4)

> Цель: Пользователь приходит и творит, а не настраивает

### Skills Loader
- 🔲 `src/api/ai/skills/loader.py` — загрузка skills по типу проекта
- 🔲 `src/api/ai/skills/base/common.md` — общие правила генерации
- 🔲 Автоматический выбор skills по шаблону проекта

### Context Builder  
- 🔲 `src/api/ai/context_builder.py` — сборка контекста
- 🔲 Project info injection (name, template, files)
- 🔲 Conversation history (последние N сообщений)
- 🔲 Skills injection по типу проекта

### Hooks System
- 🔲 `src/api/ai/hooks/pre_hooks.py` — валидация до генерации
- 🔲 `src/api/ai/hooks/post_hooks.py` — lint/format после генерации
- 🔲 Security validation (no secrets, XSS protection)

### Project Templates
- 🔲 SaaS Starter template
- 🔲 Landing Page template
- 🔲 API Backend template
- 🔲 Template preset configurations

### Skills по типам проектов

| Шаблон | Skills |
|--------|--------|
| SaaS | nextjs, tailwind, auth, database, api |
| Landing | nextjs, tailwind, seo, forms |
| API | fastapi, database, auth, validation |
| Custom | common (базовые правила) |

---

## 💰 Оценка инфраструктуры (РФ)

| Компонент | Стоимость/мес |
|-----------|---------------|
| Main Server (4 CPU, 8GB) | ~4,000 ₽ |
| Sandbox Server (8 CPU, 16GB) | ~7,000 ₽ |
| PostgreSQL (managed/self) | ~0-3,000 ₽ |
| Domain + SSL | ~100 ₽ |
| **ИТОГО** | **~12-15K ₽/мес** |
