"""
Debug test to identify validation issues
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

def test_debug_validation_error(client):
    """Debug test to see the exact validation error"""
    request_data = {
        "http_method": "GET",
        "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
        "service_name": "API_BUSINESS_PARTNER_QAS_220",
        "source_entity": "A_BusinessPartner",
        "source_key": "234277",
        "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName"
    }

    response = client.post("/api/v1/execute-odata", json=request_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Don't assert anything, just print the error details
    if response.status_code != 200:
        print(f"Error details: {response.json()}")

def test_debug_model_validation():
    """Test model validation directly"""
    from app.bussiness_logic.post_business_logic import ODataRequest
    
    try:
        request_data = {
            "http_method": "GET",
            "base_url": "https://intds4.test.apimanagement.us10.hana.ondemand.com",
            "service_name": "API_BUSINESS_PARTNER_QAS_220",
            "source_entity": "A_BusinessPartner",
            "source_key": "234277",
            "select": "BusinessPartner,BusinessPartnerFullName,BusinessPartnerName"
        }
        
        request = ODataRequest(**request_data)
        print("Model validation passed!")
        print(f"Request: {request}")
        
    except Exception as e:
        print(f"Model validation failed: {e}")
        print(f"Error type: {type(e)}") 