import requests

class FHIRClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        
    def send(self, resource):
        """
        Send FHIR resource to FHIR server
        """
        resource_type = resource['resourceType']
        url = f"{self.base_url}/{resource_type}"
        
        headers = {
            'Content-Type': 'application/fhir+json',
            'Accept': 'application/fhir+json'
        }
        
        try:
            response = requests.post(url, json=resource, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to send to FHIR server: {str(e)}") 