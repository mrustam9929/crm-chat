from django.urls import include, path, re_path

from api.v1.client import views

urlpatterns = [
    path('topics/', views.TopicListAPIView.as_view()),
    path('chats/<int:pk>/messages/', views.ChatMessageListAPIView.as_view()),
    path('chats/<int:chat_id>/messages/<int:message_id>/read/', views.ChatMessageReadAPIView.as_view()),
    path('chats/messages/', views.ChatMessageCreateAPIView.as_view()),
    path('chats/', views.ChatListCreateAPIView.as_view()),

]
