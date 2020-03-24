from django.urls import path
from users.views import *

urlpatterns = [
	path('profiles/', Profiles.as_view(), name='profile-list'),
	path('profiles/<int:pk>/', Profile.as_view(), name='profile-detail'),
]

urlpatterns += [
	path('users/', Users.as_view(), name='user-list'),
	path('users/<int:pk>/', User.as_view(), name='user-detail'),
]

urlpatterns += [
	path('usertypes/', UserTypes.as_view(), name='usertype-list'),
	path('usertypes/<int:pk>/', UserType.as_view(), name='usertype-detail'),
]

urlpatterns += [
	path('groups/', Groups.as_view(), name='group-list'),
	path('groups/<int:pk>/', Group.as_view(), name='group-detail'),
]