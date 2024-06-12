from django.urls import path

from api.v1.lms_crm import views

urlpatterns = [

    path('stats/topics-closed-chat-percentage/', views.ClosedChatPercentageAPIView.as_view()),
    path('stats/topics-popularity/', views.TopicsPopularityAPIView.as_view()),
    path('stats/topics-avg-time/', views.TopicsAvgResolutionTimeAPIView.as_view()),

    path('stats/closed-chat-percentage/', views.ClosedChatPercentageForTopicAPIView.as_view()),
    path('stats/chat-avg-time/', views.ChatsAvgResolutionTimeAPIView.as_view()),
    path('stats/curator-chats-avg-time/', views.CuratorChatsAvgTimeAPIView.as_view()),
    path('stats/curator-chats-count/', views.CuratorChatsAPIView.as_view()),
    path('notifications/', views.UserNotificationAPIView.as_view()),

]
