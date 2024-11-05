// consumer.js
const amqp = require('amqplib/callback_api');

function consumeMessage(queueName) {
    amqp.connect('amqp://localhost', (error, connection) => {
        if (error) {
            console.error("Connection error:", error);
            return;
        }

        connection.createChannel((error, channel) => {
            if (error) {
                console.error("Channel error:", error);
                return;
            }

            // Ensure the queue exists
            channel.assertQueue(queueName, { durable: true });

            console.log(`[*] Waiting for messages in ${queueName}. To exit press CTRL+C`);
            channel.consume(queueName, (msg) => {
                const message = JSON.parse(msg.content.toString());
                console.log(" [x] Received:", message);

                // Process the message and create a response
                const response = handleMessage(message);
                console.log(" [x] Received:", Object.keys(msg.properties),msg.properties.replyTo,msg.properties.correlationId)

                // Check for the reply_to and correlation_id properties
                if (msg.properties.replyTo) {
                    console.log(" [x] Replying to queue:",msg.properties.replyTo);
                    console.log(" [x] Using correlation ID:", msg.properties.correlationId);
                    try {
                        // Attempt to send the response back to the specified reply_to queue
                        channel.sendToQueue(
                            msg.properties.replyTo,
                            Buffer.from(JSON.stringify(response)),
                            { correlationId:msg.properties.correlationId }
                        );
                        console.log(" [x] Response sent:", response);
                    } catch (error) {
                        console.error("Failed to send response:", error);
                    }
                } else {
                        console.error("No reply_to property in message; cannot send response.");
                }

                // Acknowledge the message after attempting to send the response
                channel.ack(msg);
            });
        });
    });
}

function handleMessage(message) {
    // Custom logic to handle the message
    console.log("Processing message:", message);
    // Simulate a response for demonstration
    return { status: "success", processed_data: message.data };
}

// Start consuming messages from 'request_queue'
consumeMessage("request_queue");
