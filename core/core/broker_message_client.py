from contextlib import contextmanager
from pika import ConnectionParameters, BlockingConnection, BasicProperties
from loguru import logger
from core.utils import rabbitmq_message_exceptions
from requests import request
from json import loads
from abc import abstractmethod


class BaseRabbitMQClient:

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
            self._close_resources()

    def publish_message(self, message, data_to_response: dict | None = None):
        properties = self._properties_generate(data_to_response)

        with self.connect_and_channel() as ch:
            ch.basic_publish(
                exchange=self.exchange,
                routing_key=self.queue,
                body=message,
                properties=properties
            )

    def _properties_generate(self, data_to_response: dict | None = None):
        if data_to_response:
            reply_to = data_to_response.pop('reply_to', None)
            headers = {**data_to_response, 'method_type': data_to_response.get('method_type', 'POST')}
            if reply_to:
                if 'exchange' not in headers or 'queue' not in headers:
                    raise ValueError("Missing 'exchange' or 'queue' in response data")
            properties = BasicProperties(reply_to=reply_to, headers=headers)
        else:
            properties = None
        return properties

    def _close_resources(self):
        if self.channel:
            try:
                self.channel.close()
                logger.info("Channel closed successfully.")
            except Exception as e:
                logger.warning(f"Failed to close channel: {e}")
        if self.connection:
            try:
                self.connection.close()
                logger.info("Connection closed successfully.")
            except Exception as e:
                logger.warning(f"Failed to close connection: {e}")

    def consume_message(self, callback):
        with self.connect_and_channel() as ch:
            ch.basic_consume(
                queue=self.queue,
                on_message_callback=callback
            )
            ch.start_consuming()

    @abstractmethod
    def message_handler(self, body, channel, method, properties):
        ...


class RabbitMQClient(BaseRabbitMQClient):

    @staticmethod
    @rabbitmq_message_exceptions
    def message_handler(body, channel, method, properties):
        endpoint, payload = RabbitMQClient.parse_message(body)
        response = request(properties.headers['method_type'], endpoint, json=payload, timeout=1)
        channel.basic_ack(delivery_tag=method.delivery_tag)

        exchange = properties.headers.get('exchange')
        queue = properties.headers.get('queue')
        if properties.reply_to and exchange and queue:
            response_message = {
                'status_code': response.status_code,
                'data': response.json() if response.content else None
            }

            channel.basic_publish(
                exchange=properties.headers.get('exchange'),
                routing_key=properties.headers.get('queue'),
                body=response_message
            )

    @staticmethod
    def parse_message(body):
        message = body.decode('utf-8')
        data = loads(message)
        endpoint = data.get("endpoint")
        payload = data.get("payload")
        if not endpoint:
            raise ValueError("Missing 'endpoint' in message")
        return endpoint, payload


class RabbitMQResponseClient(BaseRabbitMQClient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = None

    @contextmanager
    def connect_and_channel(self):
        try:
            self.connection = BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            result = self.channel.queue_declare(queue=self.queue, exclusive=True, auto_delete=True)
            self.queue = result.method.queue
            yield self.channel
        except Exception as e:
            logger.error(f"Error with RabbitMQ {e}")
        finally:
            self._close_resources()

    @rabbitmq_message_exceptions
    def message_handler(self, body, channel, method, properties):
        response = RabbitMQClient.parse_message(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        self.response = response

    @staticmethod
    def parse_message(body):
        message = body.decode('utf-8')
        data = loads(message)
        logger.info(f"Received message: {message}, \n data: {data}")
        response = data.get("response")
        return response
