from django.urls import path
from users.views import *

urlpatterns = [
	path('users/', Users.as_view(), name='users'),
	path('users/<int:pk>/', User.as_view(), name='user'),
]