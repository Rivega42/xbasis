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
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
    
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
        assert "tokens" in data
        assert "access_token" in data["tokens"]
    
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


class TestTokenRefresh:
    """Tests for token refresh with rotation."""

    async def test_refresh_success(self, client: AsyncClient, test_user):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123",
        })
        tokens = login_response.json()["tokens"]
        refresh_token = tokens["refresh_token"]

        # Refresh the token
        response = await client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        # New refresh token should be different (rotation)
        assert data["refresh_token"] != refresh_token

    async def test_refresh_old_token_rejected(self, client: AsyncClient, test_user):
        """Test that old refresh token is rejected after rotation (PROB-003 fix)."""
        # Login to get initial tokens
        login_response = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123",
        })
        old_refresh_token = login_response.json()["tokens"]["refresh_token"]

        # First refresh - should succeed
        response1 = await client.post("/auth/refresh", json={
            "refresh_token": old_refresh_token
        })
        assert response1.status_code == 200

        # Second refresh with OLD token - should fail (race condition fix)
        response2 = await client.post("/auth/refresh", json={
            "refresh_token": old_refresh_token
        })
        assert response2.status_code == 401
        assert "expired or revoked" in response2.json()["detail"]

    async def test_refresh_invalid_token(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post("/auth/refresh", json={
            "refresh_token": "invalid-token"
        })
        assert response.status_code == 401


class TestLogout:
    """Tests for logout with token invalidation."""

    async def test_logout_invalidates_tokens(self, client: AsyncClient, test_user):
        """Test that logout invalidates all refresh tokens."""
        # Login to get tokens
        login_response = await client.post("/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123",
        })
        tokens = login_response.json()["tokens"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Logout
        logout_response = await client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert logout_response.status_code == 200

        # Try to refresh with old token - should fail
        refresh_response = await client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_response.status_code == 401
