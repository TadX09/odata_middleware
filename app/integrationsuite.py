import requests
from app.env_variables import X_API_KEY, IS_VIRTUAL_HOST, IS_VIRTUAL_PORT

#Class to perform basic CRUD REST API Operation in remote target
class ISOperations:

    def __init__(self, basePath):
        self.url = f"{IS_VIRTUAL_HOST}:{IS_VIRTUAL_PORT}/{basePath}"

    #Method to perfom basic POST HTTP Request on Integration Suite Proxy.
    #Example of a call of the method below <constructor>.execute_post_operation('Call',obj, 'application/json','SP')
    def execute_post_operation(self, path: str, body: str, contentType: str, resource: str):
        completeURL = f"https://{self.url}/{path}/{resource}"
        headers = {"Content-Type": contentType, "x-api-key": X_API_KEY}
        response = requests.post(completeURL, headers=headers, json=body)
        return response.json()
        