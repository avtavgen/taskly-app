from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_repository
from app.api.health import router


@pytest.fixture
def health_repository():
    repository = Mock()
    repository.session = Mock()
    return repository


@pytest.fixture
def health_client(health_repository):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_repository] = lambda: health_repository
    with TestClient(app) as client:
        yield client


def test_pr_health_returns_ok(health_client):
    response = health_client.get("/api/pr-health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_pr_health_does_not_touch_repository(health_client, health_repository):
    health_client.get("/api/pr-health")
    health_repository.session.execute.assert_not_called()


def test_pr_health_rejects_non_get_methods(health_client):
    response = health_client.post("/api/pr-health")
    assert response.status_code == 405


def test_existing_health_route_still_queries_database(health_client, health_repository):
    # The new handler reuses the name `health`; ensure the original route is unaffected.
    response = health_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    health_repository.session.execute.assert_called_once()


def test_existing_health_route_propagates_database_errors(health_client, health_repository):
    health_repository.session.execute.side_effect = RuntimeError("db down")
    with pytest.raises(RuntimeError, match="db down"):
        health_client.get("/api/health")
