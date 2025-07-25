import os
import base64
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta

class SAPAuth:
    def __init__(self):
        self.sap_username = os.getenv('SAP_USERNAME')
        self.sap_password = os.getenv('SAP_PASSWORD')
        self.sap_client = os.getenv('SAP_CLIENT', '100')
        self.sap_language = os.getenv('SAP_LANGUAGE', 'EN')
        self.sap_auth_url = os.getenv('SAP_AUTH_URL')
        self.token_cache = {}
        self.token_expiry = {}
    
    def get_basic_auth_headers(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict[str, str]:
        """Genera headers para autenticación básica de SAP"""
        user = username or self.sap_username
        pwd = password or self.sap_password
        
        if not user or not pwd:
            raise ValueError("SAP username and password are required")
        
        credentials = f"{user}:{pwd}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded_credentials}",
            "sap-client": self.sap_client,
            "sap-language": self.sap_language,
            "Content-Type": "application/json"
        }
    
    def get_bearer_token_headers(self, token: str) -> Dict[str, str]:
        """Genera headers para autenticación con token Bearer"""
        return {
            "Authorization": f"Bearer {token}",
            "sap-client": self.sap_client,
            "sap-language": self.sap_language,
            "Content-Type": "application/json"
        }
    
    def get_token_from_sap(self, username: Optional[str] = None, password: Optional[str] = None) -> Optional[str]:
        """Obtiene token de autenticación desde SAP"""
        if not self.sap_auth_url:
            return None
            
        cache_key = f"{username or self.sap_username}_{self.sap_client}"
        
        # Verificar cache
        if cache_key in self.token_cache:
            if datetime.now() < self.token_expiry.get(cache_key, datetime.min):
                return self.token_cache[cache_key]
        
        try:
            auth_data = {
                "username": username or self.sap_username,
                "password": password or self.sap_password,
                "client": self.sap_client
            }
            
            response = requests.post(
                self.sap_auth_url,
                json=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token') or data.get('token')
                
                if token:
                    # Cache token por 1 hora
                    self.token_cache[cache_key] = token
                    self.token_expiry[cache_key] = datetime.now() + timedelta(hours=1)
                    return token
                    
        except Exception as e:
            print(f"Error obteniendo token SAP: {e}")
        
        return None
    
    def get_auto_token_headers(self, username: Optional[str] = None, password: Optional[str] = None) -> Dict[str, str]:
        """Obtiene automáticamente un token y genera headers"""
        token = self.get_token_from_sap(username, password)
        if token:
            return self.get_bearer_token_headers(token)
        else:
            return self.get_basic_auth_headers(username, password)

# Instancia global
sap_auth = SAPAuth() 