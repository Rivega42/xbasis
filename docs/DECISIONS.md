# Architecture Decision Records

> История архитектурных решений проекта xbasis

---

## ADR-001: Выбор стека

**Дата:** 2025-01-20
**Статус:** Accepted

### Контекст
Нужно выбрать технологии для MVP платформы.

### Решение
- **Frontend:** Next.js 14 + React + Tailwind + shadcn/ui
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL (Supabase)
- **AI:** Claude API + OpenAI (fallback)

### Причины
- Next.js: SSR, отличный DX, большое сообщество
- FastAPI: async, автодокументация, типизация
- PostgreSQL: надёжность, Supabase даёт managed решение

---

## ADR-002: JWT Auth vs Sessions

**Дата:** 2025-01-20
**Статус:** Accepted

### Контекст
Выбор механизма аутентификации.

### Решение
JWT с refresh tokens.

### Причины
- Stateless (масштабирование)
- Работает с мобильными приложениями
- Refresh tokens для безопасности

---

## ADR-003: Paddle vs Stripe

**Дата:** 2025-01-21
**Статус:** Accepted

### Контекст
Выбор платёжной системы.

### Решение
Paddle как Merchant of Record.

### Причины
- Paddle берёт на себя налоги
- Работает с РФ/СНГ
- Проще compliance

---

## ADR-004: ShipKit Documentation System

**Дата:** 2025-01-22
**Статус:** Accepted

### Контекст
Нужна система документации для AI-assisted разработки.

### Решение
ShipKit методология:
- `CLAUDE.md` — entry point
- `docs/CONTEXT.md` — что за проект
- `docs/FEATURES.md` — статус функций
- `docs/SESSION.md` — текущая сессия
- `docs/DECISIONS.md` — ADR
- `docs/PROBLEMS.md` — известные проблемы

### Причины
- Сохранение контекста между сессиями
- Структурированная работа с AI
- История решений

---

## ADR-005: Claude Code Agent System

**Дата:** 2026-01-27
**Статус:** Accepted
**Complexity:** M

### Контекст
Нужна система для эффективной AI-assisted разработки с автоматизацией.

### Решение
Иерархия агентов в `.claude/`:

```
@architect (стратегический)
     ↓
@orchestrator (тактический)
     ↓
@backend, @frontend, @database, @ai,
@devops, @qa, @docs, @reviewer
```

### Компоненты
- `.claude/agents/` — 10 специализированных агентов
- `.claude/skills/` — переиспользуемые знания
- `.claude/settings.json` — hooks для автоформатирования

### Роли
| Агент | Уровень | Роль |
|-------|---------|------|
| architect | Стратегический | Планирование, ADR, консультации |
| orchestrator | Тактический | Координация, выполнение |
| остальные | Исполнительный | Специализированные задачи |

### Причины
- Разделение ответственности
- Автоматическая оркестрация
- Масштабируемость команды агентов

---

## ADR-006: AI Skills System for Users

**Дата:** 2026-01-27
**Статус:** Proposed
**Complexity:** L

### Контекст
Пользователи xbasis должны "приходить и творить, а не настраивать". Нужна система которая автоматически предоставляет AI правильный контекст для генерации кода.

### Решение
Система Skills + Context Builder + Hooks в `src/api/ai/`:

```
src/api/ai/
├── skills/
│   ├── loader.py           # Загрузка skills по типу проекта
│   └── templates/          # Markdown файлы с правилами
├── context/
│   └── builder.py          # Сборка контекста для AI
└── hooks/
    ├── pre_hooks.py        # Валидация до генерации
    └── post_hooks.py       # Lint/format после
```

### Как работает
1. Пользователь создаёт проект (выбирает шаблон)
2. При каждом запросе к AI:
   - Context Builder собирает: project info + skills + history
   - Pre-hooks валидируют запрос
   - AI генерирует код
   - Post-hooks форматируют и проверяют

### Project Templates
| Шаблон | Skills | Описание |
|--------|--------|----------|
| SaaS | nextjs, auth, db, api | Полноценное SaaS приложение |
| Landing | nextjs, seo, forms | Лендинг с формами |
| API | fastapi, db, auth | Backend API |

### Преимущества
- Пользователь не настраивает AI
- Консистентный код
- Автоматическая валидация
- Расширяемость через новые skills

### Риски
| Риск | Митигация |
|------|----------|
| Слишком большой контекст | Лимит токенов, summarization |
| Skills устаревают | Версионирование, обновления |
| Конфликты между skills | Приоритеты, тестирование |

### План реализации
1. Skills Loader (2-3 часа)
2. Context Builder (2-3 часа)
3. Hooks System (2 часа)
4. Project Templates (2 часа)

**Estimated:** 8-10 часов

---

## Шаблон для новых ADR

```markdown
## ADR-XXX: Название

**Дата:** YYYY-MM-DD
**Статус:** Proposed | Accepted | Deprecated
**Complexity:** S | M | L | XL

### Контекст
Почему нужно это решение?

### Решение
Что решили делать?

### Альтернативы
- Вариант A: плюсы/минусы
- Вариант B: плюсы/минусы

### Последствия
- Позитивные: ...
- Негативные: ...
```
