
---

# Django & Node.js Microservices Communication with RabbitMQ

This project demonstrates asynchronous communication between a Django application (producer) and a Node.js service (consumer) using RabbitMQ as the message broker. The Django app sends a message to RabbitMQ, and the Node.js service processes it, returning a response back to Django.

## Table of Contents

1. [Requirements](#requirements)
2. [Project Setup](#project-setup)
3. [Architecture Overview](#architecture-overview)
4. [Running the Services](#running-the-services)
5. [Testing the Communication](#testing-the-communication)
6. [Troubleshooting](#troubleshooting)
7. [Notes and Improvements](#notes-and-improvements)

---

## Requirements

- **Python 3.x**
- **Node.js** (14+ recommended)
- **RabbitMQ** (installed and running on `localhost`)
- **Django** (3.x or later)
- **Pika** (Python library for RabbitMQ)
- **amqplib** (Node.js library for RabbitMQ)

## Project Setup

### 1. Install RabbitMQ

Make sure RabbitMQ is installed and running on your local machine. You can install it using:

- **Ubuntu**:
  ```bash
  sudo apt-get update
  sudo apt-get install rabbitmq-server
  sudo systemctl start rabbitmq-server
  ```

- **MacOS** (using Homebrew):
  ```bash
  brew install rabbitmq
  brew services start rabbitmq
  ```

- **Windows**: Download and install RabbitMQ from [https://www.rabbitmq.com/download.html](https://www.rabbitmq.com/download.html).

To enable the RabbitMQ Management Dashboard (optional), run:
```bash
rabbitmq-plugins enable rabbitmq_management
```

Access the management UI at `http://localhost:15672` with default credentials `guest:guest`.

### 2. Set Up Django (Producer)

1. Create and navigate to your Django project:
   ```bash
   django-admin startproject myproject
   cd myproject
   python manage.py startapp myapp
   ```

2. Install the `pika` library:
   ```bash
   pip install pika
   ```

3. Implement the RabbitMQ client in Django (`myapp/rabbitmq.py`):
   - This file defines the RabbitMQ client used to send a message to the `request_queue` and receive a response on `response_queue`.
   - The code also handles timeouts to avoid indefinite waits for a response.

4. Configure the Django view to send messages via RabbitMQ:
   - Create a view in `myapp/views.py` that triggers the RabbitMQ client to send a message.
   - Map this view to a URL in `myproject/urls.py`.

5. Run the Django server:
   ```bash
   python manage.py runserver
   ```

### 3. Set Up Node.js (Consumer)

1. Create a new Node.js project and navigate to it:
   ```bash
   mkdir node_consumer
   cd node_consumer
   npm init -y
   ```

2. Install `amqplib` to interact with RabbitMQ:
   ```bash
   npm install amqplib
   ```

3. Implement the Node.js consumer (`consumer.js`):
   - This file consumes messages from the `request_queue`, processes them, and sends a response back to the `response_queue` specified by Django.
   - The response includes the same correlation ID to match the original request.

4. Run the Node.js consumer:
   ```bash
   node consumer.js
   ```

## Architecture Overview

1. **Django (Producer)**:
   - Sends a message with a unique correlation ID and `reply_to` queue (`response_queue`) to the `request_queue`.
   - Waits on the `response_queue` for a response from Node.js, matching the correlation ID.

2. **Node.js (Consumer)**:
   - Listens to the `request_queue`, processes incoming messages, and sends a response to the `reply_to` queue specified in the message.
   - Includes the original correlation ID to allow Django to match requests with responses.

3. **RabbitMQ**:
   - Acts as a message broker, managing the `request_queue` and `response_queue` to facilitate communication between Django and Node.js.

## Running the Services

1. Start RabbitMQ.
2. Run the Django server:
   ```bash
   python manage.py runserver
   ```
3. Run the Node.js consumer:
   ```bash
   node consumer.js
   ```

## Testing the Communication

1. Send a request from Django by accessing the endpoint mapped to the view that sends a message to RabbitMQ (e.g., `http://127.0.0.1:8000/trigger_event/`).
2. Check the Node.js console output to verify that it receives and processes the message.
3. Confirm that Django receives the response from Node.js and logs or returns it as expected.

## Troubleshooting

### 1. **No Response Received in Django**
   - Verify that the `reply_to` and `correlation_id` properties are correctly set in the Django message.
   - Ensure that Node.js sends the response to the correct `reply_to` queue and includes the correct `correlation_id`.
   - Check if the response queue exists and is accessible by both Django and Node.js.
   - Review RabbitMQ logs for potential errors at `/var/log/rabbitmq` (Linux).

### 2. **Timeout Reached While Waiting for Response**
   - Increase the timeout in `send_request_and_wait_for_response()` if needed.
   - Verify that Node.js is sending the response immediately after processing the message.

### 3. **Connection Issues**
   - Restart RabbitMQ, Django, and Node.js to clear any stale connections.
   - Confirm that RabbitMQ is accessible on `localhost` and the default port (`5672`).

## Notes and Improvements

- **Temporary Queues**: For production, consider creating unique temporary queues for each request and automatically deleting them once the response is received.
- **Error Handling**: Implement more robust error handling for production environments, including retries for failed connections and logging.
- **Scalability**: This setup is suitable for small-scale applications; larger applications might benefit from a more sophisticated microservices architecture or the addition of Celery with Django for task management.

---