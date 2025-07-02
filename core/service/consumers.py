from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ServiceRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.service_id = self.scope['url_route']['kwargs']['pk']
        self.group_name = f"service_{self.service_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            'message': f'Connected to service {self.service_id}',
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("Received message:", text_data)
        data = json.loads(text_data)

        if data.get('action') == 'mark_as_complete':
            service_id = data.get('service_id')

            # Notify all clients in the same group (including user)
            await self.channel_layer.group_send(
                f"service_{service_id}",
                {
                    'type': 'notify_user_to_confirm',
                    'service_id': service_id,
                }
            )

    # Handler for the group message
    async def notify_user_to_confirm(self, event):
        print("Sending notification to user:", event)
        await self.send(text_data=json.dumps({
            'message': 'Technician marked the service as complete. Do you confirm?',
            'type': 'notify_user_to_confirm',
            'service_id': event['service_id'],
        }))
