from email import message
from django.shortcuts import redirect, render
from users.views import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import authenticate,login


# Create your views here.
def main(request):
    # current_user=UserSerializer(User,data=request.data)
    # current_user = request.user
    # print(current_user)
    if request.method=='POST':
        phone_num = request.POST['phone_num']
        if phone_num=="01088888888":
            return render(request,"posts/main_j.html")
        elif phone_num=="01022222222":
            return render(request,"posts/main_c.html")    
        else:
            return render(request,"posts/main.html")

def main_j(request):
    return render(request,"posts/main_j.html")

def main_c(request):
    return render(request,"posts/main_c.html")    

def login(request):
    # if request.user.is_authenticated:
    #     print(request.user)
    #     return render(request,"posts/main.html")

    # if request.method == "POST":
    #     phone_num = request.POST['phone_num']
    #     password = request.POST['password']

    #     user = authenticate(phone_num=phone_num, password=password)

    #     try:
            
    #     except:
    #         messages.error(request, '회원정보를 찾을 수 없습니다.')
        
    #     user = MyTokenObtainPairSerializer(TokenObtainPairSerializer)
        
    #     return render(request,"posts/main.html")
    
    return render(request,"posts/login.html")