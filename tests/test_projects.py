"""
Tests for projects endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.fixture
def project_data() -> dict:
    return {
        "name": "Test Project",
        "description": "A test project",
        "type": "web",
    }


class TestListProjects:
    async def test_list_empty(self, authenticated_client: AsyncClient):
        response = await authenticated_client.get("/projects")
        assert response.status_code == 200
        assert response.json() == []
    
    async def test_list_unauthenticated(self, client: AsyncClient):
        response = await client.get("/projects")
        assert response.status_code == 401


class TestCreateProject:
    async def test_create_success(self, authenticated_client: AsyncClient, project_data: dict):
        response = await authenticated_client.post("/projects", json=project_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == project_data["name"]
        assert data["status"] == "draft"
    
    async def test_create_invalid_type(self, authenticated_client: AsyncClient):
        response = await authenticated_client.post("/projects", json={
            "name": "Bad Project",
            "type": "invalid_type",
        })
        assert response.status_code == 422


class TestGetProject:
    async def test_get_success(self, authenticated_client: AsyncClient, project_data: dict):
        create_response = await authenticated_client.post("/projects", json=project_data)
        project_id = create_response.json()["id"]
        response = await authenticated_client.get(f"/projects/{project_id}")
        assert response.status_code == 200
        assert response.json()["id"] == project_id
    
    async def test_get_not_found(self, authenticated_client: AsyncClient):
        response = await authenticated_client.get("/projects/99999")
        assert response.status_code == 404


class TestDeleteProject:
    async def test_delete_success(self, authenticated_client: AsyncClient, project_data: dict):
        create_response = await authenticated_client.post("/projects", json=project_data)
        project_id = create_response.json()["id"]
        response = await authenticated_client.delete(f"/projects/{project_id}")
        assert response.status_code == 200
        get_response = await authenticated_client.get(f"/projects/{project_id}")
        assert get_response.status_code == 404
