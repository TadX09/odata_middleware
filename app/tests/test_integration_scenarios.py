"""
Test integration scenarios and workflows
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.bussiness_logic.post_business_logic import ODataRequest, ExecuteODataRequest

class TestIntegrationScenariosAndWorkflows:
    """Test integration scenarios and workflows"""

    def test_complete_sales_order_workflow(self, client, mock_requests):
        """Test complete business partner workflow"""
        # Setup mock responses for different steps
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {
            "d": {
                "results": [
                    {
                        "BusinessPartner": "234277",
                        "BusinessPartnerFullName": "Test Business Partner",
                        "BusinessPartnerName": "Test Partner",
                        "SearchTerm2": "234277"
                    }
                ]
            }
        }
        mock_response.text = '{"d":{"results":[{"BusinessPartner":"234277","BusinessPartnerFullName":"Test Business Partner"}]}}'
        mock_requests.request.return_value = mock_response

        # Step 1: Get business partner
        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName,SearchTerm2",
            "filter": "SearchTerm2 eq '234277'"
        }

        response = client.post("/api/v1/execute-odata", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data

    def test_url_generation_and_parsing_workflow(self, client):
        """Test URL generation and parsing workflow"""
        # Step 1: Generate URL
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
        assert "odata_url" in data["data"]

        # Step 2: Parse the generated URL
        generated_url = data["data"]["odata_url"]
        response = client.get(f"/api/v1/parse-odata-url?full_url={generated_url}")

        assert response.status_code == 200
        parse_data = response.json()
        assert "data" in parse_data
        assert "is_valid" in parse_data["data"]
        assert parse_data["data"]["is_valid"] is True 