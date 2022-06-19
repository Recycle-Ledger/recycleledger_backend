from urllib import request
from django.shortcuts import redirect
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from django.contrib.auth import authenticate
import jwt
from django.conf import settings


User=get_user_model() #커스텀 유저 가져옴 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"
    
    # wallet_addr, business_num도 unique임 modelserializer는 validate 자동, Model따라해줌
    
    def create(self,validated_data): # view에서 serializer save함수 호출하면 create 또는 perform_create(생성) 가 호출됨 
        user = User.objects.create(
            phone_num=validated_data["phone_num"],
            username=validated_data["username"],
            address=validated_data["address"],
            business_num=validated_data["business_num"],
            account=validated_data["account"],
            po_name=validated_data["po_name"],
            job=validated_data["job"]
        )

        # 사업자 등록번호 뒤에 이니셜 및 숫자 추가 부분
         
        if user.job=="중상":
            alpha = "C"
        elif user.job=="식당":
            alpha = "P"
        else:
            alpha = "J"

        a = len(User.objects.all())

        if a<10:
            alpha = alpha + str(a).zfill(3)
        elif a<100:
            alpha = alpha + str(a).zfill(2)
        elif a<1000:
            alpha = alpha + str(a).zfill(1)
        else:
            alpha = alpha + str(a)

        user.business_num = user.business_num + alpha
        user.set_password(validated_data["password"]) #(SHA 256)를 통한 해시화
        user.save()
        refresh=RefreshToken.for_user(user)
        return {"refresh":str(refresh),"access":str(refresh.access_token)} #회원가입시 바로 access토큰 refresh 토큰 생성후 리턴
    
    def update(self,instance,validated_data):

        instance.phone_num=validated_data.get('phone_num',instance.phone_num)
        instance.username=validated_data.get('username',instance.username)
        instance.address=validated_data.get('address',instance.address)
        instance.business_num=validated_data.get('business_num',instance.business_num)
        instance.account=validated_data.get('account',instance.account)
        instance.po_name=validated_data.get('po_name',instance.po_name)
        instance.job=validated_data.get('job',instance.job)
        instance.set_password(validated_data.get('password',instance.password))
        instance.save()
        return instance
        # return 값을 create 처럼 json꼴로 만들어서 주고 views Response에 token 같이 return 해도됨
        # 업데이트하면 로그인이 풀리는지 확인해보기
    
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        # Add custom claims
        # token['username'] = user.username
        return token

    def validate(self,attrs):
        data = super().validate(attrs)
        refresh=self.get_token(self.user)
        data["refresh"]=str(refresh)
        data["access"]=str(refresh.access_token)        
        # data["wallet_addr"]=self.user.wallet_addr
        # data["business_num"]=self.user.business_num
        print(refresh)
        data['user'] = UserSerializer(self.user).data
        # print(jwt.decode(refresh.access_token,'secret',algorithms = 'HS256'))
        return data
    

    

class MyTokenVerifySerializer(TokenVerifySerializer):
    token = serializers.CharField()

    def validate(self, attrs):
        # UntypedToken(attrs['token'])
        data = jwt.decode(attrs['token'], settings.SECRET_KEY, algorithms=['HS256'])
        data = {'id': data['user_id']}

    
        return data