from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
    path('main',main,name="main"),
    path('login',login,name="login"),
    path('signup',signup,name="signup"),
    path('logout',logout,name="logout")
]