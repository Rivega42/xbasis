"""
Tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient


class TestRegister:
    """Tests for user registration."""
    
    async def test_register_success(self, client: AsyncClient, user_credentials: dict):
        response = await client.post("/auth/register", json=user_credentials)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user, user_credentials: dict):
        user_credentials["email"] = test_user.email
        response = await client.post("/auth/register", json=user_credentials)
        assert response.status_code == 400
    
    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "password123",
            "name": "Test",
        })
        assert response.status_code == 422


class TestLogin:
    """Tests for user login."""
    
    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "wrongpassword",
        })
        assert response.status_code == 401


class TestMe:
    """Tests for current user endpoint."""
    
    async def test_me_authenticated(self, authenticated_client: AsyncClient, test_user):
        response = await authenticated_client.get("/auth/me")
        assert response.status_code == 200
        assert response.json()["email"] == test_user.email
    
    async def test_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/auth/me")
        assert response.status_code == 401
