from email import message
from django.shortcuts import render
from users.views import *
from users.serializers import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from django.contrib import messages



User=get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny, ])
def main(request):
    if request.method=='POST':
        phone_num = request.POST['phone_num']
        password = request.POST['password']

        check = authenticate(phone_num=phone_num, password=password)
        if check==None:
            return render(request,"posts/signup.html") 

        else:
            a = {"phone_num":phone_num , "password":password}
            serializer_class=MyWebTokenObtainPairSerializer(TokenObtainPairSerializer).validate(a)

            job = serializer_class['user']['job']
            if job=="좌상":
                return render(request,"posts/main_c.html",{"user" : serializer_class['user']})
            elif job=="환경부":
                return render(request,"posts/main.html",{"user" : serializer_class['user']})
            else:
                return render(request,"posts/main_j.html",{"user" : serializer_class['user']})
 
def login(request):
    return render(request,"posts/login.html")    

def signup(request):
    if request.method=='POST':
        phone_num = request.POST['phone_num']
        password = request.POST['password']
        username = request.POST['username']
        account = request.POST['account']
        job = request.POST['job']
        po_name = request.POST['po_name']
        business_num = request.POST['business_num']
        address = None

        data = {
            "phone_num":phone_num, 
            "password":password, 
            "username":username, 
            "account":account,
            "job":job,
            "po_name":po_name,
            "business_num": business_num,
            "address": address,
        }

        userserializer=UserSerializer(data=data)
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

            return render(request,"posts/login.html")
        else:
            # 예외 처리 필요
            alert
            return Response(status=status.HTTP_400_BAD_REQUEST)


    return render(request,"posts/signup.html")    

# 예외처리 알림 메세지
def alert(request):
    message.warning(request,"이미 가입된 회원입니다.")