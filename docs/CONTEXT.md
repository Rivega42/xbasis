# xBasis — Platform Context

## Что это

**xBasis** — платформа для создания и деплоя проектов с AI-ассистентом. От идеи до production за дни, не месяцы.

Пользователь описывает что хочет → AI генерирует код из готовых модулей → автоматический деплой → live продукт.

## Бизнес-модель

- **Подписка**: Free / Pro ($29) / Team ($99)
- **Токены AI**: Pay-as-you-go с наценкой 30%
- **Compute**: $5-20/проект/мес
- **Домены**: $12-15/год

## Стек

| Слой | Технология |
|------|------------|
| **Frontend** | Next.js 14, React, Tailwind, shadcn/ui |
| **Backend API** | FastAPI (Python) |
| **Database** | PostgreSQL (Supabase) |
| **Cache** | Redis |
| **Auth** | JWT (свой) |
| **Billing** | Paddle |
| **AI** | Claude API, OpenAI API (fallback) |
| **Deploy** | Railway (интеграция), Vercel (frontend) |
| **Domains** | Cloudflare API |

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                            │
│                   (Next.js + React)                      │
│  Landing │ Dashboard │ Project Editor │ Billing         │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      API GATEWAY                         │
│                      (FastAPI)                           │
│  Auth │ Projects │ AI Gateway │ Deploy │ Billing        │
└───┬─────────┬─────────┬─────────┬─────────┬─────────────┘
    │         │         │         │         │
    ▼         ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│  JWT  │ │Postgres│ │Claude │ │Railway│ │Paddle │
│ Auth  │ │  DB   │ │OpenAI │ │  API  │ │  API  │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘
```

## Текущий статус

**MVP COMPLETE** ✅

- Auth: 100%
- Billing: 100%
- Dashboard: 100%
- Projects: 100%
- AI Gateway: 100%
- Deploy: 100%
- Landing: 100%
- Testing: 100%
- CI/CD: 100%

## Ключевые сущности

| Сущность | Описание |
|----------|----------|
| **User** | id, email, plan, tokens_balance, created_at |
| **Project** | id, user_id, name, status, repo_url, deploy_url |
| **Deployment** | id, project_id, environment, status, url |
| **AISession** | id, project_id, tokens_used, messages |
| **Transaction** | id, user_id, type, amount, tokens |

## Команда

- **Роман** — Product, Marketing, Architecture

## Ссылки

- Репозиторий: https://github.com/Rivega42/xbasis
- Production: xbasis.app (план)
