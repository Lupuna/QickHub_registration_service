from django.conf import settings
from django.core.management.base import BaseCommand
from loguru import logger

from core.broker_message_client import RabbitMQClient


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        rabbit_client = RabbitMQClient(settings.RABBITMQ_HOST, settings.RABBITMQ_EXCHANGE, settings.RABBITMQ_QUEUE)
        try:
            rabbit_client.consume_message(rabbit_client.message_handler)
        except Exception as e:
            logger.error(f"Error while consuming messages: {e}")
