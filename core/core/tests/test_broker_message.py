from django.test import TestCase
from core.broker_message_client import BaseRabbitMQClient, RabbitMQClient
from pika import ConnectionParameters
from unittest.mock import patch, MagicMock
from json import dumps


class BaseRabbitMQClientTestCase(TestCase):

    def setUp(self):
        self.host = 'test_host'
        self.queue = 'test_queue'
        self.exchange = 'test_exchange'
        self.client = BaseRabbitMQClient(
            host=self.host,
            exchange=self.exchange,
            queue=self.queue
        )

    def test_init_method(self):
        self.assertTrue(isinstance(self.client.connection_params, ConnectionParameters))

    @patch('core.broker_message_client.BlockingConnection')
    def test_connect_and_channel_success(self, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel

        with self.client.connect_and_channel() as channel:
            mock_connection.return_value.channel.assert_called_once()

        mock_channel.close.assert_called_once()
        mock_connection.return_value.close.assert_called_once()

    @patch('core.broker_message_client.BlockingConnection')
    @patch('core.broker_message_client.logger.error')
    def test_connect_and_channel_exception_handling(self, mock_logger_error, mock_connection):
        mock_connection.side_effect = Exception("Connection error")

        try:
            with self.client.connect_and_channel():
                pass
            self.fail()
        except RuntimeError:
            pass

        mock_logger_error.assert_called_once_with("Error with RabbitMQ Connection error")

    @patch('core.broker_message_client.BlockingConnection')
    @patch('core.broker_message_client.logger.warning')
    def test_connect_and_channel_close_channel_failure(self, mock_logger_warning, mock_connection):
        mock_channel = MagicMock()
        mock_channel.close.side_effect = Exception("Channel close error")
        mock_connection.return_value.channel.return_value = mock_channel

        with self.client.connect_and_channel():
            pass
        mock_connection.return_value.close.assert_called_once()
        mock_logger_warning.assert_any_call("Failed to close channel: Channel close error")

    @patch('core.broker_message_client.BlockingConnection')
    @patch('core.broker_message_client.logger.warning')
    def test_connect_and_channel_close_connection_failure(self, mock_logger_warning, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.close.side_effect = Exception("Connection close error")
        mock_connection.return_value.channel.return_value = mock_channel

        with self.client.connect_and_channel():
            pass

        mock_channel.close.assert_called_once()
        mock_logger_warning.assert_any_call("Failed to close connection: Connection close error")

    @patch('core.broker_message_client.BlockingConnection')
    def test_consume_message(self, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel

        callback = MagicMock()
        self.client.consume_message(callback)

        mock_channel.basic_consume.assert_called_once_with(
            queue=self.queue,
            on_message_callback=callback
        )
        mock_channel.start_consuming.assert_called_once()

    def test_properties_generate_with_data(self):
        data = {
            "reply_to": "test_reply",
            "exchange": "test_exchange",
            "queue": "test_queue",
            "method_type": "POST"
        }
        data_to_response = data.copy()
        properties = self.client._properties_generate(data_to_response)

        self.assertEqual(properties.reply_to, data["reply_to"])
        self.assertEqual(properties.headers["exchange"], data["exchange"])
        self.assertEqual(properties.headers["queue"], data["queue"])
        self.assertEqual(properties.headers["method_type"], data["method_type"])

    def test_properties_generate_without_data(self):
        properties = self.client._properties_generate(None)
        self.assertIsNone(properties)

    def test_properties_generate_missing_exchange_or_queue(self):
        data_to_response = {"reply_to": "test_reply"}
        with self.assertRaises(ValueError):
            self.client._properties_generate(data_to_response)

    @patch('core.broker_message_client.BlockingConnection')
    @patch('core.broker_message_client.BaseRabbitMQClient._properties_generate')
    def test_publish_message_success(self, mock_properties_generate, mock_connection):
        mock_channel = MagicMock()
        mock_connection.return_value.channel.return_value = mock_channel
        mock_properties_generate.return_value = None

        message = "test_message"

        self.client.publish_message(message)

        mock_channel.basic_publish.assert_called_once_with(
            exchange=self.exchange,
            routing_key=self.queue,
            body=message,
            properties=None
        )


class RabbitMQClientTestCase(TestCase):
    def setUp(self):
        self.host = 'test_host'
        self.queue = 'test_queue'
        self.exchange = 'test_exchange'
        self.client = RabbitMQClient(
            host=self.host,
            exchange=self.exchange,
            queue=self.queue
        )

        self.body_message_handler = MagicMock()
        self.message_handler_endpoint = "http://example.com/api"
        self.message_handler_payload = {"key": "value"}

    def test_parse_message_success(self):
        body = {
            'endpoint': r'http://example.com/api',
            'payload': {
                'title': 'test_title_payload',
                'description': 'test_description_payload'
            }
        }

        encode_body = dumps(body).encode('utf-8')
        endpoint, payload = self.client.parse_message(body=encode_body)
        self.assertEqual(endpoint, body['endpoint'])
        self.assertEqual(payload, body['payload'])

    def test_parse_message_empty_body(self):
        body = b''

        with self.assertRaises(ValueError) as context:
            self.client.parse_message(body=body)

        self.assertTrue(
            "No JSON object could be decoded" in str(context.exception) or "Expecting" in str(context.exception))

    def test_parse_message_no_payload(self):
        body = {
            'endpoint': r'http://example.com/api'
        }

        encode_body = dumps(body).encode('utf-8')
        endpoint, payload = self.client.parse_message(body=encode_body)

        self.assertEqual(endpoint, body['endpoint'])
        self.assertIsNone(payload)

    @patch('core.broker_message_client.rabbitmq_message_exceptions', lambda x: x)
    @patch('core.broker_message_client.RabbitMQClient.parse_message')
    @patch('core.broker_message_client.request')
    def test_message_handler_success(self, mock_request, mock_parse_message):
        mock_parse_message.return_value = (self.message_handler_endpoint, self.message_handler_payload)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"response": "ok"}'
        mock_response.json.return_value = {"response": "ok"}
        mock_request.return_value = mock_response

        channel = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        properties.headers = {
            "method_type": "POST",
            "exchange": "test_exchange",
            "queue": "test_queue",
        }
        properties.reply_to = "reply_queue"
        RabbitMQClient.message_handler(self.body_message_handler, channel, method, properties)

        mock_parse_message.assert_called_once_with(self.body_message_handler)
        mock_request.assert_called_once_with(
            "POST", self.message_handler_endpoint, json=self.message_handler_payload, timeout=1
        )
        channel.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)
        channel.basic_publish.assert_called_once_with(
            exchange="test_exchange",
            routing_key="test_queue",
            body={
                "status_code": 200,
                "data": {"response": "ok"},
            },
        )

    @patch('core.broker_message_client.rabbitmq_message_exceptions', lambda x: x)
    @patch('core.broker_message_client.RabbitMQClient.parse_message')
    @patch('core.broker_message_client.request')
    def test_message_handler_no_reply_to(self, mock_request, mock_parse_message):
        mock_parse_message.return_value = (self.message_handler_endpoint, self.message_handler_payload)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        channel = MagicMock()
        method = MagicMock()
        properties = MagicMock()
        properties.headers = {
            "method_type": "POST",
        }
        properties.reply_to = None
        RabbitMQClient.message_handler(self.body_message_handler, channel, method, properties)

        mock_parse_message.assert_called_once_with(self.body_message_handler)
        mock_request.assert_called_once_with(
            "POST", self.message_handler_endpoint, json=self.message_handler_payload, timeout=1
        )
        channel.basic_ack.assert_called_once_with(delivery_tag=method.delivery_tag)
        channel.basic_publish.assert_not_called()
