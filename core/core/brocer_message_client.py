from contextlib import contextmanager
from django.conf import settings
from pika import ConnectionParameters, BlockingConnection
from loguru import logger
from requests import request
import json


class RabbitMQClient:

    def __init__(self, host=None, exchange=None, queue=None):
        self.connection_params = ConnectionParameters(host=host or settings.RABBITMQ_HOST)
        self.queue = queue or settings.RABBITMQ_QUEUE
        self.exchange = exchange or settings.RABBITMQ_EXCHANGE
        self.connection = None
        self.channel = None

    @contextmanager
    def connect_and_channel(self):
        try:
            self.connection = BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            yield self.channel
        except Exception as e:
            logger.error(f"Error with RabbitMQ {e}")
        finally:
            if self.channel: self.channel.close()
            if self.connection: self.connection.close()

    def publish_message(self, message):
        with self.connect_and_channel() as ch:
            ch.basic_publish(
                exchange=self.exchange,
                routing_key=self.queue,
                body=message
            )

    def consume_message(self, callback):
        with self.connect_and_channel() as ch:
            ch.basic_consume(
                queue=self.queue,
                on_message_callback=callback
            )
            ch.start_consuming()

    @staticmethod
    def base_callback(channel, method, properties, body):
        try:
            message = body.decode('utf-8')
            data = json.loads(message)
            logger.info(f"Received message: {message}, \n {data}")
            endpoint = data.get("endpoint")
            payload = data.get("payload")
            method_type = data.get("method", "POST").upper()

            if not endpoint:
                logger.error("No endpoint provided in message")
                raise ValueError("Missing 'endpoint' in message")
            request(method_type, endpoint, json=payload, timeout=10)
        except Exception as e:
            logger.error(f"Error in base_callback: {e}")
        finally:
            channel.basic_ack(delivery_tag=method.delivery_tag, requeue=False)
