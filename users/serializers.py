from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

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
            wallet_addr=validated_data["wallet_addr"],
            business_num=validated_data["business_num"],
        )
        user.set_password(validated_data["password"]) #(SHA 256)를 통한 해시화
        user.save()
        refresh=RefreshToken.for_user(user)
        return {"refresh":str(refresh),"access":str(refresh.access_token)} #회원가입시 바로 access토큰 refresh 토큰 생성후 리턴
    
    def update(self,instance,validated_data):

        instance.phone_num=validated_data.get('phone_num',instance.phone_num)
        instance.username=validated_data.get('username',instance.username)
        instance.wallet_addr=validated_data.get('wallet_addr',instance.wallet_addr)
        instance.business_num=validated_data.get('business_num',instance.business_num)
        instance.set_password(validated_data.get('password',instance.password))
        instance.save()
        return instance
        # return 값을 create 처럼 json꼴로 만들어서 주고 views Response에 token 같이 return 해도됨
        # 업데이트하면 로그인이 풀리는지 확인해보기
    
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self,attrs):
        data = super().validate(attrs)
        refresh=self.get_token(self.user)
        data["refresh"]=str(refresh)
        data["access"]=str(refresh.access_token)
        # data["wallet_addr"]=self.user.wallet_addr
        # data["business_num"]=self.user.business_num
        return data