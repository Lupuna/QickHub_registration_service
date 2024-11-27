from functools import wraps
from loguru import logger
from requests.exceptions import Timeout, JSONDecodeError


def rabbitmq_message_exceptions(func):
    @wraps(func)
    def wrapper(channel, method, properties, body):
        try:
            func(channel, method, properties, body)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Timeout as e:
            logger.error(f"TimeoutError in base_callback: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        except (JSONDecodeError, ValueError) as e:
            logger.error(f"Error in base_callback: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Unexpected error in base_callback: {e}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    return wrapper
