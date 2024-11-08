import unittest
from src.fhir_converter import HL7ToFHIRConverter

class TestFHIRConverter(unittest.TestCase):
    def setUp(self):
        self.converter = HL7ToFHIRConverter()

    def test_convert_adt(self):
        # Sample parsed ADT message (replace with actual parsed data)
        adt_message = {'PID': [{'patient_id': '12345', 'patient_name': 'John^Doe', 'dob': '20000101', 'gender': 'M'}]}
        fhir_patient = self.converter.convert(adt_message)
        self.assertEqual(fhir_patient['resourceType'], 'Patient')
        self.assertEqual(fhir_patient['identifier'][0]['value'], '12345')

    def test_convert_oru(self):
        # Sample parsed ORU message (replace with actual parsed data)
        oru_message = {'OBX': [{'observation_id': '1234^Test', 'observation_value': '10'}]}
        fhir_observation = self.converter.convert(oru_message)
        self.assertEqual(fhir_observation['resourceType'], 'Observation')
        self.assertEqual(fhir_observation['code']['coding'][0]['code'], '1234')

    def test_convert_siu(self):
        # Sample parsed SIU message (replace with actual parsed data)
        siu_message = {'SCH': [{'fields': ['field1', 'field2', 'field3', 'field4', 'field5', 'field6', 'Appointment Description']}]}
        fhir_appointment = self.converter.convert(siu_message)
        self.assertEqual(fhir_appointment['resourceType'], 'Appointment')
        self.assertEqual(fhir_appointment['description'], 'Appointment Description')

    def test_convert_generic(self):
        # Sample parsed generic message (replace with actual parsed data)
        generic_message = {'MSH': [{'message_type': 'Generic', 'message_control_id': '123'}]}
        fhir_basic = self.converter.convert(generic_message)
        self.assertEqual(fhir_basic['resourceType'], 'Basic')
        self.assertEqual(fhir_basic['id'], '123')

    def test_map_gender(self):
        self.assertEqual(self.converter._map_gender('M'), 'male')
        self.assertEqual(self.converter._map_gender('F'), 'female')
        self.assertEqual(self.converter._map_gender('O'), 'other')
        self.assertEqual(self.converter._map_gender('U'), 'unknown')


if __name__ == '__main__':
    unittest.main()
