class HL7Parser:
    def parse(self, message_str):
        """
        Parse HL7 message string into a more flexible dictionary structure
        """
        try:
            # Split message into segments
            segments = message_str.strip().split('\n')
            message_dict = {
                'segments': [],
                'raw': message_str
            }
            
            for segment in segments:
                if not segment.strip():
                    continue
                    
                # Split segment into fields
                fields = segment.split('|')
                segment_name = fields[0]
                
                # Create segment dictionary
                segment_dict = {
                    'name': segment_name,
                    'fields': fields[1:],  # Skip segment name
                    'raw': segment
                }
                
                # Add parsed fields as named items for common segments
                if segment_name == 'MSH':
                    segment_dict.update({
                        'sending_app': fields[2] if len(fields) > 2 else '',
                        'sending_facility': fields[3] if len(fields) > 3 else '',
                        'receiving_app': fields[4] if len(fields) > 4 else '',
                        'receiving_facility': fields[5] if len(fields) > 5 else '',
                        'message_datetime': fields[6] if len(fields) > 6 else '',
                        'message_type': fields[8] if len(fields) > 8 else '',
                        'message_control_id': fields[9] if len(fields) > 9 else '',
                        'version': fields[11] if len(fields) > 11 else '2.5'
                    })
                elif segment_name == 'PID':
                    segment_dict.update({
                        'patient_id': fields[3] if len(fields) > 3 else '',
                        'patient_name': fields[5] if len(fields) > 5 else '',
                        'dob': fields[7] if len(fields) > 7 else '',
                        'gender': fields[8] if len(fields) > 8 else ''
                    })
                elif segment_name == 'OBR':
                    segment_dict.update({
                        'order_number': fields[2] if len(fields) > 2 else '',
                        'universal_service_id': fields[4] if len(fields) > 4 else '',
                        'observation_datetime': fields[7] if len(fields) > 7 else ''
                    })
                elif segment_name == 'OBX':
                    segment_dict.update({
                        'set_id': fields[1] if len(fields) > 1 else '',
                        'value_type': fields[2] if len(fields) > 2 else '',
                        'observation_id': fields[3] if len(fields) > 3 else '',
                        'observation_value': fields[5] if len(fields) > 5 else '',
                        'units': fields[6] if len(fields) > 6 else '',
                        'references_range': fields[7] if len(fields) > 7 else '',
                        'abnormal_flags': fields[8] if len(fields) > 8 else ''
                    })
                
                message_dict['segments'].append(segment_dict)
                
                # Store segment by name for easy access
                if segment_name not in message_dict:
                    message_dict[segment_name] = []
                message_dict[segment_name].append(segment_dict)
            
            return message_dict
            
        except Exception as e:
            raise Exception(f"Failed to parse HL7 message: {str(e)}")

    def get_segment(self, message, segment_name):
        """Helper method to get first segment of a specific type"""
        return message.get(segment_name, [{}])[0]

    def get_segments(self, message, segment_name):
        """Helper method to get all segments of a specific type"""
        return message.get(segment_name, [])

    def get_field_value(self, segment, field_index):
        """Helper method to safely get field value"""
        try:
            return segment['fields'][field_index] if len(segment['fields']) > field_index else ''
        except:
            return ''