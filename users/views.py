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
def user_signup(request):
    serializer=UserSerializer(data=request.data)
    if serializer.is_valid(): #UserSerializer에 validate
        token = serializer.save()
        return Response(token,status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class=MyTokenObtainPairSerializer