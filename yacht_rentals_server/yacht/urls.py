from django.urls import path
from .views import Login, GetTodo

urlpatterns = [
    path('test', GetTodo.as_view()),
    path('login', Login.as_view()),
]