from django.urls import path
from .views import delete_todo, todo_list, update_todo, user_login, user_signup

urlpatterns = [
    path('', todo_list, name='todo_list'),
    path('update/<int:pk>/', update_todo, name='update_todo'),
    path('delete/<int:pk>/', delete_todo, name='delete_todo'),
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
]