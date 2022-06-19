from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status #응답코드용 
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView
from .serializers import *
from django.contrib.auth import get_user_model
import json
from qldb.services.select_data import select_for_po, select_po_for_collector
from rest_framework import permissions
# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request): #회원가입
    userserializer=UserSerializer(data=request.data)
    if userserializer.is_valid(raise_exception=True): #UserSerializer validate
        token = userserializer.save()
        
        if request.data["job"]=="식당":
            cursor=select_for_po(request.data["phone_num"])
            cursor = { cs for cs in cursor}
            token['list']=cursor
        elif request.data['job']=="중상":
            cursor=select_po_for_collector()
            cursor = { cs for cs in cursor}
            token['list']=cursor
            
        return Response(token,status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny]) #로그인
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class=MyTokenObtainPairSerializer
    
    def main(self):
        user = self.request.user
        return render(request, "posts/main.html", {"user": user})   
    
    


@api_view(['PUT'])    
# @permission_classes([IsAuthenticated]) #회원으로 인증된 요청 한해서 view 호출
def user_info_update(request): #회원정보 수정
    serializer_class=MyTokenObtainPairSerializer
    body=json.loads(request.body)
    User=get_user_model()
    me=get_object_or_404(User,phone_num=body["phone_num"])

    # print(me)
    
    userserializer=UserSerializer(me,data=request.data)
    # print(userserializer.is_valid())
    if userserializer.is_valid():
        token=userserializer.save()
        # print(token)
        return Response(status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)

# request에 {"phone_num":"","update_data":{}}

class TokenVerify(TokenVerifyView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenVerifySerializer

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        account = self.get_object()
        serializer = UserSerializer(account)
        return Response(serializer.data)
