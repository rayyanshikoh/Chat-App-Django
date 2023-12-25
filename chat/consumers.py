import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['url_route']['kwargs']['username']
        self.room_group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
            # self.username 
        )
        self.accept()
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sent_by = text_data_json['username']
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sent_by': sent_by
            }
        )

    def chat_message(self, event):
        message = event['message']
        sent_by = event['sent_by']
        time = datetime.now().strftime("%H:%M")
        
        self.send(text_data=json.dumps({
            'message': message,
            'username': sent_by,
            'time': time
        }))

# A user types a message into the chat box and hits 'Enter' or clicks the 'Send' button. 
# This triggers a JavaScript function that sends the message and the username of the sender to the server over a WebSocket connection. 
# The message is sent as a JSON string.

# The server receives the message on the WebSocket and triggers the receive method in the consumer. 
# The text_data parameter of this method contains the JSON string that was sent by the client.

# Inside the receive method, the JSON string is parsed into a Python dictionary using json.loads(text_data). 
# The message and the username are extracted from this dictionary.

# The receive method then sends a message to the group associated with the chat room. This is done using async_to_sync(self.channel_layer.group_send). 
# The message sent to the group includes the type of the message ('chat_message'), the message itself, and the username of the sender.

# The group_send method triggers the chat_message method on all consumers that are in the group. 
# The event parameter of this method contains the message that was sent to the group.

# Inside the chat_message method, the message and the username are extracted from the event dictionary. The current time is also obtained and formatted as a string.

# The chat_message method then sends a message back to the client over the WebSocket. This is done using self.send. 
# The message sent back to the client includes the message, the username of the sender, and the time. This message is sent as a JSON string.

# The client receives the message on the WebSocket and updates the chat box to display the new message, the username of the sender, and the time the message was sent.