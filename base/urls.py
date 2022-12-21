from django.urls import path
from . import views

urlpatterns = [
    path('signIn', views.signInView , name="signIn"),
    path('signUp', views.signUpView , name="signUp"),
    path('signOut', views.signOutView , name="signOut"),
    path('', views.home , name="home"),
    path('room/<int:pk>/', views.room, name="room"),
    path('createRoom/', views.createRoom, name="createRoom"),
    path('updateRoom/<int:pk>/', views.updateRoom, name="updateRoom"),
    path('deleteRoom/<int:pk>/', views.deleteRoom, name="deleteRoom"),
    path('updateMessage/<int:pk>/', views.updateMessage, name="updateMessage"),
    path('deleteMessage/<int:pk>/', views.deleteMessage, name="deleteMessage"),
    path('profile/<int:pk>/', views.userProfile, name="userProfile"),
    path('updateUser/', views.updateUser, name="updateUser"),
    path('topicsPage/', views.topicsPage, name="topics"),
    path('activityPage/', views.activityPage, name="activity"),
]
