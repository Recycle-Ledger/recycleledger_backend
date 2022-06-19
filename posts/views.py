from email import message
from django.shortcuts import redirect, render
from users.views import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate,login
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json
from django.http import HttpResponse, JsonResponse
import requests

User=get_user_model()
# Create your views here.
# def main(request):
#     # current_user=UserSerializer(User,data=request.data)
#     # current_user = request.user
#     # print(current_user)
#     # if request.method=='POST':
#     #     phone_num = request.POST['phone_num']
#     #     print(phone_num)
#     #     if phone_num=="01088888888":
#     #         return render(request,"posts/main_c.html")
#     #     elif phone_num=="01022222222":
#     #         return render(request,"posts/main_j.html")    
#     #     else:
#     user = request.user
#     return render(request, "posts/main.html", {"user": user})

def main_j(request):
    return render(request,"posts/main_j.html")

def main_c(request):
    return render(request,"posts/main_c.html")

def login(request):
    if request.method=='POST':
        phone_num = request.POST['phone_num']
        password = request.POST['password']
        post_data = request.POST.copy()
        
        print(post_data)
        

        # url = "http://localhost:8000/users/login/"
        content = {
            "phone_num" : phone_num,
            "password" : password        
        }

        print(type(json.dumps(content)))
        # headers = {'content-type' : 'application/json'}

        # print(type(content))

        return JsonResponse(json.dumps(content), content_type="application/json")

        # serializer = MyTokenObtainPairSerializer(data=data)
        # print(serializer)

        # return render(request,"posts/main.html")

    return render(request,"posts/login.html")    

    