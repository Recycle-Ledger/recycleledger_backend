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
    path('discharge', insert_first_info, name='insert_first_info'),
    path('pickup', pickup, name='pickup'),
    path('reject', reject, name='reject'),
    
    # 트래킹 정보 수정
    # path('first_info/<str:Tracking_id>', insert_first_info, name='insert_first_info'),
    path('PO_first_page', PO_first_page, name='PO_first_page'),
    path('Collector_first_page', Collector_first_page, name='Collector_first_page'), #중상첫페이지 
    path('Collector_Com_pickup_page', Collector_Com_pickup_page, name='Collector_Com_pickup_page'), #픽업페이지
    
    
    # path('check', check, name='check'),
    # path('check2', check2, name='check2'),
    
]
