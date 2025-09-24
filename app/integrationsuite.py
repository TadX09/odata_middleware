import requests

#Class to perform basic CRUD REST API Operation in remote target
class ISOperations:

    def __init__(self, basePath, virtual_host=None, virtual_port=None, api_key=None):
        self.virtual_host = virtual_host
        self.virtual_port = virtual_port
        self.api_key = api_key
        self.base_path = basePath

    #Method to perfom basic POST HTTP Request on Integration Suite Proxy.
    #Example of a call of the method below <constructor>.execute_post_operation('Call',obj, 'application/json','SP')
    def execute_post_operation(self, path: str, body: str, contentType: str, resource: str):
        if not all([self.virtual_host, self.virtual_port, self.api_key]):
            raise ValueError("virtual_host, virtual_port and api_key are required")
            
        url = f"{self.virtual_host}:{self.virtual_port}/{self.base_path}"
        completeURL = f"https://{url}/{path}/{resource}"
        headers = {"Content-Type": contentType, "x-api-key": self.api_key}
        response = requests.post(completeURL, headers=headers, json=body)
        return response.json()