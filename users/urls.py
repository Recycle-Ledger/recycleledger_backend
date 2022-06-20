from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView,TokenRefreshView,TokenVerifyView
from .views import *

app_name="users"

urlpatterns = [
    path('create',user_signup,name="signup"),
    path('login',MyTokenObtainPairView.as_view(),name="login"),
    path('logout',TokenBlacklistView.as_view(),name="logout"),
    
    #access토큰 재발급, {"refresh": 토큰} 꼴로 post
    path('token-refresh', TokenRefreshView.as_view(), name='token_refresh'),
    #토큰 유효성 검사, {"token": 토큰} 꼴로 post, refresh access 둘다 검사가능
    path('token-verify', TokenVerifyView.as_view(), name='token_verify'),
    
    path('info-update',user_info_update,name="info_update"),
    # as_view는 클래스 진입 메소드 
]
