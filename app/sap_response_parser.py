import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

class SAPResponseMetadata(BaseModel):
    """Metadatos de la respuesta SAP"""
    timestamp: str = Field(..., description="Timestamp de la respuesta")
    request_id: Optional[str] = Field(None, description="ID de la petición")
    status_code: int = Field(..., description="Código de estado HTTP")
    content_type: str = Field(..., description="Tipo de contenido")
    response_time_ms: Optional[float] = Field(None, description="Tiempo de respuesta en ms")

class SAPEntity(BaseModel):
    """Entidad individual de SAP"""
    id: Optional[str] = Field(None, description="ID de la entidad")
    type: Optional[str] = Field(None, description="Tipo de entidad")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Propiedades de la entidad")
    links: Optional[Dict[str, str]] = Field(None, description="Enlaces relacionados")
    etag: Optional[str] = Field(None, description="ETag de la entidad")

class SAPCollection(BaseModel):
    """Colección de entidades SAP"""
    entities: List[SAPEntity] = Field(default_factory=list, description="Lista de entidades")
    count: Optional[int] = Field(None, description="Número total de entidades")
    next_link: Optional[str] = Field(None, description="Enlace a la siguiente página")
    skip_token: Optional[str] = Field(None, description="Token para paginación")

class SAPError(BaseModel):
    """Error de SAP"""
    code: str = Field(..., description="Código de error")
    message: str = Field(..., description="Mensaje de error")
    details: Optional[List[Dict[str, Any]]] = Field(None, description="Detalles del error")
    target: Optional[str] = Field(None, description="Objetivo del error")

class StandardSAPResponse(BaseModel):
    """Respuesta estándar de SAP con estructura consistente"""
    success: bool = Field(..., description="Indica si la petición fue exitosa")
    status_code: int = Field(..., description="Código de estado HTTP")
    timestamp: str = Field(..., description="Timestamp de la respuesta")
    content_type: str = Field(..., description="Tipo de contenido original")
    original_format: str = Field(..., description="Formato original (json/xml)")
    
    # Datos siempre presentes, incluso si están vacíos
    data: Dict[str, Any] = Field(default_factory=dict, description="Datos de la respuesta")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Lista de entidades")
    count: int = Field(default=0, description="Número de entidades")
    
    # Información de paginación (siempre presente)
    pagination: Dict[str, Any] = Field(default_factory=dict, description="Información de paginación")
    
    # Error (siempre presente, None si no hay error)
    error: Optional[Dict[str, Any]] = Field(None, description="Información de error")
    
    # Metadatos adicionales
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")

class ParsedSAPResponse(BaseModel):
    """Respuesta SAP parseada y estructurada (mantiene compatibilidad)"""
    success: bool = Field(..., description="Indica si la petición fue exitosa")
    metadata: SAPResponseMetadata = Field(..., description="Metadatos de la respuesta")
    data: Optional[Union[SAPEntity, SAPCollection, Dict[str, Any]]] = Field(None, description="Datos de la respuesta")
    error: Optional[SAPError] = Field(None, description="Información de error si aplica")
    raw_response: Optional[Union[Dict[str, Any], str]] = Field(None, description="Respuesta original de SAP")
    original_format: str = Field(..., description="Formato original de la respuesta (json/xml)")

class SAPResponseParser:
    """Parser para respuestas de SAP OData (JSON y XML)"""
    
    def __init__(self):
        self.start_time = None
    
    def parse_response(self, response_data: Union[Dict[str, Any], str], status_code: int, content_type: str = "application/json") -> ParsedSAPResponse:
        """
        Parsea una respuesta de SAP a un formato más legible
        
        Args:
            response_data: Datos de la respuesta de SAP (dict para JSON, str para XML)
            status_code: Código de estado HTTP
            content_type: Tipo de contenido de la respuesta
            
        Returns:
            ParsedSAPResponse: Respuesta parseada y estructurada
        """
        try:
            # Determinar el formato de la respuesta de manera más robusta
            original_format = self._detect_response_format(response_data, content_type)
            
            if original_format == "xml":
                # Parsear XML a diccionario
                response_data = self._xml_to_dict(response_data)
            
            # Crear metadatos
            metadata = SAPResponseMetadata(
                timestamp=datetime.now().isoformat(),
                status_code=status_code,
                content_type=content_type
            )
            
            # Verificar si es una respuesta exitosa
            success = 200 <= status_code < 300
            
            if success:
                # Parsear datos exitosos
                parsed_data = self._parse_success_response(response_data)
                return ParsedSAPResponse(
                    success=True,
                    metadata=metadata,
                    data=parsed_data,
                    raw_response=response_data,
                    original_format=original_format
                )
            else:
                # Parsear error
                error = self._parse_error_response(response_data)
                return ParsedSAPResponse(
                    success=False,
                    metadata=metadata,
                    error=error,
                    raw_response=response_data,
                    original_format=original_format
                )
                
        except Exception as e:
            # Error en el parsing
            error = SAPError(
                code="PARSING_ERROR",
                message=f"Error al parsear respuesta: {str(e)}"
            )
            return ParsedSAPResponse(
                success=False,
                metadata=SAPResponseMetadata(
                    timestamp=datetime.now().isoformat(),
                    status_code=status_code,
                    content_type=content_type
                ),
                error=error,
                raw_response=response_data,
                original_format="unknown"
            )
    
    def _detect_response_format(self, response_data: Union[Dict[str, Any], str], content_type: str) -> str:
        """Detecta el formato de la respuesta de manera robusta"""
        content_type_lower = content_type.lower()
        
        # Verificar content-type específico de SAP
        if any(xml_type in content_type_lower for xml_type in ["xml", "atom"]):
            return "xml"
        
        # Verificar si es string que parece XML
        if isinstance(response_data, str):
            stripped = response_data.strip()
            if stripped.startswith("<?xml") or stripped.startswith("<feed") or stripped.startswith("<entry"):
                return "xml"
        
        # Por defecto, asumir JSON
        return "json"
    
    def _xml_to_dict(self, xml_string: str) -> Dict[str, Any]:
        """Convierte XML a diccionario con mejor manejo de namespaces"""
        try:
            # Limpiar el XML de espacios en blanco
            xml_string = xml_string.strip()
            
            # Parsear el XML
            root = ET.fromstring(xml_string)
            
            # Convertir a diccionario con manejo de namespaces
            return self._element_to_dict_with_namespaces(root)
            
        except ET.ParseError as e:
            raise ValueError(f"Error al parsear XML: {str(e)}")
    
    def _element_to_dict_with_namespaces(self, element: ET.Element) -> Dict[str, Any]:
        """Convierte un elemento XML a diccionario con mejor manejo de namespaces"""
        result = {}
        
        # Agregar atributos
        if element.attrib:
            result["@attributes"] = dict(element.attrib)
        
        # Procesar elementos hijos
        for child in element:
            # Obtener el tag sin namespace para facilitar el parsing
            tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            child_data = self._element_to_dict_with_namespaces(child)
            
            if tag in result:
                # Si ya existe el tag, convertir a lista
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_data)
            else:
                result[tag] = child_data
        
        # Si no hay hijos y hay texto, agregar el texto
        if not list(element) and element.text and element.text.strip():
            result["#text"] = element.text.strip()
        
        return result
    
    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convierte un elemento XML a diccionario"""
        result = {}
        
        # Agregar atributos
        if element.attrib:
            result["@attributes"] = dict(element.attrib)
        
        # Procesar elementos hijos
        for child in element:
            child_data = self._element_to_dict(child)
            
            if child.tag in result:
                # Si ya existe el tag, convertir a lista
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        # Si no hay hijos y hay texto, agregar el texto
        if not element and element.text and element.text.strip():
            result["#text"] = element.text.strip()
        
        return result
    
    def _parse_success_response(self, response_data: Dict[str, Any]) -> Union[SAPEntity, SAPCollection, Dict[str, Any]]:
        """Parsea una respuesta exitosa de SAP"""
        
        # Para XML, buscar patrones comunes de SAP OData
        if "feed" in response_data:
            # Es una colección en formato Atom/XML
            return self._parse_xml_collection(response_data)
        elif "entry" in response_data:
            # Es una entidad individual en formato Atom/XML
            return self._parse_xml_entity(response_data)
        elif "d" in response_data and "results" in response_data["d"]:
            # Es una colección en formato JSON
            return self._parse_collection(response_data["d"])
        elif "d" in response_data:
            # Es una entidad individual en formato JSON
            return self._parse_entity(response_data["d"])
        elif "odata.metadata" in response_data or "odata.type" in response_data:
            # Es una entidad con metadatos OData
            return self._parse_entity(response_data)
        else:
            # Respuesta genérica
            return self._parse_generic_response(response_data)
    
    def _parse_xml_collection(self, xml_data: Dict[str, Any]) -> SAPCollection:
        """Parsea una colección en formato XML/Atom"""
        entities = []
        
        feed = xml_data.get("feed", {})
        entries = feed.get("entry", [])
        
        # Asegurar que entries sea una lista
        if not isinstance(entries, list):
            entries = [entries]
        
        for entry in entries:
            entity = self._parse_xml_entry(entry)
            entities.append(entity)
        
        return SAPCollection(
            entities=entities,
            count=len(entities)
        )
    
    def _parse_xml_entity(self, xml_data: Dict[str, Any]) -> SAPEntity:
        """Parsea una entidad individual en formato XML/Atom"""
        entry = xml_data.get("entry", {})
        return self._parse_xml_entry(entry)
    
    def _parse_xml_entry(self, entry: Dict[str, Any]) -> SAPEntity:
        """Parsea una entrada XML/Atom con mejor manejo de propiedades SAP"""
        properties = {}
        metadata = {}
        
        # Extraer ID del entry
        entry_id = entry.get("id", "")
        if isinstance(entry_id, dict) and "#text" in entry_id:
            metadata["id"] = entry_id["#text"]
        elif isinstance(entry_id, str):
            metadata["id"] = entry_id
        
        # Extraer propiedades del content
        content = entry.get("content", {})
        if isinstance(content, dict):
            properties_data = content.get("properties", {})
            if isinstance(properties_data, dict):
                properties = self._extract_xml_properties(properties_data)
        
        # Extraer enlaces
        links = entry.get("link", [])
        if links and isinstance(links, list):
            link_dict = {}
            for link in links:
                if isinstance(link, dict):
                    rel = link.get("@attributes", {}).get("rel", "")
                    href = link.get("@attributes", {}).get("href", "")
                    if rel and href:
                        link_dict[rel] = href
            if link_dict:
                metadata["links"] = link_dict
        
        return SAPEntity(
            id=metadata.get("id"),
            type=metadata.get("type"),
            properties=properties,
            links=metadata.get("links")
        )
    
    def _extract_xml_properties(self, properties_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae propiedades de XML con mejor manejo de tipos de datos SAP"""
        properties = {}
        
        for key, value in properties_data.items():
            if key.startswith("@"):
                continue
                
            # Manejar diferentes formatos de valores XML
            if isinstance(value, dict):
                # Verificar si tiene atributos de tipo
                attributes = value.get("@attributes", {})
                type_attr = attributes.get("m:type", "")
                
                # Extraer el valor real
                if "#text" in value:
                    raw_value = value["#text"]
                else:
                    raw_value = value
                
                # Convertir según el tipo de datos SAP
                properties[key] = self._convert_sap_value(raw_value, type_attr)
            else:
                properties[key] = self._clean_property_value(value)
        
        return properties
    
    def _convert_sap_value(self, value: str, sap_type: str) -> Any:
        """Convierte valores de SAP según su tipo de datos"""
        if not value:
            return value
            
        try:
            if "Edm.Int32" in sap_type or "Edm.Int64" in sap_type:
                return int(value)
            elif "Edm.Decimal" in sap_type or "Edm.Double" in sap_type:
                return float(value)
            elif "Edm.Boolean" in sap_type:
                return value.lower() in ("true", "1", "yes")
            elif "Edm.DateTime" in sap_type:
                # Mantener como string por ahora, se puede convertir a datetime si es necesario
                return value
            else:
                # String por defecto
                return value.strip()
        except (ValueError, TypeError):
            # Si falla la conversión, devolver el valor original
            return value
    
    def _parse_collection(self, collection_data: Dict[str, Any]) -> SAPCollection:
        """Parsea una colección de entidades"""
        entities = []
        
        if "results" in collection_data:
            for entity_data in collection_data["results"]:
                entity = self._parse_entity_data(entity_data)
                entities.append(entity)
        
        return SAPCollection(
            entities=entities,
            count=collection_data.get("__count"),
            next_link=collection_data.get("__next"),
            skip_token=collection_data.get("__skiptoken")
        )
    
    def _parse_entity(self, entity_data: Dict[str, Any]) -> SAPEntity:
        """Parsea una entidad individual"""
        return self._parse_entity_data(entity_data)
    
    def _parse_entity_data(self, entity_data: Dict[str, Any]) -> SAPEntity:
        """Parsea los datos de una entidad"""
        # Separar propiedades de metadatos
        properties = {}
        metadata = {}
        
        for key, value in entity_data.items():
            if key.startswith("__"):
                # Es un metadato
                metadata[key] = value
            else:
                # Es una propiedad
                properties[key] = self._clean_property_value(value)
        
        return SAPEntity(
            id=metadata.get("id"),
            type=metadata.get("type"),
            properties=properties,
            links=metadata.get("links"),
            etag=metadata.get("etag")
        )
    
    def _parse_generic_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parsea una respuesta genérica"""
        cleaned_data = {}
        
        for key, value in response_data.items():
            cleaned_data[key] = self._clean_property_value(value)
        
        return cleaned_data
    
    def _parse_error_response(self, error_data: Dict[str, Any]) -> SAPError:
        """Parsea una respuesta de error"""
        error_info = error_data.get("error", {})
        
        return SAPError(
            code=error_info.get("code", "UNKNOWN_ERROR"),
            message=error_info.get("message", "Error desconocido"),
            details=error_info.get("details"),
            target=error_info.get("target")
        )
    
    def _clean_property_value(self, value: Any) -> Any:
        """Limpia y formatea valores de propiedades"""
        if isinstance(value, dict):
            # Recursivamente limpiar diccionarios anidados
            return {k: self._clean_property_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            # Limpiar listas
            return [self._clean_property_value(item) for item in value]
        elif isinstance(value, str):
            # Limpiar strings (remover caracteres especiales de SAP)
            return value.strip()
        else:
            return value
    
    def format_for_display(self, parsed_response: ParsedSAPResponse) -> Dict[str, Any]:
        """Formatea la respuesta parseada para mostrar de forma más legible"""
        result = {
            "success": parsed_response.success,
            "status_code": parsed_response.metadata.status_code,
            "timestamp": parsed_response.metadata.timestamp,
            "original_format": parsed_response.original_format
        }
        
        if parsed_response.success:
            if isinstance(parsed_response.data, SAPCollection):
                result["type"] = "collection"
                result["count"] = parsed_response.data.count
                result["entities"] = [
                    {
                        "id": entity.id,
                        "type": entity.type,
                        "properties": entity.properties
                    }
                    for entity in parsed_response.data.entities
                ]
                if parsed_response.data.next_link:
                    result["next_page"] = parsed_response.data.next_link
                    
            elif isinstance(parsed_response.data, SAPEntity):
                result["type"] = "entity"
                result["entity"] = {
                    "id": parsed_response.data.id,
                    "type": parsed_response.data.type,
                    "properties": parsed_response.data.properties
                }
            else:
                result["type"] = "generic"
                result["data"] = parsed_response.data
        else:
            result["error"] = {
                "code": parsed_response.error.code,
                "message": parsed_response.error.message,
                "details": parsed_response.error.details
            }
        
        return result
    
    def parse_to_standard_response(self, response_data: Union[Dict[str, Any], str], status_code: int, content_type: str = "application/json") -> StandardSAPResponse:
        """
        Parsea una respuesta de SAP a un formato estándar con estructura consistente
        
        Args:
            response_data: Datos de la respuesta de SAP (dict para JSON, str para XML)
            status_code: Código de estado HTTP
            content_type: Tipo de contenido de la respuesta
            
        Returns:
            StandardSAPResponse: Respuesta estándar con estructura consistente
        """
        try:
            # Determinar el formato de la respuesta
            original_format = self._detect_response_format(response_data, content_type)
            
            if original_format == "xml":
                # Parsear XML a diccionario
                response_data = self._xml_to_dict(response_data)
            
            # Verificar si es una respuesta exitosa
            success = 200 <= status_code < 300
            
            if success:
                return self._create_standard_success_response(response_data, status_code, content_type, original_format)
            else:
                return self._create_standard_error_response(response_data, status_code, content_type, original_format)
                
        except Exception as e:
            # Error en el parsing
            return self._create_standard_error_response(
                response_data, 
                status_code, 
                content_type, 
                "unknown",
                error_code="PARSING_ERROR",
                error_message=f"Error al parsear respuesta: {str(e)}"
            )
    
    def _create_standard_success_response(self, response_data: Dict[str, Any], status_code: int, content_type: str, original_format: str) -> StandardSAPResponse:
        """Crea una respuesta estándar exitosa"""
        # Parsear datos usando el método existente
        parsed_response = self.parse_response(response_data, status_code, content_type)
        
        # Extraer entidades y datos
        entities = []
        data = {}
        count = 0
        pagination = {}
        
        if parsed_response.success and parsed_response.data:
            if isinstance(parsed_response.data, SAPCollection):
                entities = [
                    {
                        "id": entity.id,
                        "type": entity.type,
                        "properties": entity.properties,
                        "links": entity.links
                    }
                    for entity in parsed_response.data.entities
                ]
                count = parsed_response.data.count or len(entities)
                
                # Información de paginación
                if parsed_response.data.next_link:
                    pagination["next_link"] = parsed_response.data.next_link
                if parsed_response.data.skip_token:
                    pagination["skip_token"] = parsed_response.data.skip_token
                    
            elif isinstance(parsed_response.data, SAPEntity):
                entities = [{
                    "id": parsed_response.data.id,
                    "type": parsed_response.data.type,
                    "properties": parsed_response.data.properties,
                    "links": parsed_response.data.links
                }]
                count = 1
                data = parsed_response.data.properties
            else:
                data = parsed_response.data if isinstance(parsed_response.data, dict) else {"raw_data": parsed_response.data}
        
        return StandardSAPResponse(
            success=True,
            status_code=status_code,
            timestamp=datetime.now().isoformat(),
            content_type=content_type,
            original_format=original_format,
            data=data,
            entities=entities,
            count=count,
            pagination=pagination,
            error=None,
            metadata={
                "response_type": "success",
                "has_data": count > 0 or bool(data)
            }
        )
    
    def _create_standard_error_response(self, response_data: Union[Dict[str, Any], str], status_code: int, content_type: str, original_format: str, error_code: str = None, error_message: str = None) -> StandardSAPResponse:
        """Crea una respuesta estándar de error"""
        # Intentar parsear el error de la respuesta
        if not error_code or not error_message:
            try:
                if isinstance(response_data, dict):
                    error_info = response_data.get("error", {})
                    error_code = error_info.get("code", "UNKNOWN_ERROR")
                    error_message = error_info.get("message", "Error desconocido")
                else:
                    error_code = "UNKNOWN_ERROR"
                    error_message = "Error desconocido"
            except:
                error_code = "UNKNOWN_ERROR"
                error_message = "Error desconocido"
        
        return StandardSAPResponse(
            success=False,
            status_code=status_code,
            timestamp=datetime.now().isoformat(),
            content_type=content_type,
            original_format=original_format,
            data={},
            entities=[],
            count=0,
            pagination={},
            error={
                "code": error_code,
                "message": error_message,
                "status_code": status_code
            },
            metadata={
                "response_type": "error",
                "has_data": False
            }
        )

# Instancia global del parser
sap_parser = SAPResponseParser() 