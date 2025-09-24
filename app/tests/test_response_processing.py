"""
Test response processing and format handling
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.bussiness_logic.post_business_logic import ODataRequest

class TestResponseProcessingAndFormatHandling:
    """Test response processing and format handling"""

    def test_json_response_processing(self, client, mock_requests):
        """Test processing of JSON responses"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {
            "d": {
                "results": [
                    {
                        "__metadata": {
                            "id": "https://intds4.test.apimanagement.us10.hana.ondemand.com/API_BUSINESS_PARTNER_QAS_220/A_BusinessPartner('234277')",
                            "type": "API_BUSINESS_PARTNER_QAS_220.A_BusinessPartner"
                        },
                        "BusinessPartner": "234277",
                        "BusinessPartnerFullName": "Test Business Partner",
                        "BusinessPartnerName": "Test Partner"
                    }
                ]
            }
        }
        mock_response.text = '{"d":{"results":[{"BusinessPartner":"234277","BusinessPartnerFullName":"Test Business Partner"}]}}'
        mock_requests.request.return_value = mock_response

        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName"
        }

        response = client.post("/api/v1/execute-odata", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data

    def test_xml_response_processing(self, client, mock_requests):
        """Test processing of XML responses"""
        # Setup mock XML response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/atom+xml'}
        mock_response.text = """<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>https://intds4.test.apimanagement.us10.hana.ondemand.com/API_BUSINESS_PARTNER_QAS_220/A_BusinessPartner('234277')</id>
                <content type="application/xml">
                    <m:properties xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata">
                        <d:BusinessPartner>234277</d:BusinessPartner>
                        <d:BusinessPartnerFullName>Test Business Partner</d:BusinessPartnerFullName>
                    </m:properties>
                </content>
            </entry>
        </feed>"""
        mock_requests.request.return_value = mock_response
    
        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "format": "xml"
        }

        response = client.post("/api/v1/execute-odata", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data

    def test_error_response_processing(self, client, mock_requests):
        """Test processing of error responses"""
        # Setup mock error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {
            "error": {
                "code": "NOT_FOUND",
                "message": "Entity not found"
            }
        }
        mock_response.text = '{"error":{"code":"NOT_FOUND","message":"Entity not found"}}'
        mock_requests.request.return_value = mock_response

        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "99999"
        }

        response = client.post("/api/v1/execute-odata", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "metadata" in data 