from enum import Enum
import re
from typing import Dict, Optional, Union, List
from urllib.parse import urlparse

from fastapi import HTTPException, Request
from pydantic import BaseModel, Field, HttpUrl
import requests

from app.sap_auth import sap_auth
from app.xm_json_response import JsonOrXmlResponse
from app.sap_response_parser import sap_parser

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

class NavigationStep(BaseModel):
    """Represents a single navigation step with entity and optional key"""
    entity: str = Field(..., description="Entity name", example="to_Items")
    key: Optional[Union[str, Dict[str, str]]] = Field(None, description="Entity key or keys", example="10")
    filter: Optional[str] = Field(None, description="OData filter for this step", example="Status eq 'ACTIVE'")

class ODataRequest(BaseModel):
    http_method: HTTPMethod = Field(
        default=HTTPMethod.GET,
        description="HTTP method for the request (GET, POST, PUT, PATCH, DELETE)",
        example="GET"
    )
    base_url: HttpUrl = Field(
        ...,
        description="Base URL of the SAP server",
        example="https://my.sap.server.com"
    )
    service_name: Optional[str] = Field(
        None,
        description="SAP OData service name",
        example="ZMY_SRV"
    )
    sap_api_endpoint: Optional[str] = Field(
        None,
        description="Complete SAP API endpoint",
        example="/sap/opu/odata/sap/ZMY_SRV"
    )
    source_entity: str = Field(
        ...,
        description="Main entity name",
        example="SalesOrders"
    )
    source_key: Union[str, Dict[str, str]] = Field(
        ...,
        description="Key or keys of the main entity",
        example="5001"
    )
    navigation_property: Optional[Union[str, List[NavigationStep]]] = Field(
        None,
        description="Navigation property for relationships. Can be string (legacy) or JSON array for complex navigation",
        example=[
            {"entity": "to_Items", "key": "10"},
            {"entity": "to_Product", "filter": "Category eq 'ELECTRONICS'"}
        ]
    )
    expand: Optional[str] = Field(
        None,
        description="Properties to expand in the response",
        example="to_Items/to_Product"
    )
    select: Optional[str] = Field(
        None,
        description="Specific fields to return",
        example="SalesOrderID,Status,CreatedAt"
    )
    filter: Optional[str] = Field(
        None,
        description="OData filters for the query",
        example="Status eq 'OPEN'"
    )
    orderby: Optional[str] = Field(
        None,
        description="Field and direction for sorting results",
        example="CreatedAt desc"
    )
    top: Optional[int] = Field(
        None,
        description="Maximum number of records to return",
        example=10
    )
    skip: Optional[int] = Field(
        None,
        description="Number of records to skip",
        example=0
    )
    inlinecount: Optional[str] = Field(
        None,
        description="Include total count in response",
        example="allpages"
    )
    from_date: Optional[str] = Field(
        None,
        description="Start date for filtering",
        example="2024-01-01"
    )
    to_date: Optional[str] = Field(
        None,
        description="End date for filtering",
        example="2024-01-31"
    )
    format: Optional[str] = Field(
        None,
        description="Desired response format",
        example="json"
    )
    levels: Optional[int] = Field(
        None,
        description="Expansion levels for relationships",
        example=1
    )
    skiptoken: Optional[str] = Field(
        None,
        description="Pagination token to continue query",
        example="token123"
    )
    deltatoken: Optional[str] = Field(
        None,
        description="Token for delta queries",
        example="delta123"
    )
    sap_client: Optional[str] = Field(
        None,
        description="SAP client ID",
        example="100"
    )
    sap_language: Optional[str] = Field(
        None,
        description="SAP language code",
        example="EN"
    )
    context_id: Optional[str] = Field(
        None,
        description="Context ID for the request",
        example="ctx123"
    )
    custom_string: Optional[str] = Field(
        None,
        description="Custom string field",
        example="custom value"
    )
    custom_int: Optional[int] = Field(
        None,
        description="Custom integer field",
        example=42
    )
    custom_double: Optional[float] = Field(
        None,
        description="Custom double field",
        example=3.14
    )
    custom_decimal: Optional[float] = Field(
        None,
        description="Custom decimal field",
        example=10.99
    )
    custom_boolean: Optional[bool] = Field(
        None,
        description="Custom boolean field",
        example=True
    )
    custom_datetime: Optional[str] = Field(
        None,
        description="Custom datetime field",
        example="2024-01-01T12:00:00"
    )
    payload: Optional[Dict[str, Union[str, int, float, dict, list]]] = Field(
        default=None,
        description="Data to send in request body",
        example={"ProductID": "MAT001", "Quantity": 5}
    )
    timeout: Optional[int] = Field(
        default=30,
        description="Maximum wait time in seconds",
        example=30
    )
    entity_type: Optional[str] = Field(
        None,
        description="SAP entity type",
        example="SalesOrder"
    )
    filters: Optional[Dict[str, str]] = Field(
        None,
        description="Filters in dictionary format",
        example={"Status": "OPEN"}
    )
    batch_operations: Optional[list] = Field(
        None,
        description="List of operations for batch processing",
        example=[{"method": "POST", "url": "/EntitySet", "body": {}}]
    )
    batch_id: Optional[str] = Field(
        None,
        description="Batch identifier",
        example="batch123"
    )
    change_set_id: Optional[str] = Field(
        None,
        description="Change set identifier",
        example="changeset1"
    )
    metadata_level: Optional[str] = Field(
        None,
        description="Metadata level to include",
        example="full"
    )
    search: Optional[str] = Field(
        None,
        description="General search term",
        example="search term"
    )
    count: Optional[bool] = Field(
        None,
        description="Include count in response",
        example=True
    )
    custom_headers: Optional[Dict[str, str]] = Field(
        None,
        description="Additional custom headers",
        example={"x-custom-header": "value"}
    )
    retry_attempts: Optional[int] = Field(
        default=3,
        description="Number of retry attempts",
        example=3
    )
    retry_delay: Optional[int] = Field(
        default=1,
        description="Delay between retries in seconds",
        example=1
    )
    
class TargetEntityCreationRequest(BaseModel):
    http_method: HTTPMethod = Field(
        default=HTTPMethod.POST,
        description="HTTP method for creation",
        example="POST"
    )
    base_url: HttpUrl = Field(
        ...,
        description="Base URL of the SAP server",
        example="https://my.sap.server.com"
    )
    service_name: Optional[str] = Field(
        None,
        description="SAP OData service name",
        example="ZMY_SRV"
    )
    sap_api_endpoint: Optional[str] = Field(
        None,
        description="Complete SAP API endpoint",
        example="/sap/opu/odata/sap/ZMY_SRV"
    )
    target_entity: str = Field(
        ...,
        description="Target entity for creation",
        example="SalesOrderItems"
    )
    parent_keys: Dict[str, str] = Field(
        ...,
        description="Parent entity keys",
        example={"SalesOrderID": "5001"}
    )
    payload: Dict[str, Union[str, int, float]] = Field(
        ...,
        description="Data for creating new entity",
        example={"ProductID": "MAT001", "Quantity": 10}
    )

class ODataUrlAnalysisResult(BaseModel):
    is_valid: bool = Field(
        ...,
        description="Indicates if URL is valid"
    )
    message: Optional[str] = Field(
        None,
        description="Analysis descriptive message"
    )
    parsed_structure: Optional[Dict[str, Union[str, Dict[str, str]]]] = Field(
        None,
        description="Parsed URL structure"
    )
 
class ExecuteODataRequest(BaseModel):
    odata_url: HttpUrl = Field(
        ...,
        description="Complete OData endpoint URL",
        example="https://my.sap.server.com/sap/opu/odata/sap/ZMY_SRV/EntitySet"
    )
    http_method: HTTPMethod = Field(
        ...,
        description="HTTP method to execute",
        example="GET"
    )
    payload: Optional[Dict[str, Union[str, int, float, dict, list]]] = Field(
        default=None,
        description="Data to send in request body",
        example={"ProductID": "MAT001", "Quantity": 5}
    )
    timeout: Optional[int] = Field(
        default=30,
        description="Maximum wait time in seconds",
        example=30
    )


def _build_full_url(request: ODataRequest) -> str:
    """Builds the complete OData URL from the request components."""
    base_url = _get_base_url(request)
    path = _build_path(request)
    query_string = _build_query_string(request)
    return f"{base_url}/{path}{query_string}"

def _get_base_url(request: ODataRequest) -> str:
    """Gets and formats the base URL."""
    return str(request.base_url).rstrip("/")

def _build_path(request: ODataRequest) -> str:
    """Builds the API path including entity path."""
    api_path = _get_api_path(request)
    entity_path = _build_entity_path(request)
    return f"{api_path}/{entity_path}"

#--------------------------------------------------

def _get_api_path_from_request(request: TargetEntityCreationRequest) -> str:
    """Extract API path from request"""
    if request.sap_api_endpoint:
        return request.sap_api_endpoint.strip("/")
    elif request.service_name:
        return f"sap/opu/odata/{request.service_name}"
    raise HTTPException(status_code=400, detail="Either service_name or sap_api_endpoint must be provided.")

def _build_target_url(request: TargetEntityCreationRequest) -> str:
    """Build full URL for target entity"""
    base_url = str(request.base_url).rstrip("/")
    api_path = _get_api_path_from_request(request)
    return f"{base_url}/{api_path}/{request.target_entity}"

def _combine_payloads(request: TargetEntityCreationRequest) -> dict:
    """Combine parent keys and payload"""
    return {**request.payload, **request.parent_keys}

def generate_target_entity_request(request: TargetEntityCreationRequest):
    """
    Creates a request structure for creating a new entity related to a parent entity.
    
    Args:
        request: The target entity creation request parameters
        
    Returns:
        dict: Dictionary containing the generated request details
        
    Raises:
        ValueError: If request parameters are invalid
        ConnectionError: If SAP service is unavailable
    """
    try:
        # Build target URL for the new entity
        full_url = _build_target_url(request)
        
        # Combine parent and child entity payloads
        combined_payload = _combine_payloads(request)

        # Return request details
        return {
            "http_method": request.http_method,
            "odata_url": full_url,
            "payload": combined_payload
        }

    except ValueError as e:
        raise ValueError(f"Invalid request parameters: {str(e)}")
    except ConnectionError as e:
        raise ConnectionError("SAP service unavailable")
    except Exception as e:
        raise Exception(f"Error generating target entity request: {str(e)}")

#--------------------------------------------------

def format_key_string(key_data):
    if isinstance(key_data, dict):
        return ','.join(f"{k}='{v}'" for k, v in key_data.items())
    else:
        return f"'{key_data}'"

def _get_api_path(request: ODataRequest) -> str:
    """Extract API path from request"""
    if request.sap_api_endpoint:
        return request.sap_api_endpoint.strip("/")
    elif request.service_name:
        return f"sap/opu/odata/{request.service_name}"
    raise HTTPException(status_code=400, detail="service_name or sap_api_endpoint is required")

def _build_navigation_path(navigation_steps: List[NavigationStep]) -> str:
    """Build navigation path from list of NavigationStep objects"""
    path_parts = []
    
    for step in navigation_steps:
        step_path = step.entity
        
        # Add key if provided
        if step.key:
            key_string = format_key_string(step.key)
            step_path += f"({key_string})"
        
        # Add filter if provided
        if step.filter:
            step_path += f"?$filter={step.filter}"
        
        path_parts.append(step_path)
    
    return "/".join(path_parts)

def _build_entity_path(request: ODataRequest) -> str:
    """Build entity path with keys and navigation"""
    path = request.source_entity
    if request.source_key:
        key_string = format_key_string(request.source_key)
        path += f"({key_string})"
    
    if request.navigation_property:
        if isinstance(request.navigation_property, str):
            # Legacy string format
            path += f"/{request.navigation_property}"
        elif isinstance(request.navigation_property, list):
            # New JSON array format
            navigation_path = _build_navigation_path(request.navigation_property)
            path += f"/{navigation_path}"
    
    return path

def _build_query_string(request: ODataRequest) -> str:
    """Build OData query string from request parameters"""
    query_params = []
    query_options = {
        'select': '$select',
        'expand': '$expand', 
        'filter': '$filter',
        'orderby': '$orderby',
        'top': '$top',
        'skip': '$skip',
        'inlinecount': '$inlinecount',
        'format': '$format',
        'from_date': 'fromDate',
        'to_date': 'toDate'
    }
    
    for attr, prefix in query_options.items():
        if value := getattr(request, attr, None):
            query_params.append(f"{prefix}={value}")
            
    return f"?{'&'.join(query_params)}" if query_params else ""

#--------------------------------------------------

def _get_sap_headers(auth_type: str) -> dict:
    """Get SAP authentication headers based on auth type"""
    if auth_type == "basic":
        return sap_auth.get_basic_auth_headers()
    elif auth_type == "auto":
        return sap_auth.get_auto_token_headers()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported authentication type: {auth_type}")

def _build_request_url(request: Union[ExecuteODataRequest, ODataRequest]) -> str:
    """Build the full request URL based on request type"""
    if isinstance(request, ODataRequest):
        return _build_odata_request_url(request)
    else:
        _validate_execute_request(request)
        return str(request.odata_url)

def _build_odata_request_url(request: ODataRequest) -> str:
    """Build URL for ODataRequest type"""
    query_string = _build_query_string(request)
    base_url = str(request.base_url).rstrip("/")
    api_path = _get_api_path_for_request(request)
    entity_path = _build_entity_path(request)
    return f"{base_url}/{api_path}/{entity_path}{query_string}"

def _get_api_path_for_request(request: ODataRequest) -> str:
    """Get API path from request parameters"""
    if request.sap_api_endpoint:
        return request.sap_api_endpoint.strip("/")
    elif request.service_name:
        return f"sap/opu/odata/{request.service_name}"
    else:
        raise HTTPException(status_code=400, detail="Either service_name or sap_api_endpoint must be provided")

def _validate_execute_request(request: ExecuteODataRequest):
    """Validate ExecuteODataRequest parameters"""
    method = request.http_method.upper()
    if method not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        raise HTTPException(status_code=400, detail="Unsupported HTTP method")
        
    if method in {"POST", "PUT", "PATCH"} and not request.payload:
        raise HTTPException(status_code=400, detail=f"{method} requires payload")

def _execute_request(request: Union[ExecuteODataRequest, ODataRequest], url: str, sap_headers: dict) -> requests.Response:
    """Execute the HTTP request"""
    return requests.request(
        method=request.http_method.upper(),
        url=url,
        headers=sap_headers,
        json=request.payload if request.payload else None,
        timeout=request.timeout
    )

def _process_response(response: requests.Response, auth_type: str, parse_response: bool = True) -> dict:
    """Process the response and build response data"""
    content_type = response.headers.get("content-type", "").lower()
    
    # Determinar si es XML o JSON
    is_xml = "xml" in content_type or "atom" in content_type
    
    if is_xml:
        # Para XML, usar el texto directamente
        response_data = response.text
    else:
        # Para JSON, intentar parsear
        try:
            response_data = response.json()
        except ValueError:
            response_data = {"text": response.text}

    if parse_response:
        # Parsear la respuesta de SAP a un formato más legible
        parsed_response = sap_parser.parse_response(
            response_data, 
            response.status_code, 
            content_type
        )
        
        return {
            "status_code": response.status_code,
            "parsed_response": sap_parser.format_for_display(parsed_response),
            "raw_response": response_data,
            "auth_type_used": auth_type,
            "content_type": content_type
        }
    else:
        # Devolver respuesta sin parsear
        return {
            "status_code": response.status_code,
            "response": response_data,
            "auth_type_used": auth_type,
            "content_type": content_type
        }

def execute_direct_request(request: ExecuteODataRequest, request_obj: Request, auth_type: str, parse_response: bool = True) -> JsonOrXmlResponse:
    """Execute request using direct OData URL"""
    sap_headers = _get_sap_headers(auth_type)
    full_url = str(request.odata_url)
    response = _execute_request(request, full_url, sap_headers)
    response_data = _process_response(response, auth_type, parse_response)
    return JsonOrXmlResponse(content=response_data, request=request_obj)

def execute_odata_request(request: ODataRequest, request_obj: Request, auth_type: str, parse_response: bool = True) -> JsonOrXmlResponse:
    """Execute request using OData request parameters"""
    sap_headers = _get_sap_headers(auth_type)
    full_url = _build_odata_request_url(request)
    response = _execute_request(request, full_url, sap_headers)
    response_data = _process_response(response, auth_type, parse_response)
    return JsonOrXmlResponse(content=response_data, request=request_obj)

#--------------------------------------------------
