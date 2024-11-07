class HL7ToFHIRConverter:
    def convert(self, hl7_message):
        """
        Convert HL7 message to FHIR resource
        """
        try:
            # Get message type from MSH segment
            msh = hl7_message.get('MSH', [{}])[0]
            message_type = msh.get('message_type', '').split('^')[0]
            
            if message_type == 'ADT':
                return self._convert_adt(hl7_message)
            elif message_type == 'ORU':
                return self._convert_oru(hl7_message)
            elif message_type == 'SIU':
                return self._convert_siu(hl7_message)
            else:
                return self._convert_generic(hl7_message)
                
        except Exception as e:
            raise Exception(f"Failed to convert to FHIR: {str(e)}")
    
    def _convert_adt(self, hl7_message):
        """Convert ADT message to FHIR Patient resource"""
        pid = hl7_message.get('PID', [{}])[0]
        
        patient = {
            "resourceType": "Patient",
            "identifier": [{
                "system": "HL7v2",
                "value": pid.get('patient_id', '').split('^')[0]
            }],
            "active": True
        }
        
        # Add name if available
        if pid.get('patient_name'):
            names = pid['patient_name'].split('^')
            patient["name"] = [{
                "family": names[0] if len(names) > 0 else '',
                "given": [names[1]] if len(names) > 1 else []
            }]
        
        # Add gender if available
        if pid.get('gender'):
            patient["gender"] = self._map_gender(pid['gender'])
            
        # Add birth date if available
        if pid.get('dob'):
            patient["birthDate"] = pid['dob']
            
        return patient
    
    def _convert_oru(self, hl7_message):
        """Convert ORU message to FHIR Observation resource"""
        obx_segments = hl7_message.get('OBX', [])
        observations = []
        
        for obx in obx_segments:
            observation = {
                "resourceType": "Observation",
                "status": "final",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": obx.get('observation_id', '').split('^')[0],
                        "display": obx.get('observation_id', '').split('^')[1] if '^' in obx.get('observation_id', '') else ''
                    }]
                }
            }
            
            # Add value
            if obx.get('observation_value'):
                try:
                    value = float(obx['observation_value'])
                    observation["valueQuantity"] = {
                        "value": value,
                        "unit": obx.get('units', '')
                    }
                except ValueError:
                    observation["valueString"] = obx['observation_value']
            
            observations.append(observation)
        
        return observations[0] if observations else {"resourceType": "Observation", "status": "unknown"}
    
    def _convert_siu(self, hl7_message):
        """Convert SIU message to FHIR Appointment resource"""
        sch = hl7_message.get('SCH', [{}])[0]
        
        appointment = {
            "resourceType": "Appointment",
            "status": "booked",
            "description": sch.get('fields', [None] * 7)[6] or "No description"
        }
        
        return appointment
    
    def _convert_generic(self, hl7_message):
        """Convert any message to a basic FHIR resource"""
        return {
            "resourceType": "Basic",
            "id": hl7_message.get('MSH', [{}])[0].get('message_control_id', ''),
            "code": {
                "coding": [{
                    "system": "HL7v2",
                    "code": hl7_message.get('MSH', [{}])[0].get('message_type', ''),
                    "display": "HL7v2 Message"
                }]
            }
        }
    
    def _map_gender(self, hl7_gender):
        """Map HL7 gender to FHIR gender"""
        gender_map = {
            'M': 'male',
            'F': 'female',
            'O': 'other',
            'U': 'unknown',
            'A': 'other',
            'N': 'other'
        }
        return gender_map.get(hl7_gender.upper(), 'unknown') 