---
name: xbasis-patterns
description: Code patterns and conventions for xbasis platform development. Auto-loaded when working on src/ or web/ files.
---

# xbasis Code Patterns

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND                            │
│                   (Next.js + React)                      │
│  Landing │ Dashboard │ Project Editor │ Billing         │
└─────────────────────────┬───────────────────────────────┘
                          │ REST API
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      BACKEND                             │
│                      (FastAPI)                           │
│  Auth │ Projects │ AI Gateway │ Deploy │ Billing        │
└───────────────────────────────────────────────────────────┘
```

## Backend Patterns (Python/FastAPI)

### File Organization
```
src/api/
├── routes/
│   └── {resource}.py      # One file per resource
├── models/
│   └── {resource}.py      # SQLAlchemy models
├── schemas/
│   └── {resource}.py      # Pydantic schemas (Create, Update, Response)
└── services/
    └── {resource}_service.py  # Business logic
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|--------|
| Files | snake_case | `user_service.py` |
| Classes | PascalCase | `UserCreate` |
| Functions | snake_case | `get_user_by_id` |
| Constants | UPPER_SNAKE | `MAX_TOKENS` |
| Tables | snake_case plural | `users`, `ai_sessions` |

### Error Handling
```python
from fastapi import HTTPException, status

# Use specific status codes
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)

# For validation errors, let Pydantic handle it
```

## Frontend Patterns (Next.js)

### File Organization
```
web/
├── app/
│   ├── (auth)/           # Route groups for layouts
│   │   ├── login/
│   │   └── register/
│   └── (dashboard)/
│       ├── projects/
│       └── settings/
├── components/
│   ├── ui/               # shadcn/ui (don't modify)
│   ├── forms/            # Form components
│   └── layout/           # Layout components
└── lib/
    ├── api.ts            # API client
    └── utils.ts          # Helpers
```

### Component Structure
```tsx
// 1. Imports (React, then external, then internal)
"use client"; // if needed

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { formatDate } from "@/lib/utils";

// 2. Types
interface Props {
  // ...
}

// 3. Component
export function ComponentName({ prop }: Props) {
  // hooks first
  // handlers
  // render
}
```

### Tailwind Conventions
```tsx
// Use design system values
<div className="p-4 md:p-6">           {/* Responsive padding */}
<div className="text-foreground">       {/* Theme colors */}
<div className="flex flex-col gap-4">   {/* Flex with gap */}
```

## API Communication

### Frontend → Backend
```typescript
// lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function apiClient<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}
```

## Database Patterns

### Model Definition
```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
```
