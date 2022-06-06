from django.urls import path
from .views import *
app_name="qldb"

urlpatterns = [
    # 원장 생성 및 테이블 구성 # create
    path('ledger', create_ledger, name='create_ledger'),
    # path('create_driver', create_qldb_driver, name='create_driver'),
    path('table', create_table, name='create_table'),
    path('index', create_index, name='create_index'),
    
    
    # 정보 삽입
    path('first_info', insert_first_info, name='insert_first_info'),
    
    # 트래킹 정보 수정
    # path('first_info/<str:Tracking_id>', insert_first_info, name='insert_first_info'),
    
    
    path('check', check, name='check'),
    
]
