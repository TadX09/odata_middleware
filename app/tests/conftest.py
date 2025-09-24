"""
Test configuration and fixtures
"""
import os
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.bussiness_logic.post_business_logic import ODataRequest, ExecuteODataRequest, NavigationStep

# Configure environment variables for testing
os.environ['SAP_USERNAME'] = 'test_user'
os.environ['SAP_PASSWORD'] = 'test_password'
os.environ['SAP_CLIENT'] = '100'
os.environ['SAP_LANGUAGE'] = 'EN'

@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(autouse=True)
def patch_sap_auth():
    """Mock global de sap_auth para todos los tests"""
    with patch('app.bussiness_logic.post_business_logic.sap_auth') as mock_auth:
        mock_auth.get_basic_auth_headers.return_value = {
            "Authorization": "Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ=",
            "sap-client": "100",
            "sap-language": "EN",
            "Content-Type": "application/json"
        }
        mock_auth.get_auto_token_headers.return_value = {
            "Authorization": "Bearer test_token",
            "sap-client": "100",
            "sap-language": "EN",
            "Content-Type": "application/json"
        }
        yield mock_auth

@pytest.fixture
def mock_requests():
    """Mock requests library"""
    with patch('app.bussiness_logic.post_business_logic.requests') as mock_req:
        yield mock_req

@pytest.fixture
def mock_response():
    """Create a mock response object"""
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.headers = {'content-type': 'application/json'}
    mock_resp.json.return_value = {
        "d": {
            "results": [
                {
                    "BusinessPartner": "234277",
                    "BusinessPartnerFullName": "Test Business Partner",
                    "BusinessPartnerName": "Test Partner"
                }
            ]
        }
    }
    mock_resp.text = '{"d":{"results":[{"BusinessPartner":"234277","BusinessPartnerFullName":"Test Business Partner"}]}}'
    return mock_resp

@pytest.fixture
def sample_odata_request():
    """Sample OData request for testing"""
    return ODataRequest(
        http_method="GET",
        base_url="https://test.sap.com",
        service_name="TEST_SRV",
        source_entity="A_SalesOrder",
        source_key="5001",
        select="SalesOrderID,Status",
        format="json"
    ) 