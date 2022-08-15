from channels.generic.websocket import WebsocketConsumer,AsyncWebsocketConsumer
from time import sleep
import asyncio
import json
from asgiref.sync import async_to_sync
from . models import Group,Chat
from channels.db import database_sync_to_async



class MyWebsocketConsumer(WebsocketConsumer):
    def connect(self):
        print("Websocket Connected....")
        print('Channel layer .... ',self.channel_layer)
        print('Channel Name .... ',self.channel_name)
        self.group_name = self.scope['url_route']['kwargs']['groupkaname']
        print("Group Name ....",self.group_name)
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name    
        )        
        self.accept()  # to accept the connection
        # self.close() # to reject the connection
        
        
        
    def receive(self, text_data=None, bytes_data=None):
        # print('Message Received....',text_data)
        data =  json.loads(text_data)
        message = data['msg']
        # print(message)
        
        group = Group.objects.get(name = self.group_name)
        if self.scope['user'].is_authenticated:
            
            chats =Chat(
                content =data['msg'],
                group=group
            )
            chats.save()
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    'type':'chat.message',
                    'message':message
                    
                    }    
            )
            
        else:
            self.send(text_data=json.dumps({
                "msg":"Login requird"    
            }))
        
    def chat_message(self,event):
        # print("Event..",event)
        self.send(text_data=json.dumps({
            'msg':event['message']
        }))
    
            
        # self.send(text_data="message from server to clint")
            # to send data 
            # sleep(1)
        # self.close() # to forcefully close  the connection
    
    
    def disconnect(self, code):
        print("websocket Disconnected.....",code)
        print("Channel Layer ..",self.channel_layer)
        print("Channel Name ..",self.channel_name)
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name    
        )
        # return super().disconnect(code)
        
        
#########################################################888888888888888888888888888888*************************      
        
        
      # async  
class MyasyncWebsocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("Websocket Connected....")
        print('Channel layer .... ',self.channel_layer)
        print('Channel Name .... ',self.channel_name)
        self.group_name = self.scope['url_route']['kwargs']['groupkaname']
        print("Group Name ....",self.group_name)
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name    
        )        
        await self.accept()  # to accept the connection
        # await self.close() # to reject the connection
        
        
        
    async def receive(self, text_data, bytes_data=None):
        print('Message Received....',text_data)
        # return super().receive(text_data, bytes_data)
        # await self.send(text_data="message from server to clint")
        data =  json.loads(text_data)
        message = data['msg']
        # print(message)
        group = await database_sync_to_async(Group.objects.get)(name = self.group_name)
        if  self.scope['user'].is_authenticated:
            chats =Chat(
                content =data['msg'],
                group=group
            )
            await database_sync_to_async(chats.save)()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type':'chat.message',
                    'message':message
                    
                    }    
            )
        else:
            await self.send(text_data=json.dumps({
                "msg":"Login requird"    
            }))
            
    async def chat_message(self,event):
        # print("Event..",event)
        await self.send(text_data=json.dumps({
        'msg':event['message']
    }))
    
    
    async def disconnect(self, code):
        print("websocket Disconnected.....",code)
        print("Channel Layer ..",self.channel_layer)
        print("Channel Name ..",self.channel_name)
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name    
        )
        # return super().disconnect(code)