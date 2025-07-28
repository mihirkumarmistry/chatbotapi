import json
from .reply_engine import generate_reply
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()  # Accept the individual WebSocket connection

    async def disconnect(self, close_code):
        pass  # No group to leave

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get("message", "").strip()

        # Process message and get response and type
        response_data = generate_reply(user_message)

        # Send a standardized response
        await self.send(text_data=json.dumps(response_data))