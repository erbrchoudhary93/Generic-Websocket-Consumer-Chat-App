from django.urls import path
from .import consumers



websocket_urlpattern  =  [ 
        
                      
        path('ws/sc/<str:groupkaname>/',consumers.MyWebsocketConsumer.as_asgi()),                  
        path('ws/asc/<str:groupkaname>/',consumers.MyasyncWebsocketConsumer.as_asgi()),                  
                          
]