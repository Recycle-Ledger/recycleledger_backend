from datetime import datetime, timedelta
from distutils.command.upload import upload
import secrets
from time import strftime
from xml.etree.ElementInclude import default_loader
from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
import jwt

from recycleledger_backend.settings import SECRET_KEY, SIMPLE_JWT
# import uuid

# Create your models here.

# BaseUserManager : user 생성할때 사용하는 클래스
# AbstractBaseUser : 상속받아 생성하는 클래스 

class UserManager(BaseUserManager):
    def create_user(self,phone_num,password,account,job): # user 생성 함수 
        
        if not phone_num:
            raise ValueError(_('핸드폰 번호는 필수'))
        # if not username:
        #     raise ValueError(_('사용자 이름은 필수'))
        if not password:
            raise ValueError(_('비밀번호는 필수'))
        if not account:
            raise ValueError(_('계좌번호는 필수'))
 
        user=self.model(
            phone_num=phone_num,
            # username=username,
            account=account,
            job=job
        ) 
        user.set_password(password) # set_password 함수 : 회원가입시 받은 비밀번호 hash하여 저장 
        user.save(using=self._db) # settings에 db중 기본 db 사용한다는 의미
        return user
    
    def create_superuser(self,phone_num,password): # superuser 생성 함수 
        user = self.create_user(
            phone_num=phone_num,
            account="0000",
            job="환경부",
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
    business_num=models.CharField(verbose_name=_("사업자등록번호"), max_length=20,unique=True,null=True,blank=True)# 사업자등록번호는 10자리로 구성됨
    phone_num= models.CharField(verbose_name=_("핸드폰 번호"),unique=True,max_length=15) # 전화번호(필수)
    username=models.CharField(verbose_name=_("사용자 이름"),max_length=20,null=True,blank=True) # 사용자 이름 (필수)
    address=models.CharField(verbose_name=_("주소"), max_length=100,null=True,blank=True) # 주소
    account=models.CharField(verbose_name=_("계좌번호"), max_length=100,unique=True) # 계좌번호(필수)
    po_name=models.CharField(verbose_name=_("상호명"), max_length=50,null=True,blank=True) # 상호명
    job=models.CharField(verbose_name=_("직업군"), max_length=50,null=True,blank=True) # 직업군 - 좌상,중상,식당 고르기
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser= models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(verbose_name=_("회원가입날짜"),auto_now_add=True)     
    
    objects = UserManager()
    
    USERNAME_FIELD="phone_num" #고유식별자
    REQUIRED_FIELD=["phone_num","username","account","job"] #필수적 요구 필드 

    def __str__(self):
        return self.phone_num

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id' : self.phone_num,
            'password' : int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')
        return token
#verbose_name : 설정해두면 verbose_name 출력하면 설정값이 나옴

#profile 부분
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    # total_QTY= models.IntegerField(default=0)
    total_KG= models.IntegerField(default=0)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()