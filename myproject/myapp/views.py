# myapp/views.py
from django.http import JsonResponse
from .rabbitmq import send_message_to_queue

def trigger_event(request):
    message = {
        "task": "process_data",
        "data": {"id": 123, "type": "sample"}
    }
    response = send_message_to_queue(message)
    return JsonResponse({"status": "Processed by Node.js", "response": response})
