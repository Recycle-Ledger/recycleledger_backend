from xml.etree.ElementInclude import default_loader
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
# import uuid

# Create your models here.

# BaseUserManager : user 생성할때 사용하는 클래스
# AbstractBaseUser : 상속받아 생성하는 클래스 

class UserManager(BaseUserManager):
    def create_user(self,phone_num,username,password): # user 생성 함수 
        
        if not phone_num:
            raise ValueError(_('핸드폰 번호는 필수'))
        if not username:
            raise ValueError(_('사용자 이름은 필수'))
        if not password:
            raise ValueError(_('비밀번호는 필수'))
        
        user=self.model(
            phone_num=phone_num,
            username=username,
            # wallet_addr=wallet_addr #자동생성해야함 
        ) 
        user.set_password(password) # set_password 함수 : 회원가입시 받은 비밀번호 hash하여 저장 
        user.save(using=self._db) # settings에 db중 기본 db 사용한다는 의미
        return user
    
    def create_superuser(self,phone_num,username,password): # superuser 생성 함수 
        user = self.create_user(
            phone_num=phone_num,
            username=username,
            password=password
        )
        user.is_superuser=True
        user.is_admin=True
        user.is_staff=True
        user.save(using=self._db)
        return user
# is_active(일반사용자)랑 is_admin은 장고 유저 모델의 필수필드라 정의
# is_staff(사이트관리스탭->이 값이 true여야 관리자페이지 로그인 가능)
# is_superuser는 관리자 페이지의 내용을 제한없이 봄

#PermissionMixin: admin계정 로그인시 사용자 권한 요구하는데 그때 해결 
# AbstractBaseUser는 기존필드 만족안하고 완전히 새로운 모델 생성할때 
class User(AbstractBaseUser,PermissionsMixin):
    
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    
    phone_num= models.CharField(verbose_name=_("핸드폰 번호"),unique=True,max_length=15)
    username=models.CharField(verbose_name=_("사용자 이름"),max_length=20)
    wallet_addr=models.CharField(verbose_name=_("전자지갑주소"), max_length=50,unique=True,null=True,blank=True)# 전자지갑주소는 34자리로구성됨
    business_num=models.CharField(verbose_name=_("사업자등록번호"), max_length=20,unique=True,null=True,blank=True)# 사업자등록번호는 10자리로 구성됨
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser= models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(verbose_name=_("회원가입날짜"),auto_now_add=True)     
    
    objects = UserManager()
    
    USERNAME_FIELD="phone_num" #고유식별자
    REQUIRED_FIELD=["phone_num","username"] #필수적 요구 필드 


    # class Meta:
    #     verbose_name = _("user")
    #     verbose_name_plural = _("users")
    #     ordering = ("-date_joined",)

    # def __str__(self):
    #     return self.username

    # def get_full_name(self):
    #     return self.nickname

    # def get_short_name(self):
    #     return self.nickname

    def __str__(self):
        return self.phone_num   #pk로 두자- 뇌피셜
    
#verbose_name : 설정해두면 verbose_name 출력하면 설정값이 나옴
