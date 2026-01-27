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

## 🤖 Агенты (вызываются автоматически)

| Агент | Специализация | Триггеры |
|-------|---------------|----------|
| **orchestrator** | Координация | Всегда активен |
| **backend** | FastAPI, Python, API | endpoint, model, route, service |
| **frontend** | Next.js, React, UI | component, page, UI, кнопка, форма |
| **database** | SQLAlchemy, миграции | migration, schema, table, column |
| **ai** | AI Gateway, промпты | Claude, tokens, generation, prompt |
| **devops** | Docker, CI/CD, деплой | deploy, Docker, Railway, CI |
| **qa** | Тесты, покрытие | test, pytest, coverage, edge case |
| **docs** | Документация | README, documentation, guide |
| **reviewer** | Code review | review, commit, check, PR |

### Как это работает

```
Ты: "Добавь endpoint для списка проектов"
         │
         ▼
    orchestrator анализирует
         │
         ▼
    @backend создаёт endpoint
         │
         ▼
    orchestrator собирает результат
         │
         ▼
Тебе: "Готово. Создан GET /api/projects..."
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
│   ├── agents/            # 9 специализированных агентов
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
