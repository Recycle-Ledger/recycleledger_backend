from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User=get_user_model() #커스텀 유저 가져옴 

class UserSerializer(serializers.Serializer):
    wallet_addr=serializers.CharField(required=True,max_length=50)
    business_num=serializers.CharField(required=True,max_length=20)
    password = serializers.CharField(required=True)
    
    def validate(self,data): #validate_필드명(self,value):로 하면 해당 필드만 검사, validate는 다수 필드 검사 
        if (
            data["wallet_addr"]
            and User.objects.filter(wallet_addr=data["wallet_addr"]).exists()
        ):
            
            raise serializers.ValidationError("이미 등록된 전자 지갑 주소입니다.")
        if (
            data["business_num"]
            and User.objects.filter(business_num=data["business_num"]).exists()
        ):
            raise serializers.ValidationError("이미 등록된 사업자등록번호입니다.")
        
        return data
    
    def create(self,validated_data): # view에서 serializer save함수 호출하면 create 또는 perform_create(생성) 가 호출됨 
        user = User.objects.create(
            wallet_addr=validated_data["wallet_addr"],
            business_num=validated_data["business_num"],
        )
        user.set_password(validated_data["password"])
        user.save()
        refresh=RefreshToken.for_user(user)
        return {"refresh":str(refresh),"access":str(refresh.access_token)} #회원가입시 바로 access토큰 refresh 토큰 생성후 리턴
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self,attrs):
        data = super().validate(attrs)
        refresh=self.get_token(self.user)
        data["refresh"]=str(refresh)
        data["access"]=str(refresh.access_token)
        
        data["wallet_addr"]=self.user.wallet_addr
        data["business_num"]=self.user.business_num
        return data