from django.urls import path
from .views import *

urlpatterns = [
    path('get_available_yachts', GetAvailableYachts.as_view()),
    path('add_balance', AddBalance.as_view()),
    path('get_user_info', GetUserInfo.as_view()),
    path('deny_request', DenyRequest.as_view()),
    path('allow_request', AllowRequest.as_view()),
    path('get_user_requests', GetUserRequest.as_view()),
    path('create_back_request', CreateBackRequest.as_view()),
    path('create_yacht_request', CreateYachtRequest.as_view()),
    path('login', Login.as_view()),
    path('signup', Signup.as_view()),
]