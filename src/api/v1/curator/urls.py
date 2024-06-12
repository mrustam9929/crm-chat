from django.urls import path

from api.v1.curator import views

urlpatterns = [
    path('chats/<int:chat_id>/messages/<int:message_id>/read/', views.ChatMessageReadAPIView.as_view()),
    path('chats/assign/', views.ChatAssignCuratorAPIView.as_view()),
    path('chats/<int:pk>/comments/', views.ChatCommentListAPIView.as_view()),
    path('chats/<int:pk>/close/', views.ChatCloseAPIView.as_view()),
    path('chats/<int:pk>/messages/', views.ChatMessageListAPIView.as_view()),

    path('chats/<int:pk>/', views.ChatUpdateAPIView.as_view()),
    path('chats/topics/', views.ChatTopicListAPIView.as_view()),
    path('chats/messages/<int:pk>/', views.ChatMessageUpdateDeleteAPIView.as_view()),
    path('chats/messages/', views.ChatMessageCreateAPIView.as_view()),
    path('chats/comments/<int:pk>/', views.ChatCommentUpdateDeleteAPIView.as_view()),

    path('chats/comments/', views.ChatCommentCreateAPIView.as_view()),
    path('chats/info/', views.ChatInfoAPIView.as_view()),
    path('chats/', views.ChatCreateListAPIView.as_view()),
]
