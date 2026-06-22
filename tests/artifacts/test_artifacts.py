import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_artifacts_returns_empty(async_client: AsyncClient):
    response = await async_client.get("/api/artifacts")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_artifact_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/artifacts/nonexistent")
    assert response.status_code == 404
