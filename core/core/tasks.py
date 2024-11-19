from celery import shared_task
from loguru import logger

from core.brocer_message_client import RabbitMQClient


@shared_task
def ai_consume_messages(callback_path=None, queue=None):
    client = RabbitMQClient(queue=queue)
    callback = RabbitMQClient.base_callback
    if callback_path:
        try:
            module_path, func_name = callback_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[func_name])
            callback = getattr(module, func_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Error importing callback: {e}")

    try:
        client.consume_message(callback)
    except Exception as e:
        logger.error(f"Error consuming message: {e}")