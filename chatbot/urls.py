from django.urls import path
from .views import ChatPageView, chatbot_api, HomePageView
urlpatterns = [
    path("", ChatPageView.as_view(), name="chat"),
    path("api/chatbot/", chatbot_api, name="chatbot_api"),
]
