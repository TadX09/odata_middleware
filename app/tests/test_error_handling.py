"""
Test error handling and edge cases
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.bussiness_logic.post_business_logic import ODataRequest, NavigationStep

class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""

    def test_sap_connection_error(self, client, mock_requests):
        """Test handling of SAP connection errors"""
        # Setup mock to raise connection error
        mock_requests.request.side_effect = Exception("SAP server unreachable")

        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277"
        }

        response = client.post("/api/v1/execute-odata", json=request_data)

        # Should return 422 for validation error or 500 for server error
        assert response.status_code in [422, 500]

    def test_malformed_odata_url_parsing(self, client):
        """Test parsing of malformed OData URLs"""
        malformed_url = "not-a-valid-url"

        response = client.get(f"/api/v1/parse-odata-url?full_url={malformed_url}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "is_valid" in data["data"]
        assert data["data"]["is_valid"] is False 