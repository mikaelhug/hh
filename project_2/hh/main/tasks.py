from celery import shared_task


@shared_task
def forward_to_message_queue(sensor_data: dict) -> None:
    # For now, just print — later this will send to RabbitMQ or Timescale
    print(f"Received sensor data: {sensor_data}")
