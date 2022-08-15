from django.urls import path
from .import views
urlpatterns = [
    # path('',views.index,name='index'),
    path('<str:groupname>',views.index,name='group'),
    # path('group/<str:groupname>',views.index_group,name='group'),
]