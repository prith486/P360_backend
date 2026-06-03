import pytest
from fastapi import status


class TestHealthEndpoints:
    """Integration tests for health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/api/v1/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_database_health_check(self, client, db):
        """Test database health check endpoint."""
        response = client.get("/api/v1/health/db")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
