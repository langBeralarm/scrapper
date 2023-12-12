import json
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from mqtt.mqtt_client import MqttClient


class MqttClientPublishTestCase(TestCase):
    @patch("mqtt.mqtt_client.mqtt.Client")
    def setUp(self, mock_client: MagicMock) -> None:
        self.mqtt_client = MqttClient("", 1883, [("test/test", 2)])
        self.mqtt_client.client = mock_client
        self.topic = "test/test"
        self.payload = {
            "type": "test",
            "data": {
                "key": "value",
            },
        }

    def test_publish(self):
        # Arrange
        self.mqtt_client.connected = True
        # Act
        self.mqtt_client._publish(self.topic, self.payload)
        # Assert
        self.mqtt_client.client.publish.assert_called_once_with(
            self.topic, json.dumps(self.payload), 2, False
        )

    @patch("mqtt.mqtt_client.logger")
    def test_publish_with_type_error(self, logger: MagicMock):
        # Arrange
        self.mqtt_client.connected = True
        # Act
        with patch("json.dumps", side_effect=TypeError()):
            self.mqtt_client._publish(self.topic, self.payload)
        # Assert
        self.mqtt_client.client.publish.assert_not_called()
        logger.error.assert_called_once_with("Payload has invalid keys")

    @patch("mqtt.mqtt_client.logger")
    def test_publish_with_value_error(self, logger: MagicMock):
        # Arrange
        self.mqtt_client.connected = True
        self.mqtt_client.client.publish.side_effect = ValueError()
        expected_calls = [
            call("Outgoing queue is full - retrying to publish message"),
            call("Outgoing queue is full - retrying to publish message"),
            call("Outgoing queue is full - retrying to publish message"),
            call("Could not publish message"),
        ]
        # Act
        self.mqtt_client._publish(self.topic, self.payload)
        # Assert
        self.assertEqual(self.mqtt_client.client.publish.call_count, 3)
        self.assertEqual(logger.warning.call_args_list, expected_calls)

    @patch("mqtt.mqtt_client.logger")
    def test_publish_with_runtime_error(self, logger: MagicMock):
        # Arrange
        self.mqtt_client.connected = True
        self.mqtt_client.client.publish.side_effect = RuntimeError()
        expected_calls = [
            call("Message could not be published - retrying to publish message"),
            call("Message could not be published - retrying to publish message"),
            call("Message could not be published - retrying to publish message"),
            call("Could not publish message"),
        ]
        # Act
        self.mqtt_client._publish(self.topic, self.payload)
        # Assert
        self.assertEqual(self.mqtt_client.client.publish.call_count, 3)
        self.assertEqual(logger.warning.call_args_list, expected_calls)

    @patch("mqtt.mqtt_client.mqtt.Client.publish")
    @patch("json.dumps")
    @patch("mqtt.mqtt_client.logger")
    def test_publish_not_connected(
        self, logger: MagicMock, dumps: MagicMock, publish: MagicMock
    ):
        # Act
        self.mqtt_client._publish(self.topic, self.payload)
        # Assert
        logger.warning.assert_called_once_with(
            "Can not publish message - Not connected to the MQTT Broker"
        )
        dumps.assert_not_called()
        self.mqtt_client.client.publish.assert_not_called()

    @patch("mqtt.mqtt_client.MqttClient._retry_connection")
    @patch("mqtt.mqtt_client.mqtt.Client.loop_start")
    @patch("mqtt.mqtt_client.mqtt.Client.connect")
    @patch("mqtt.mqtt_client.mqtt.Client.will_set")
    @patch("mqtt.mqtt_client.mqtt.Client.username_pw_set")
    def test_init(
        self,
        pw_set: MagicMock,
        will_set: MagicMock,
        connect: MagicMock,
        loop_start: MagicMock,
        retry_connection: MagicMock,
    ):
        # Act
        self.mqtt_client.init()
        # Assert
        self.assertEqual(
            self.mqtt_client.on_connect, self.mqtt_client.client.on_connect
        )
        self.assertEqual(
            self.mqtt_client.on_disconnect, self.mqtt_client.client.on_disconnect
        )
        self.assertEqual(
            self.mqtt_client.on_message, self.mqtt_client.client.on_message
        )
        self.assertEqual(
            self.mqtt_client.on_publish, self.mqtt_client.client.on_publish
        )
        self.mqtt_client.client.username_pw_set.assert_called_once()
        self.mqtt_client.client.will_set.assert_called_once()
        self.mqtt_client.client.connect.assert_called_once()
        self.mqtt_client.client.loop_start.assert_called_once()
        retry_connection.assert_not_called()

    @patch("mqtt.mqtt_client.logger")
    @patch("mqtt.mqtt_client.MqttClient._retry_connection")
    @patch("mqtt.mqtt_client.mqtt.Client.loop_start")
    @patch("mqtt.mqtt_client.mqtt.Client.connect")
    @patch("mqtt.mqtt_client.mqtt.Client.will_set")
    @patch("mqtt.mqtt_client.mqtt.Client.username_pw_set")
    def test_init_with_connection_refused_error(
        self,
        pw_set: MagicMock,
        will_set: MagicMock,
        connect: MagicMock,
        loop_start: MagicMock,
        retry_connection: MagicMock,
        logger: MagicMock,
    ):
        # Arrange
        self.mqtt_client.client.connect = connect
        self.mqtt_client.client.connect.side_effect = ConnectionRefusedError()
        # Act
        self.mqtt_client.init()
        # Assert
        self.mqtt_client.client.username_pw_set.assert_called_once()
        self.mqtt_client.client.will_set.assert_called_once()
        self.mqtt_client.client.connect.assert_called_once()
        # self.mqtt_client.client.loop_start.assert_not_called()
        logger.info.assert_called_with("The MQTT Broker is not available.")
        retry_connection.assert_called_once()

    @patch("mqtt.mqtt_client.MqttClient._publish")
    @patch("mqtt.mqtt_client.mqtt.Client.subscribe")
    def test_on_connect(self, subscribe: MagicMock, publish: MagicMock):
        # Act
        self.mqtt_client.on_connect(self.mqtt_client.client, {}, {}, 0)
        # Assert
        self.assertTrue(self.mqtt_client.connected)
        self.assertEqual(self.mqtt_client.retries, 3)
        self.mqtt_client.client.subscribe.assert_called_once_with(
            self.mqtt_client.topics
        )
        publish.assert_called_once_with(
            "test/status",
            {"type": "status", "data": {"offline": False, "willful": True}},
        )

    @patch("mqtt.mqtt_client.MqttClient._retry_connection")
    def test_on_connect_1(self, retry_connection: MagicMock):
        # Act
        self.mqtt_client.on_connect(self.mqtt_client.client, {}, {}, 1)
        # Assert
        retry_connection.assert_called_once_with(1)

    @patch("mqtt.mqtt_client.logger")
    def test_on_disconnect(self, logger: MagicMock):
        # Act
        self.mqtt_client.on_disconnect(self.mqtt_client.client, {}, 0)
        # Assert
        self.assertFalse(self.mqtt_client.connected)
        logger.info.assert_called_once_with(
            "The MQTT Client successfully disconnected | RC %d", 0
        )

    @patch("mqtt.mqtt_client.logger")
    def test_on_disconnect_1(self, logger: MagicMock):
        # Act
        self.mqtt_client.on_disconnect(self.mqtt_client, {}, 1)
        # Assert
        self.assertFalse(self.mqtt_client.connected)
        logger.warning.assert_called_once_with(
            "The MQTT Client unexpectedly disconnected | RC %d", 1
        )

    @patch("mqtt.mqtt_client.mqtt.Client.loop_stop")
    @patch("mqtt.mqtt_client.mqtt.Client.disconnect")
    @patch("mqtt.mqtt_client.mqtt.Client.unsubscribe")
    @patch("mqtt.mqtt_client.MqttClient._publish")
    def test_disconnect(
        self,
        publish: MagicMock,
        unsubscribe: MagicMock,
        disconnect: MagicMock,
        loop_stop: MagicMock,
    ):
        # Arrange
        expected_calls = [call(topic[0]) for topic in self.mqtt_client.topics]
        # Act
        self.mqtt_client.disconnect()
        # Assert
        publish.assert_called_once_with(
            "test/status",
            {"type": "status", "data": {"offline": True, "willful": True}},
        )
        self.assertEqual(
            self.mqtt_client.client.unsubscribe.call_args_list, expected_calls
        )
        self.mqtt_client.client.disconnect.assert_called_once()
        self.mqtt_client.client.loop_stop.assert_called_once()

    @patch("mqtt.mqtt_client.logger")
    @patch("time.sleep")
    @patch("mqtt.mqtt_client.mqtt.Client.loop_start")
    @patch("mqtt.mqtt_client.mqtt.Client.connect")
    @patch("mqtt.mqtt_client.mqtt.Client.loop_stop")
    def test_retry_connection(
        self,
        loop_stop: MagicMock,
        connect: MagicMock,
        loop_start: MagicMock,
        sleep: MagicMock,
        logger: MagicMock,
    ):
        # Arrange
        expected_calls = [
            call(
                "The MQTT client could not connect to the MQTT broker, returned with RC %s",  # noqa: E501
                "",
            ),
        ]
        # Act
        self.mqtt_client._retry_connection("")
        # Assert
        self.assertEqual(self.mqtt_client.client.loop_stop.call_count, 3)
        self.assertEqual(self.mqtt_client.client.connect.call_count, 3)
        self.assertEqual(self.mqtt_client.client.loop_start.call_count, 3)
        self.assertEqual(sleep.call_count, 3)
        self.assertFalse(self.mqtt_client.connected)
        self.assertEqual(self.mqtt_client.retries, 0)
        self.assertEqual(logger.warning.call_args_list, expected_calls)
