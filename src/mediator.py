import json
import os
import requests
import threading
import time
from datetime import datetime
from requests.auth import HTTPBasicAuth

class OpenHIMMediator:
    def __init__(self):
        self.config = self._load_config()
        self.openhim_url = os.getenv('OPENHIM_URL')
        self.username = os.getenv('OPENHIM_USERNAME')
        self.password = os.getenv('OPENHIM_PASSWORD')
        self.auth = HTTPBasicAuth(self.username, self.password)
        self.uptime = 0
        self._heartbeat_thread = None
        self._running = False

    def _load_config(self):
        """Load mediator config from JSON file"""
        config_path = os.path.join(os.path.dirname(__file__), '../config/mediator.json')
        with open(config_path) as f:
            return json.load(f)

    def register_mediator(self):
        """Register this mediator with the OpenHIM core"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.post(
                f"{self.openhim_url}/mediators",
                json=self.config,
                headers=headers,
                auth=self.auth,
                verify=False  # Only use in development
            )
            response.raise_for_status()
            print("Successfully registered mediator")
            
            # Start heartbeat
            self._start_heartbeat()
            
        except Exception as e:
            print(f"Failed to register mediator: {str(e)}")

    def _heartbeat_worker(self):
        """Worker function for heartbeat thread"""
        while self._running:
            try:
                response = requests.post(
                    f"{self.openhim_url}/mediators/{self.config['urn']}/heartbeat",
                    json={'uptime': self.uptime},
                    auth=self.auth,
                    verify=False
                )
                if response.status_code == 200:
                    print(f"Heartbeat sent successfully. Uptime: {self.uptime} seconds")
                else:
                    print(f"Failed to send heartbeat. Status code: {response.status_code}")
                
                # Increment uptime
                self.uptime += 10
                
                # Wait for 10 seconds before next heartbeat
                time.sleep(10)
                
            except Exception as e:
                print(f"Error sending heartbeat: {str(e)}")
                time.sleep(5)  # Wait 5 seconds before retry on error

    def _start_heartbeat(self):
        """Start the heartbeat thread"""
        if not self._heartbeat_thread or not self._heartbeat_thread.is_alive():
            self._running = True
            self._heartbeat_thread = threading.Thread(target=self._heartbeat_worker)
            self._heartbeat_thread.daemon = True  # Thread will exit when main program exits
            self._heartbeat_thread.start()
            print("Heartbeat thread started")

    def stop_heartbeat(self):
        """Stop the heartbeat thread"""
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join()
            print("Heartbeat thread stopped")

    def response(self, request, response, status_code):
        """Format response for OpenHIM"""
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        
        return {
            'x-mediator-urn': self.config['urn'],
            'status': 'Successful' if status_code == 200 else 'Failed',
            'response': {
                'status': status_code,
                'body': response,
                'timestamp': timestamp,
                'headers': {'content-type': 'application/json'}
            },
            'properties': {
                'property': 'Primary Route',
                'value': 'HL7 to FHIR conversion'
            },
            'orchestrations': [{
                'name': 'HL7 to FHIR Conversion',
                'request': {
                    'method': request.method,
                    'headers': dict(request.headers),
                    'body': request.get_data(as_text=True),
                    'timestamp': timestamp
                },
                'response': {
                    'status': status_code,
                    'headers': {'content-type': 'application/json'},
                    'body': response,
                    'timestamp': timestamp
                }
            }]
        }

    def send_metrics(self, metrics):
        """Send metrics to OpenHIM"""
        try:
            requests.post(
                f"{self.openhim_url}/metrics",
                json=metrics,
                auth=self.auth,
                verify=False
            )
        except Exception as e:
            print(f"Failed to send metrics: {str(e)}")