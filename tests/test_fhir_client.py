import unittest
from unittest.mock import patch
from src.fhir_client import FHIRClient

class TestFHIRClient(unittest.TestCase):
    @patch('src.fhir_client.requests.post')
    def test_send_success(self, mock_post):
        client = FHIRClient('http://example.com/fhir')
        resource = {'resourceType': 'Patient'}
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {'id': '1'}
        response = client.send(resource)
        self.assertEqual(response, {'id': '1'})
        mock_post.assert_called_once()

    @patch('src.fhir_client.requests.post')
    def test_send_failure(self, mock_post):
        client = FHIRClient('http://example.com/fhir')
        resource = {'resourceType': 'Patient'}
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {'error': 'Internal Server Error'}
        with self.assertRaises(Exception):
            client.send(resource)
        mock_post.assert_called_once()

    @patch('src.fhir_client.requests.post')
    def test_send_exception(self, mock_post):
        client = FHIRClient('http://example.com/fhir')
        resource = {'resourceType': 'Patient'}
        mock_post.side_effect = Exception('Network Error')
        with self.assertRaises(Exception):
            client.send(resource)
        mock_post.assert_called_once()


if __name__ == '__main__':
    unittest.main()
