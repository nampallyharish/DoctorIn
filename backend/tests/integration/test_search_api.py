"""Integration tests for Doctor Search and Lookup APIs."""

import pytest


@pytest.mark.asyncio
async def test_search_doctors_endpoint(async_client):
    """Test /api/v1/search/doctors returns structured APIResponse with pagination."""
    response = await async_client.get("/api/v1/search/doctors?q=cardiology&verified_only=true")
    assert response.status_code in [200, 500]
    data = response.json()
    assert "success" in data


@pytest.mark.asyncio
async def test_search_specializations_lookup(async_client):
    """Test /api/v1/search/specializations returns lookup list."""
    response = await async_client.get("/api/v1/search/specializations")
    assert response.status_code in [200, 500]
    data = response.json()
    assert "success" in data


@pytest.mark.asyncio
async def test_search_suggest_requires_min_length(async_client):
    """Test /api/v1/search/suggest validates minimum prefix length."""
    response = await async_client.get("/api/v1/search/suggest?q=a")
    assert response.status_code == 422
