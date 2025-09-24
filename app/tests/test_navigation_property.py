"""
Test navigation property functionality
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.bussiness_logic.post_business_logic import ODataRequest, NavigationStep

class TestNavigationPropertySystem:
    """Test navigation property functionality"""

    def test_execute_request_with_json_navigation(self, client, mock_requests, mock_response):
        """Test executing request with JSON navigation property format"""
        # Setup mock
        mock_requests.request.return_value = mock_response
    
        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "navigation_property": [
                {
                    "entity": "to_BusinessPartnerBank",
                    "key": "10"
                }
            ],
            "select": "BusinessPartner,BusinessPartnerFullName"
        }
    
        response = client.post("/api/v1/execute-odata", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data

    def test_legacy_string_navigation(self, client, mock_requests, mock_response):
        """Test legacy string navigation property format"""
        # Setup mock
        mock_requests.request.return_value = mock_response

        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "navigation_property": "to_BusinessPartnerBank",
            "select": "BusinessPartner,BusinessPartnerFullName"
        }
    
        response = client.post("/api/v1/execute-odata", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data

    def test_url_generation_with_navigation(self, client):
        """Test URL generation with navigation properties"""
        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "navigation_property": [
                {
                    "entity": "to_BusinessPartnerBank",
                    "key": "10"
                }
            ],
            "select": "BusinessPartner,BusinessPartnerFullName"
        }

        response = client.post("/api/v1/generate-odata-url", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "odata_url" in data["data"] 