import unittest
from src.hl7_parser import HL7Parser

class TestHL7Parser(unittest.TestCase):
    def setUp(self):
        self.parser = HL7Parser()

    def test_parse_msh(self):
        # Sample MSH segment
        msh_segment = "MSH|^~\\&|SendingApp|SendingFacility|ReceivingApp|ReceivingFacility|202407261000||ADT^A01|12345|P|2.5"
        parsed_msh = self.parser.parse(msh_segment)
        self.assertEqual(parsed_msh['MSH'][0]['message_type'], 'ADT^A01')
        self.assertEqual(parsed_msh['MSH'][0]['message_control_id'], '12345')

    def test_parse_pid(self):
        # Sample PID segment
        pid_segment = "PID|||1234567^PatientName^^^&amp;||20000101|M"
        parsed_pid = self.parser.parse(pid_segment)
        self.assertEqual(parsed_pid['PID'][0]['patient_id'], '1234567')
        self.assertEqual(parsed_pid['PID'][0]['patient_name'], 'PatientName')

    def test_parse_empty(self):
        parsed_empty = self.parser.parse("")
        self.assertEqual(len(parsed_empty['segments']), 0)

    def test_parse_invalid(self):
        with self.assertRaises(Exception):
            self.parser.parse("Invalid HL7 message")

    def test_get_segment(self):
        message = self.parser.parse(msh_segment + "\n" + pid_segment)
        msh = self.parser.get_segment(message, 'MSH')
        self.assertEqual(msh['message_type'], 'ADT^A01')

    def test_get_segments(self):
        message = self.parser.parse(msh_segment + "\n" + pid_segment + "\n" + pid_segment)
        pids = self.parser.get_segments(message, 'PID')
        self.assertEqual(len(pids), 2)

    def test_get_field_value(self):
        message = self.parser.parse(msh_segment)
        msh = self.parser.get_segment(message, 'MSH')
        self.assertEqual(self.parser.get_field_value(msh, 0), 'MSH')
        self.assertEqual(self.parser.get_field_value(msh, 100), '')


if __name__ == '__main__':
    unittest.main()
