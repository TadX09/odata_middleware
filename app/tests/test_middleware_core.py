"""
Test core middleware functionality
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.bussiness_logic.post_business_logic import ODataRequest, ExecuteODataRequest

class TestCoreMiddlewareFunctionality:
    """Test core middleware functionality"""

    def test_execute_odata_request_success(self, client, mock_requests, mock_response):
        """Test successful OData request execution"""
        # Setup mock
        mock_requests.request.return_value = mock_response
    
        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName",
            "filter": "SearchTerm2 eq '234277'"
        }

        response = client.post("/api/v1/execute-odata", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data

    def test_url_generation_functionality(self, client):
        """Test URL generation endpoint"""
        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName",
            "filter": "SearchTerm2 eq '234277'"
        }

        response = client.post("/api/v1/generate-odata-url", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "http_method" in data["data"]
        assert "odata_url" in data["data"]

    def test_url_parsing_functionality(self, client):
        """Test URL parsing endpoint"""
        test_url = "https://intds4.test.apimanagement.us10.hana.ondemand.com/API_BUSINESS_PARTNER_QAS_220/A_BusinessPartner?$select=BusinessPartner,BusinessPartnerFullName,BusinessPartnerName,PersonFullName,SearchTerm2,to_Supplier,BusinessPartnerGrouping,to_BusinessPartnerBank&$filter=SearchTerm2 eq '234277'"

        response = client.get(f"/api/v1/parse-odata-url?full_url={test_url}")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "is_valid" in data["data"]

    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/v1/healthcheck")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["status"] == "ok" 