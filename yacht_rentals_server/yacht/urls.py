from django.urls import path
from .views import Login, GetAvailableYachts, AddBalance, GetUserInfo

urlpatterns = [
    path('get_available_yachts', GetAvailableYachts.as_view()),
    path('add_balance', AddBalance.as_view()),
    path('get_user_info', GetUserInfo.as_view()),
    path('login', Login.as_view()),
]