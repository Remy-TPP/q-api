from django.urls import path
from .views import *

urlpatterns = [
	path('profiles/', ProfilesView.as_view(), name='profile-list'),
	path('profiles/<int:pk>/', ProfileView.as_view(), name='profile-detail'),
]

urlpatterns += [
	path('users/', UsersView.as_view(), name='user-list'),
	path('users/<int:pk>/', UserView.as_view(), name='user-detail'),
]

urlpatterns += [
	path('usertypes/', UserTypesView.as_view(), name='usertype-list'),
	path('usertypes/<int:pk>/', UserTypeView.as_view(), name='usertype-detail'),
]

urlpatterns += [
	path('groups/', GroupsView.as_view(), name='group-list'),
	path('groups/<int:pk>/', GroupView.as_view(), name='group-detail'),
]

