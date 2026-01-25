# xBasis

**AI-Powered Development Platform** — полная платформа для создания и развертывания приложений с AI-ассистентом.

## 🚀 Возможности

- **AI Чат** — Claude-powered ассистент для разработки
- **Cloud IDE** — редактор кода, база данных, live preview
- **One-Click Deploy** — деплой на Railway в один клик
- **Database Sandbox** — изолированные PostgreSQL схемы для каждого проекта
- **Billing** — Paddle интеграция с токенами и подписками

## 🏗️ Архитектура

```
xbasis/
├── api/                    # FastAPI Backend
│   ├── main.py            # Entry point
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── models/            # Pydantic models
│   └── database.py        # PostgreSQL connection
├── web/                    # Next.js Frontend
│   ├── app/               # App Router pages
│   ├── components/        # React components
│   ├── lib/               # Utilities & API client
│   └── contexts/          # React contexts
├── docs/                   # Documentation
└── tests/                  # Test suite
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** — async Python framework
- **PostgreSQL** — database with per-project schemas
- **JWT** — authentication
- **Anthropic Claude** — AI API
- **Paddle** — payments
- **Docker** — sandboxed code execution

### Frontend
- **Next.js 14** — React framework with App Router
- **TypeScript** — type safety
- **Tailwind CSS** — styling
- **shadcn/ui** — UI components
- **Radix UI** — headless components

## 📦 Установка

### Backend

```bash
cd api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Заполните .env
uvicorn main:app --reload
```

### Frontend

```bash
cd web
npm install
cp .env.example .env.local
# Заполните .env.local
npm run dev
```

## 🔐 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost/xbasis
JWT_SECRET=your-secret-key
ANTHROPIC_API_KEY=sk-ant-...
PADDLE_API_KEY=...
PADDLE_WEBHOOK_SECRET=...
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PADDLE_CLIENT_TOKEN=...
```

## 🧪 Тесты

```bash
cd api
pytest tests/ -v
```

## 📖 API Documentation

После запуска backend доступно:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Подробная документация: [docs/API.md](docs/API.md)

## 🚀 Deploy

### Railway

1. Создайте проект на Railway
2. Добавьте PostgreSQL service
3. Подключите GitHub репозиторий
4. Добавьте environment variables
5. Deploy!

## 📋 Features Roadmap

- [x] Auth (JWT)
- [x] Projects CRUD
- [x] AI Chat
- [x] Billing (Paddle)
- [x] Database Sandbox
- [x] Deploy Service
- [ ] WebSocket realtime
- [ ] Team collaboration
- [ ] Custom domains

## 🔒 152-ФЗ Compliance

Платформа разработана с учетом требований 152-ФЗ:
- Изоляция данных проектов (PostgreSQL schemas)
- Журналирование доступа
- Шифрование в transit и at rest
- Контроль доступа на уровне ролей

Подробнее: [docs/COMPLIANCE.md](docs/COMPLIANCE.md)

## 📄 License

MIT © 2025 xBasis Team
