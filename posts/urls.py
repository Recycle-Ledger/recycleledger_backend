from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
    # path('main',main,name="main"),
    path('main_j',main_j,name="main_j"),
    path('main_c',main_c,name="main_c"),
    path('login',login,name="login")
]