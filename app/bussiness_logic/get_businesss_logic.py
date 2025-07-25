
import re
from urllib.parse import urlparse

#--------------------------------------------------

def _parse_url_components(url: str):
    """Parse URL while preserving encoded characters"""
    return urlparse(url)

def _get_path_parts(parsed_url):
    """Split path into components"""
    return [p for p in parsed_url.path.strip("/").split("/") if p]

def _extract_service_info(path_parts):
    """Extract service name/path information"""
    if "API_" in "/".join(path_parts):
        srv_index = next(i for i, p in enumerate(path_parts) if p.startswith("API_"))
        return {
            "is_valid": True,
            "index": srv_index,
            "path": path_parts[srv_index]
        }
    try:
        srv_index = path_parts.index("odata") + 1
        return {
            "is_valid": True,
            "index": srv_index,
            "path": "/".join(path_parts[srv_index:])
        }
    except ValueError:
        return {
            "is_valid": False,
            "message": "Not a valid OData/API path"
        }

def _build_base_structure(parsed_url, path_parts, service_info):
    """Build base URL structure with entity and navigation info"""
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    sap_api_endpoint = "/" + "/".join(path_parts[:service_info["index"] + 1])
    
    entity_info = _parse_entity_info(path_parts, service_info["index"])
    navigation = _get_navigation_property(path_parts, service_info["index"])
    
    structure = {
        "base_url": base_url,
        "sap_api_endpoint": sap_api_endpoint,
        "source_entity": entity_info["entity"],
        "source_key": entity_info["key"]
    }
    
    if navigation:
        structure["navigation_property"] = navigation
        
    return structure

def _parse_entity_info(path_parts, srv_index):
    """Parse entity name and key"""
    if len(path_parts) <= srv_index + 1:
        return {"entity": "", "key": ""}
        
    entity = path_parts[srv_index + 1]
    match = re.search(r"\(([^)]+)\)", entity)
    if match:
        return {
            "entity": entity.split("(")[0],
            "key": match.group(1).strip("'")
        }
    return {"entity": entity, "key": ""}

def _get_navigation_property(path_parts, srv_index):
    """Extract navigation property if present"""
    nav_parts = path_parts[srv_index + 2:] if len(path_parts) > srv_index + 2 else []
    return "/".join(nav_parts) if nav_parts else None

def _parse_query_params(query_string):
    """Parse query parameters from URL"""
    query_params = {}
    if query_string:
        param_pairs = query_string.split('&')
        for pair in param_pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                query_params[key] = [value]
    return query_params

def _map_query_parameters(query_params):
    """Map OData query parameters to structure keys"""
    odata_params = {
        "$select": "select",
        "$expand": "expand",
        "$filter": "filter", 
        "$orderby": "orderby",
        "$top": "top",
        "$skip": "skip",
        "$inlinecount": "inlinecount",
        "$format": "format",
        "$search": "search",
        "$apply": "apply",
        "$compute": "compute",
        "$count": "count",
        "$levels": "levels",
        "$skiptoken": "skiptoken",
        "$deltatoken": "deltatoken",
        "sap-client": "sap_client",
        "sap-language": "sap_language", 
        "sap-contextid": "context_id",
        "fromDate": "from_date",
        "toDate": "to_date"
    }

    mapped_params = {}
    for odata_key, struct_key in odata_params.items():
        if odata_key in query_params:
            param_value = query_params[odata_key][0]
            
            if struct_key == "expand":
                if not any(c in param_value for c in ["(", ")", ","]):
                    param_value = param_value.replace("/", ",")
                    
            mapped_params[struct_key] = param_value
            
    return mapped_params

#--------------------------------------------------