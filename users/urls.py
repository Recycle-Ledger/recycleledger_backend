from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from .views import *
app_name="users"

urlpatterns = [
    path('create',user_signup,name="signup"),
    path('login',MyTokenObtainPairView.as_view(),name="login"),
    path('logout',TokenBlacklistView.as_view(),name="logout"),
    # as_view는 클래스 진입 메소드 
]
