from rest_framework.response import Response
from rest_framework.views import APIView
from core.tasks import ai_consume_messages
from core.brocer_message_client import RabbitMQClient


class PublishMessageAPIView(APIView):
    def post(self, request):
        message = request.data.get("message")
        exchange = request.data.get("exchange")
        if not message:
            return Response({"error": "Message is required"}, status=400)

        rabbit_client = RabbitMQClient(exchange=exchange)
        try:
            rabbit_client.publish_message(message)
            return Response({"status": "Message published successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ConsumeMessageAPIView(APIView):
    def get(self, request):
        queue = request.data.get("queue")
        async_consume_messages.delay(queue)
        return Response({"status": "Consuming task started"})