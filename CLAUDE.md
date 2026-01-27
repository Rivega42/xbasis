# CLAUDE.md — xbasis Development Guide

> Этот файл читается ПЕРВЫМ в начале каждой сессии

---

## 🚀 Быстрый старт

### Обязательное чтение
```
docs/CONTEXT.md      # Что за проект, стек, архитектура
docs/FEATURES.md     # Что готово, что в работе
docs/SESSION.md      # Последняя сессия, текущие TODO
```

### По необходимости
```
docs/DECISIONS.md    # История архитектурных решений
docs/PROBLEMS.md     # Известные проблемы
docs/API.md          # API документация
CHANGELOG.md         # История версий
```

---

## 🤖 Система агентов (автоматическая)

### Иерархия

```
ТЫ (задача/вопрос)
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│  Это глобальное изменение / новая интеграция / архитектура?│
└───────────────────────────────────────────────────────────┘
        │                           │
       ДА                          НЕТ
        │                           │
        ▼                           │
   @architect                       │
   (планирует)                      │
        │                           │
        └───────────┬───────────────┘
                    ▼
              @orchestrator
              (координирует)
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
@backend       @frontend        @database
@devops          @qa              @ai
@docs         @reviewer          ...
```

### Все агенты

| Агент | Роль | Когда вызывается |
|-------|------|------------------|
| **@architect** | Стратег, планирует крупные изменения | интеграция, архитектура, "как лучше сделать" |
| **@orchestrator** | Координатор, выполняет план | каждая задача |
| **@backend** | FastAPI, Python, API | endpoint, model, route |
| **@frontend** | Next.js, React, UI | component, page, кнопка |
| **@database** | SQLAlchemy, миграции | migration, schema, table |
| **@ai** | AI Gateway, промпты | Claude, tokens, prompt |
| **@devops** | Docker, CI/CD, деплой | deploy, Docker, Railway |
| **@qa** | Тесты, покрытие | test, pytest, coverage |
| **@docs** | Документация | README, documentation |
| **@reviewer** | Code review | review, commit, PR |

### Как это работает

**Пример 1: Простая задача**
```
Ты: "Добавь поле description в модель Project"

→ @orchestrator видит: database + backend задача
→ @database: создаёт миграцию
→ @backend: обновляет schema
→ Тебе: "Готово, запусти alembic upgrade head"
```

**Пример 2: Глобальное изменение**
```
Ты: "Нужно добавить интеграцию со Stripe"

→ @orchestrator видит: это архитектурное решение
→ @architect получает задачу
   → консультируется с @backend, @database, @devops
   → создаёт план крупными блоками
   → записывает ADR в DECISIONS.md
   → передаёт план @orchestrator
→ @orchestrator выполняет план через агентов
→ Тебе: "Готово, вот что изменилось..."
```

---

## 📝 Подключённые Skills

@.claude/skills/xbasis-patterns/SKILL.md
@.claude/skills/shipkit-workflow/SKILL.md

---

## 📁 Структура проекта

```
xbasis/
├── CLAUDE.md              ← ТЫ ЗДЕСЬ
├── .claude/
│   ├── settings.json      # Hooks (автоформат, валидация)
│   ├── agents/            # 10 специализированных агентов
│   └── skills/            # Переиспользуемые знания
├── docs/                  # ShipKit документация
├── src/api/               # FastAPI backend
├── web/                   # Next.js frontend
└── tests/                 # Тесты
```

---

## ⚡ Команды

### Backend
```bash
docker-compose up -d          # Запуск
docker-compose logs -f api    # Логи
pytest                        # Тесты
open http://localhost:8000/docs  # API Docs
```

### Frontend
```bash
cd web && npm run dev         # Development
cd web && npm run build       # Build
```

### Database
```bash
alembic upgrade head          # Применить миграции
alembic revision --autogenerate -m "description"  # Новая миграция
```

### Git
```bash
git commit -m "feat: new feature"
git commit -m "fix: bug fix"
git commit -m "docs: documentation"
```

---

## 🔄 Чеклист конца сессии

```
□ docs/SESSION.md  — что сделано, TODO на следующую сессию
□ docs/FEATURES.md — обновить статусы функций
□ docs/DECISIONS.md — если были архитектурные решения
□ docs/PROBLEMS.md — если нашли баги
□ git commit docs/
```

---

## 🚧 Не делай

- Не начинай кодить без плана
- Не меняй стек без записи в DECISIONS.md
- Не заканчивай сессию без обновления SESSION.md
- Не пропускай @reviewer для важных изменений
- Не делай глобальные изменения без @architect
