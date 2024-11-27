from django.test import TestCase
from core.broker_message_client import RabbitMQClient
from pika import ConnectionParameters


class RabbitMQClientTestCase(TestCase):

    def setUp(self):
        self.host = 'test_host'
        self.queue = 'test_queue'
        self.exchange = 'test_exchange'

    def test_init_method(self):
        client = RabbitMQClient(
            host=self.host,
            exchange=self.exchange,
            queue=self.queue
        )
        self.assertTrue(isinstance(client.connection_params, ConnectionParameters))
        self.assertTrue()
