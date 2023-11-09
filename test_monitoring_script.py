import unittest
from unittest.mock import patch, Mock
import requests
import monitoring_script # Replace with the actual name of your Python script

class TestMonitoringScript(unittest.TestCase):

    @patch('monitoring_script.requests.get')
    def test_check_for_200_response_success(self, mock_get):
        mock_get.return_value = Mock(status_code=200)
        result = monitoring_script.check_for_200_response("http://example.com")
        self.assertTrue(result)

    @patch('monitoring_script.requests.get')
    def test_check_for_200_response_failure(self, mock_get):
        mock_get.return_value = Mock(status_code=404)
        result = monitoring_script.check_for_200_response("http://example.com")
        self.assertFalse(result)

    @patch('monitoring_script.requests.get')
    def test_check_for_200_response_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError
        with self.assertRaises(requests.exceptions.ConnectionError):
            monitoring_script.check_for_200_response("http://example.com")

    @patch('monitoring_script.requests.get')
    def test_get_alertmanager_notification_health_for_opsgenie_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [{"value": [1234567890, "0"]}]
            }
        }
        mock_get.return_value = mock_response
        result = monitoring_script.get_alertmanager_notifification_health_for_opsgenie()
        self.assertTrue(result)

    @patch('monitoring_script.requests.get')
    def test_get_alertmanager_notification_health_for_opsgenie_failure(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [{"value": [1234567890, "1"]}]
            }
        }
        mock_get.return_value = mock_response
        result = monitoring_script.get_alertmanager_notifification_health_for_opsgenie()
        self.assertFalse(result)

    @patch('monitoring_script.requests.get')
    def test_send_opsgenie_heartbeat_success(self, mock_get):
        mock_get.return_value = Mock(status_code=202)
        result = monitoring_script.send_opsgenie_heartbeat("heartbeat_name")
        self.assertIsNone(result)  # Assuming your function doesn't return anything

    @patch('monitoring_script.requests.get')
    def test_send_opsgenie_heartbeat_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError
        with self.assertRaises(requests.exceptions.HTTPError):
            monitoring_script.send_opsgenie_heartbeat("heartbeat_name")

    @patch('monitoring_script.get_alertmanager_notifification_health_for_opsgenie')
    @patch('monitoring_script.check_for_200_response')
    def test_is_cluster_healthy_all_checks_pass(self, mock_check_for_200, mock_get_alertmanager):
        mock_check_for_200.return_value = True
        mock_get_alertmanager.return_value = True
        result = monitoring_script.is_cluster_healthy()
        self.assertTrue(result)

    @patch('monitoring_script.get_alertmanager_notifification_health_for_opsgenie')
    @patch('monitoring_script.check_for_200_response')
    def test_is_cluster_healthy_some_checks_fail(self, mock_check_for_200, mock_get_alertmanager):
        mock_check_for_200.side_effect = [True, False, True, False]  # Simulating some checks passing and some failing
        mock_get_alertmanager.return_value = True
        result = monitoring_script.is_cluster_healthy()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
