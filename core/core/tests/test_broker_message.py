from django.test import TestCase
from core.broker_message_client import RabbitMQClient
from pika import ConnectionParameters
from unittest.mock import patch, MagicMock


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
