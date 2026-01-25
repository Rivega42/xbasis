# xBasis — API Documentation

> Base URL: `http://localhost:8000` (dev) | `https://api.xbasis.app` (prod)

---

## Аутентификация

Все защищённые endpoints требуют заголовок:
```
Authorization: Bearer <access_token>
```

Токены:
- **Access token**: 15 минут
- **Refresh token**: 7 дней

---

## Endpoints

### 🔐 Auth

#### POST /auth/register
Регистрация нового пользователя.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "free",
    "tokens_balance": 10000
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

---

### 📦 Projects

#### GET /projects
Список проектов.

#### POST /projects
Создание проекта.

#### GET /projects/{id}
Получение проекта.

#### PUT /projects/{id}
Обновление проекта.

#### DELETE /projects/{id}
Удаление проекта.

---

### 🤖 AI

#### GET /ai/models
Доступные модели.

#### POST /ai/chat
Чат с AI.

#### GET /ai/usage
Статистика использования.

---

### 🚀 Deploy

#### POST /projects/{id}/deploy
Деплой проекта.

#### GET /projects/{id}/deployments
История деплоев.

---

### 💳 Billing

#### GET /billing/plans
Список планов.

#### POST /billing/checkout
Создание checkout сессии.

#### GET /billing/usage
Статистика использования.

---

## Интерактивная документация

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
