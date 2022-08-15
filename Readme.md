# **Generic Websocket Consumer Chat App**

## configuration in settings.py file

```python

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]

ASGI_APPLICATION = 'gneric_Consumer.asgi.application'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

```

## configuration in asgi.py file

```python
import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
import app.routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gneric_Consumer.settings')

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket':AuthMiddlewareStack(URLRouter(
        
        app.routing.websocket_urlpattern
        )
    )
    })
```
## configuration in urls.py file

```python
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('app.urls'))
]
```

## configuration in app/models.py file

```python

from django.db import models

# Create your models here.

class Chat(models.Model):
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(auto_now=True)
    group = models.ForeignKey('Group',on_delete=models.CASCADE)
    
class Group(models.Model):
    name=models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.name

```

## configuration in app/views.py file

```python

from django.shortcuts import render
from .models import Group,Chat
def index(request,groupname):
    print("Group Name : ",groupname)
    group= Group.objects.filter(name=groupname).first()
    chats=[]
    if group:
        chats = Chat.objects.filter(group=group)
        
    else:
        group = Group(name=groupname)
        group.save()
    return render(request,'app/index.html',{'group':groupname,'chats':chats})
   
   
```

## configuration in app/urls.py file
```python
from django.urls import path
from .import views
urlpatterns = [
    path('<str:groupname>',views.index,name='group'),
]

```

## configuration in app/consumer.py file

```python

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
        data =  json.loads(text_data)
        message = data['msg']
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
    
    def disconnect(self, code):
        print("websocket Disconnected.....",code)
        print("Channel Layer ..",self.channel_layer)
        print("Channel Name ..",self.channel_name)
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name    
        )  
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
        data =  json.loads(text_data)
        message = data['msg']
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
        
```

## configuration in app/routing.py file

```python
from django.urls import path
from .import consumers



websocket_urlpattern  =  [ 
        
                      
        path('ws/sc/<str:groupkaname>/',consumers.MyWebsocketConsumer.as_asgi()),                  
        path('ws/asc/<str:groupkaname>/',consumers.MyasyncWebsocketConsumer.as_asgi()),                  
                          
]
```

## configuration in app/index.html file

```html
<!DOCTYPE html>
<html lang="en">
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat app</title>
    </head>
    <body>
        
    
    <h1>Websocket Testing</h1>
    
    <h1>Group Name :{{group}}</h1>
    
    
    
    
    <textarea name="" id="chat-log" cols="100" rows="20">
        
        {% for chat in chats %}
    
        {{chat.content}}
            
        {% endfor %}
            
    </textarea><br>
    
    <h4>Type Your Message</h4>
 
    <input type="text" id="chat-message-input" size="100"><br>
    <input type="button" value="Send" id="chat-message-submit">
    
 
    
    {{group|json_script:"group-name"}}
    
    
    
    
        <script>
            const groupName = JSON.parse(document.getElementById('group-name').textContent)
            console.log(groupName)
             var ws = new WebSocket(
                   
                'ws://'
                +window.location.host 
                +'/ws/asc/'+ groupName 
                +'/'
    
             )    
            ws.onopen=function(){
                console.log('Websocket connection Open....')
            }
            ws.onmessage=function(event){
                const data = JSON.parse(event.data)
                document.querySelector('#chat-log').value+=(
                    // data.user+
                    // " : "+ 
                    data.msg+
                    "\n")
    
            };
            ws.onclose=function(){
                console.log('Websocket connection closed....');
            }
            document.getElementById('chat-message-submit').onclick =
                function(event){
                    const messageInputDom = document.getElementById('chat-message-input')
                    const message = messageInputDom.value
                    ws.send(JSON.stringify({
                        'msg':message
                    }))
                    messageInputDom.value = ''
                }
    
    
            
        </script>
    </body>
    </html>
    
    
    
```

## configuration in app/admin.py file

```python
from django.contrib import admin
from .models import Chat,Group

# Register your models here.
@admin.register(Chat)
class ChatmodalAdmin(admin.ModelAdmin):
    list_display =['id','content','timestamp','group']
@admin.register(Group)
class GroupmodalAdmin(admin.ModelAdmin):
    list_display = ['id','name']

```


