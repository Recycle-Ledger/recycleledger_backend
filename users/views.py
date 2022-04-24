from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status #응답코드용 
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request): #회원가입
    serializer=UserSerializer(data=request.data)
    if serializer.is_valid(): #UserSerializer에 validate
        token = serializer.save()
        return Response(token,status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny]) #로그인
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class=MyTokenObtainPairSerializer

'''
    회원가입시 POST
    {
        "wallet_addr":"전자지갑주소",
        "business_num":"사업자등록번호",
        "password":"패스워드"
    }
    return 
    {
        "refresh":"토큰",
        "access":"토큰"
    }
    
'''
'''
    로그인시 POST 
    {   
        "wallet_addr":"전자지갑주소",
        "password":"패스워드"
    }
    return
    {
        "refresh": "토큰",
        "access": "토큰",
        "wallet_addr": "지갑주소",
        "business_num": "사업자등록번호"
    }
'''
'''
    로그아웃시 POST
    {
        "refresh":"토큰"
    }
    return
    {} #200ok
    
    로그인 안한상황에 로그아웃하면
    {
        "detail": "블랙리스트에 추가된 토큰",
        "code": "token_not_valid"
    }   
'''