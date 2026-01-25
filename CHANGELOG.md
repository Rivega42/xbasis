# Changelog

All notable changes to xBasis will be documented in this file.

## [0.1.0] - 2026-01-25

### Added

#### Backend (FastAPI)
- **Auth Module** - JWT authentication with access/refresh tokens
- **Projects Module** - Full CRUD, project types, env vars
- **AI Gateway** - Anthropic Claude, OpenAI GPT, streaming
- **Billing Module** - Plans, Paddle integration
- **Deploy Module** - Railway, GitHub webhooks
- **Database Module** - PostgreSQL schemas per project
- **Sandbox Module** - Docker containers for live preview

#### Frontend (Next.js 14)
- Landing Page with pricing
- Authentication (login, register)
- Dashboard with projects list
- Project IDE (editor + preview + database)
- AI Chat interface
- Dark mode

#### Infrastructure
- Docker Compose for local dev
- CI/CD with GitHub Actions
- Tests (pytest + Jest)

### Documentation
- CLAUDE.md with AI instructions
- API documentation
- Architecture decisions

---

## Development Stats

- **Total sessions:** 10
- **Lines of code:** ~15,000
- **Backend endpoints:** 30+
- **Frontend pages:** 10
- **Tests:** 31
