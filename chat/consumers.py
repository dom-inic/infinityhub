import json
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        #  accept the connection 
        self.accept()

    def disconnect(self, code):
        return super().disconnect(code)
    
    # receive message from websocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # send message to websockect 
        self.send(text_data=json.dumps({'message': message}))