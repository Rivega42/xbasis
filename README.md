# 🚀 xBasis

**From Idea to Production in Days**

AI-powered SaaS builder. Опиши идею → получи готовый код → деплой в один клик.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100-green.svg)](https://fastapi.tiangolo.com/)

---

## ✨ Возможности

- 🤖 **AI-генерация кода** — Claude/GPT генерируют код по описанию
- 🏗️ **Готовые модули** — Auth, Billing, Dashboard из коробки
- 🚀 **One-click deploy** — Railway/Vercel интеграция
- 💳 **Биллинг** — Paddle для подписок и токенов
- 🌙 **Dark mode** — Светлая/тёмная/системная тема

---

## 🛠️ Стек

| Слой | Технология |
|------|------------|
| **Frontend** | Next.js 14, React, TypeScript |
| **UI** | Tailwind CSS, shadcn/ui |
| **Backend** | FastAPI, Python 3.11+ |
| **Database** | PostgreSQL, SQLAlchemy |
| **Auth** | JWT (access + refresh tokens) |
| **AI** | Anthropic Claude, OpenAI GPT |
| **Payments** | Paddle |
| **Deploy** | Railway, Docker |

---

## 🚀 Quick Start

### Требования

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Docker (опционально)

### 1. Клонирование

```bash
git clone https://github.com/Rivega42/xbasis.git
cd xbasis
```

### 2. Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cd src/api && uvicorn main:app --reload
```

API: http://localhost:8000 | Docs: http://localhost:8000/docs

### 3. Frontend

```bash
cd web && npm install
cp .env.example .env.local
npm run dev
```

App: http://localhost:3000

### 4. Docker

```bash
docker-compose up -d
```

---

## 📁 Структура

```
xbasis/
├── src/api/              # FastAPI backend
│   ├── auth/             # Авторизация
│   ├── projects/         # Проекты  
│   ├── ai/               # AI Gateway
│   ├── billing/          # Биллинг
│   ├── sandbox/          # Live Preview containers
│   └── database/         # DB Management
├── web/                  # Next.js frontend
│   ├── app/              # App Router
│   ├── components/       # React компоненты
│   └── lib/              # API клиент, hooks
└── docs/                 # Документация
```

---

## 📝 License

MIT License

---

**Built with ❤️ and AI**