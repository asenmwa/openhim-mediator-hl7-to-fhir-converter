from flask import Flask, request, jsonify
from mediator import OpenHIMMediator
from hl7_parser import HL7Parser
from fhir_converter import HL7ToFHIRConverter
from fhir_client import FHIRClient
import os
import signal
import sys
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
mediator = OpenHIMMediator()
hl7_parser = HL7Parser()
fhir_converter = HL7ToFHIRConverter()
fhir_client = FHIRClient(
    base_url=os.getenv('FHIR_SERVER_URL', 'http://hapi-fhir:8080/fhir')
)

def signal_handler(sig, frame):
    """Handle shutdown gracefully"""
    print('Shutting down...')
    mediator.stop_heartbeat()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@app.route('/hl7', methods=['POST'])
def receive_hl7():
    try:
        # Get HL7 message from request
        hl7_message = request.data.decode('utf-8')
        
        # Parse HL7 message
        parsed_hl7 = hl7_parser.parse(hl7_message)
        
        # Convert to FHIR
        fhir_resource = fhir_converter.convert(parsed_hl7)
        
        # Send to FHIR server
        response = fhir_client.send(fhir_resource)
        
        # Create response for OpenHIM
        result = {
            'status': 'Success',
            'response': response
        }
        
        return mediator.response(
            request=request,
            response=result,
            status_code=200
        )
        
    except Exception as e:
        error_result = {
            'status': 'Error',
            'message': str(e)
        }
        return mediator.response(
            request=request,
            response=error_result,
            status_code=500
        )

if __name__ == '__main__':
    mediator.register_mediator()
    app.run(host='0.0.0.0', port=3000) 