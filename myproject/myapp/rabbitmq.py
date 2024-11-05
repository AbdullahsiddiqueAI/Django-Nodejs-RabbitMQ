# myapp/rabbitmq.py
import pika
import json
import uuid

class RabbitMQClient:
    def __init__(self):
        # Set up the connection and channel
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        
        # Declare the request queue
        self.channel.queue_declare(queue='request_queue', durable=True)
        
        # Declare a fixed response queue for testing
        self.response_queue = 'response_queue'
        self.channel.queue_declare(queue=self.response_queue, durable=True)
        
        self.response = None
        self.corr_id = None

        # Start consuming on the response queue with the on_response callback
        self.channel.basic_consume(
            queue=self.response_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

    def on_response(self, ch, method, props, body):
        # Match the correlation ID to identify the correct response
        print("props",props.correlation_id)
        if str(self.corr_id) == str(props.correlation_id):
            self.response = json.loads(body)

    def send_request_and_wait_for_response(self, message):
        # Reset the response and set a unique correlation ID
        self.response = None
        self.corr_id = str(uuid.uuid4())
        
        # Log the `reply_to` and `correlation_id` properties
        print(f"Sending message with reply_to={self.response_queue} and correlation_id={self.corr_id}")

        # Publish message to the request queue with reply_to and correlation_id
        self.channel.basic_publish(
            exchange='',
            routing_key='request_queue',
            properties=pika.BasicProperties(
                reply_to=self.response_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(message)
        )

        # Wait for the response by processing data events
        while self.response is None:
            self.connection.process_data_events()  # Blocking wait for a single response

        # Close the connection after receiving the response
        self.connection.close()
        return self.response

def send_message_to_queue(message):
    client = RabbitMQClient()
    response = client.send_request_and_wait_for_response(message)
    return response
