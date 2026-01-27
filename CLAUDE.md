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

## 🤖 Agents & Skills

### Доступные агенты
| Агент | Когда использовать |
|-------|-------------------|
| `@backend` | API, FastAPI, база данных, бизнес-логика |
| `@frontend` | Next.js, компоненты, UI, стили |
| `@reviewer` | Code review перед коммитом |

### Подключённые skills
@.claude/skills/xbasis-patterns/SKILL.md
@.claude/skills/shipkit-workflow/SKILL.md

---

## 📁 Структура проекта

```
xbasis/
├── CLAUDE.md              ← ТЫ ЗДЕСЬ
├── .claude/
│   ├── settings.json      # Hooks (auto-format, validation)
│   ├── agents/            # Специализированные агенты
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
cd web
npm run dev      # Development
npm run build    # Build
npm run lint     # Lint
```

### Git
```bash
# Commit conventions
git commit -m "feat: new feature"
git commit -m "fix: bug fix"
git commit -m "docs: documentation"
git commit -m "refactor: code refactoring"
```

---

## 🎨 Конвенции

### Python (Backend)
- **Formatter:** Black + Ruff
- **Types:** Полная типизация (Pydantic)
- **Style:** async/await везде, snake_case

### TypeScript (Frontend)
- **Formatter:** Prettier + ESLint
- **Components:** shadcn/ui + Tailwind
- **Style:** PascalCase компоненты, camelCase функции

---

## 🎭 Режим Архитектор → Агенты

```
┌──────────────────────────────────────────────────────────┐
│                      АРХИТЕКТОР                           │
│  1. Анализ задачи                                        │
│  2. Выбор агентов (@backend, @frontend, @reviewer)       │
│  3. Распределение работы                                 │
│  4. Приёмка результатов                                  │
└─────────────────────────────┬────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   @backend              @frontend              @reviewer
   (API, DB)             (UI, styles)           (quality)
```

### Правила
- ✅ Можно параллельно: Backend + Frontend (разные файлы)
- ❌ Нельзя: Frontend зависит от нового API → сначала backend

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

## 🚫 Не делай

- Не начинай кодить без плана
- Не меняй стек без записи в DECISIONS.md
- Не заканчивай сессию без обновления SESSION.md
- Не пропускай code review для важных изменений
