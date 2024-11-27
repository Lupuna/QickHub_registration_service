from contextlib import contextmanager
from pika import ConnectionParameters, BlockingConnection
from loguru import logger
from requests import request
from requests.exceptions import Timeout
from json import JSONDecodeError, loads


class RabbitMQClient:

    def __init__(self, host, exchange, queue):
        self.connection_params = ConnectionParameters(host=host)
        self.queue = queue
        self.exchange = exchange
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
            try:
                if self.channel: self.channel.close()
            except Exception as e:
                logger.warning(f"Failed to close channel: {e}")
            try:
                if self.connection: self.connection.close()
            except Exception as e:
                logger.warning(f"Failed to close connection: {e}")

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
            endpoint, method_type, payload = RabbitMQClient.parse_message(body)
            request(method_type, endpoint, json=payload, timeout=1)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Timeout as e:
            logger.error(f"TimeoutError in base_callback: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except (JSONDecodeError, ValueError) as e:
            logger.error(f"Error in base_callback: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    @staticmethod
    def parse_message(body):
        message = body.decode('utf-8')
        data = loads(message)
        logger.info(f"Received message: {message}, \n data: {data}")
        endpoint = data.get("endpoint")
        payload = data.get("payload")
        method_type = data.get("method", "POST").upper()
        if not endpoint:
            raise ValueError("Missing 'endpoint' in message")
        return endpoint, method_type, payload

