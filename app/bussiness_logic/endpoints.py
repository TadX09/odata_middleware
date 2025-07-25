
from datetime import datetime,timezone
from typing import Union
from fastapi import APIRouter, HTTPException, Query, Request

from app.bussiness_logic.get_businesss_logic import _build_base_structure, _extract_service_info, _get_path_parts, _map_query_parameters, _parse_query_params, _parse_url_components
from app.bussiness_logic.post_business_logic import (
    ExecuteODataRequest,
    ODataRequest, 
    ODataUrlAnalysisResult,
    TargetEntityCreationRequest,
    _build_entity_path,
    _build_full_url,
    _build_query_string,
    _build_request_url,
    _build_target_url,
    _combine_payloads,
    _execute_request,
    _get_api_path,
    _get_sap_headers,
    _process_response,
    execute_direct_request,
    execute_odata_request,
    generate_target_entity_request
)

from app.xm_json_response import JsonOrXmlResponse
from app.sap_auth import sap_auth

business_logic_router = APIRouter()

@business_logic_router.get("/helpcheck", 
    summary="Basic Health Check",
    description="Verifies that the service is active and responding",
    tags=["System"]
)
def helpcheck(request: Request):
    """
    Simple health check endpoint that verifies the service is functioning.
    """
    return JsonOrXmlResponse(content={
        "status": "ok",
        "message": "Service is running",
        "service": {
            "name": "OData Middleware",
            "environment": "production",
            "uptime": "healthy"
        }
    }, request=request)

@business_logic_router.post("/generate-odata-url") 
def generate_odata_url(request: ODataRequest, request_obj: Request):
    """
    Generates a complete OData URL based on the provided parameters.
    
    Returns:
        200: Successfully generated OData URL
        400: Invalid request parameters
        422: Validation error in request body
        500: Internal server error
    """
    try:
        # Build the full OData URL from request parameters
        full_url = _build_full_url(request)
        
        # Return response with HTTP method and generated URL
        return JsonOrXmlResponse({
            "http_method": request.http_method,
            "odata_url": full_url
        }, request_obj)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@business_logic_router.get("/parse-odata-url", response_model=ODataUrlAnalysisResult)
def parse_odata_url(request: Request, full_url: str = Query(..., description="Full SAP OData URL")):
    """
    Analyzes and parses a complete OData URL into its components.
    
    Returns:
        200: Successfully parsed OData URL
        400: Invalid URL format
        422: Validation error in URL parameters
        500: Internal server error
    """
    try:
        # Parse URL into components (scheme, netloc, path, etc)
        parsed_url = _parse_url_components(full_url)
        
        # Validate base URL has scheme and host
        if not parsed_url.scheme or not parsed_url.netloc:
            return JsonOrXmlResponse(
                ODataUrlAnalysisResult(is_valid=False, message="Invalid base URL").dict(),
                request
            )

        # Extract path segments and validate service info
        path_parts = _get_path_parts(parsed_url)
        service_info = _extract_service_info(path_parts)
        if not service_info["is_valid"]:
            return JsonOrXmlResponse(
                ODataUrlAnalysisResult(is_valid=False, message=service_info["message"]).dict(),
                request
            )

        # Build base structure and validate entity exists
        base_structure = _build_base_structure(parsed_url, path_parts, service_info)
        if not base_structure["source_entity"]:
            return JsonOrXmlResponse(
                ODataUrlAnalysisResult(is_valid=False, message="No entity found in URL").dict(),
                request
            )

        # Parse and map query parameters
        query_params = _parse_query_params(parsed_url.query)
        parsed_structure = {**base_structure, **_map_query_parameters(query_params)}

        # Return successful response with parsed URL structure
        return JsonOrXmlResponse(
            ODataUrlAnalysisResult(
                is_valid=True,
                message="URL parsed successfully",
                parsed_structure=parsed_structure
            ).dict(),
            request
        )

    except ValueError as e:
        return JsonOrXmlResponse(
            ODataUrlAnalysisResult(is_valid=False, message=f"Validation error: {str(e)}").dict(),
            request
        )
    except Exception as e:
        return JsonOrXmlResponse(
            ODataUrlAnalysisResult(is_valid=False, message=f"Internal error: {str(e)}").dict(),
            request
        )

@business_logic_router.post("/execute-odata")
def execute_odata(request: Union[ExecuteODataRequest, ODataRequest], request_obj: Request, auth_type: str = "basic", parse_response: bool = True):
    """
    Executes an OData request with SAP authentication.
    
    Args:
        request: Either ExecuteODataRequest or ODataRequest with request parameters
        request_obj: FastAPI request object
        auth_type: Authentication type ("basic" or "auto")
        parse_response: Whether to parse the SAP response
        
    Returns:
        200: Successfully executed OData request
        201: Successfully created new entity
        400: Invalid request parameters
        401: Authentication failed
        403: Insufficient permissions
        404: Entity not found
        422: Validation error
        500: Internal server error
        503: SAP service unavailable
        
    Example Postman request:
    {
        "url": "https://sap-server.com/sap/opu/odata/sap/API_SALES_ORDER_SRV/A_SalesOrder",
        "method": "GET",
        "entity_type": "SalesOrder",
        "filters": {
            "SalesOrderID": "12345"
        },
        "select": ["SalesOrderID", "CustomerName", "TotalAmount"],
        "expand": ["to_Items"]
    }
    """
    try:
        # Validate request type is supported
        if not isinstance(request, (ExecuteODataRequest, ODataRequest)):
            raise HTTPException(status_code=400, detail="Invalid request type")
        
        # Validate auth_type is supported    
        if auth_type not in ["basic", "auto"]:
            raise HTTPException(status_code=400, detail="Invalid auth_type. Must be 'basic' or 'auto'")
        
        # Handle direct execution vs target entity request    
        if isinstance(request, ExecuteODataRequest):
            # Execute direct OData request
            return execute_direct_request(request, request_obj, auth_type, parse_response)
        else:
            # Generate target entity request if needed
            if request.entity_type:
                request = generate_target_entity_request(request)
            # Execute standard OData request
            return execute_odata_request(request, request_obj, auth_type)
            
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail="SAP service unavailable")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
