# pylint: disable=fixme
import json
import logging
import random
import subprocess  # nosec
import time
from typing import Optional

import paho.mqtt.client as mqtt

# Get name of docker container
container_name: str = str(subprocess.check_output(["sh", "-c", "echo $NAME"]))  # nosec

logger = logging.getLogger(__name__)


class MqttClient:  # pylint: disable=too-many-instance-attributes
    """
    MqttClient for establishing connections to an MQTT Broker, sending and handling
    received messages.
    """

    def __init__(self, host: str, port: int, topics: list[tuple[str, int]]):
        self.host: str = host
        self.port: int = port
        self.keep_alive: int = 60
        self.client: Optional[mqtt.Client] = None
        self.default_qos: int = 2  # Is equal to exactly once
        self.topics: list[tuple[str, int]] = topics
        self.connected: bool = False
        self.tries: int = 0

    def init(self):
        """Initialize the MqttClient.

        Set a last will message and try to connect to the MQTT broker.
        """
        # Give the client a certain client_id to identify it
        logger.info("Initializing Paho MQTT Client")
        self.client: mqtt.Client = mqtt.Client(  # type: ignore[no-redef]
            client_id=container_name,
            userdata={},
        )
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish

        # TODO: Verify encryption with tls or --opt encryption in docker swarm ?
        # https://github.com/docker/labs/blob/master/networking/concepts/11-security.md
        self.client.username_pw_set("tester", "password12")  # TODO: Change this
        # Set a last will message to enable subscribers to determine this clients status
        self.client.will_set(
            "test/status",
            json.dumps({"type": "status", "data": {"offline": True, "willful": False}}),
            self.default_qos,
        )
        logger.info(
            "Connecting to MQTT Broker on %s:%d with keepalive %d",
            self.host,
            self.port,
            self.keep_alive,
        )
        try:
            self.client.connect(self.host, self.port, self.keep_alive)
            self.client.loop_start()
        except ConnectionRefusedError:
            logger.info("The MQTT Broker is not available.")
            self._retry_connection("-")

    def on_connect(self, _client: mqtt.Client, _userdata: dict, _flags: dict, rc: int):
        """Callback method for CONNACK messages from the MQTT broker.

        Subscribes to topics and publishes a status message if the connection is
        successful. Otherwise the client tries to reconnect to the MQTT broker.
        """
        if rc == 0:
            self.connected = True
            logger.info(
                "The MQTT client successfully connected to the MQTT broker with RC %d",
                rc,
            )
            _client.subscribe(self.topics)
            self._publish(
                "test/status",
                {"type": "status", "data": {"offline": False, "willful": True}},
            )
            self.tries = 0
            return

        self._retry_connection(rc)

    def _retry_connection(self, rc: str | int):
        """Retry to establish a connection with the MQTT broker."""
        if self.client is None:
            logger.error("The Client is not defined")
            return
        while self.tries < 3 and not self.connected:
            self.client.loop_stop()
            try:
                self.client.connect(self.host, self.port, self.keep_alive)
                self.client.loop_start()
            except ConnectionRefusedError:
                pass
            finally:
                # TODO: Implement exponential backoff while trying to reconnect
                time.sleep(self._get_exponential_backoff(self.tries))
                self.tries += 1
        logger.warning(
            "The MQTT client could not connect to the MQTT broker, returned with RC %s",
            str(rc),
        )

    # TODO: Check if option for masking logs should be used
    def _publish(self, topic: str, payload: dict, qos=2, retain=False, _tries=3):
        """Try to publish a message to the MQTT broker."""
        if self.client is None:
            logger.error("The Client is not defined")
            return
        if not self.connected:
            logger.warning("Can not publish message - Not connected to the MQTT Broker")
            return
        if _tries <= 0:
            logger.warning("Could not publish message")
            return
        try:
            _payload: str = json.dumps(payload)
            info: mqtt.MQTTMessageInfo = self.client.publish(
                topic, _payload, qos, retain
            )
            info.wait_for_publish(1)
            logger.info(
                "Sent %s to topic: %s with payload: %s", str(info.mid), topic, _payload
            )
        except TypeError:
            logger.error("Payload has invalid keys")
        # TODO: Check if this should be done because message retry occurs automatically
        except ValueError:
            logger.warning("Outgoing queue is full - retrying to publish message")
            self._publish(topic, payload, qos, retain, _tries - 1)
        except RuntimeError:
            logger.warning(
                "Message could not be published - retrying to publish message"
            )
            self._publish(topic, payload, qos, retain, _tries - 1)

    @staticmethod
    def on_publish(_client: mqtt.Client, _userdata: dict, mid):
        """Callback method for messages transmission completion to the MQTT broker."""
        logger.info("Successfully published %s", str(mid))

    def on_disconnect(self, _client: mqtt.Client, _userdata: dict, rc: int):
        """Callback method for the client disconnecting from the MQTT broker."""
        self.connected = False
        if rc == 0:
            logger.info(
                "The MQTT Client successfully disconnected | RC %d",
                rc,
            )
            return
        logger.warning(
            "The MQTT Client unexpectedly disconnected | RC %d",
            rc,
        )

    @staticmethod
    def on_message(_client: mqtt.Client, _userdata: dict, message: mqtt.MQTTMessage):
        """Callback method for messages received on a subscribed topic."""
        try:
            _payload = json.loads(message.payload)  # noqa: F841
            logger.info(
                "Received payload: %s on topic: %s", message.payload, message.topic
            )
        except json.JSONDecodeError:
            logger.warning("An error occurred while decoding the MQTT message payload")

    def disconnect(self):
        """Cleanly disconnect from the MQTT Broker.

        Publish status message, unsubscribe from subscribed topics and disconnect from
        the MQTT broker.
        """
        if self.client is None:
            logger.error("The Client is not defined")
            return

        self._publish(
            "test/status",
            {"type": "status", "data": {"offline": True, "willful": True}},
        )

        for topic in self.topics:
            self.client.unsubscribe(topic[0])
        self.client.disconnect()
        self.client.loop_stop()
        logger.info("Disconnecting from MQTT Broker ...")

    @staticmethod
    def _get_exponential_backoff(tries: int) -> float:
        """Calculate an exponential backoff with jitter."""
        return 2**tries + (random.randint(0, 1000) / 1000)  # nosec B311
