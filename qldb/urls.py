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
    #중상
    path('collector_pickup', collector_pickup, name='collector_pickup'),
    path('collector_reject', collector_reject, name='collector_reject'),
    #좌상
    path('com_pickup', com_pickup, name='com_pickup'),
    path('com_reject', com_reject, name='com_reject'),
    
    # 트래킹 정보 수정
    # path('first_info/<str:Tracking_id>', insert_first_info, name='insert_first_info'),
    path('po_first_page', po_first_page, name='po_first_page'),
    path('collector_first_page', collector_first_page, name='collector_first_page'), #중상첫페이지 
    
    
    path('collector_com_pickup_page', collector_com_pickup_page, name='collector_com_pickup_page'), #중상 좌상 수거목록 페이지

  
    path('update_info', update_info, name='update_info'), 
    
    
    # path('check', check, name='check'),
    # path('check2', check2, name='check2'),
    
]
