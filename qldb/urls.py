from django.urls import path
from .views import *
app_name="qldb"

urlpatterns = [
    # 원장 생성 및 테이블 구성
    path('ledger', create_ledger, name='ledger'),
    # path('create_driver', create_qldb_driver, name='create_driver'),
    path('table', create_table, name='table'),
    path('index', create_index, name='index'),
    
    # ------------- 식당 --------------
    # 첫페이지(GET)
    path('po_first_page', po_first_page, name='po_first_page'), 
    # 폐식용유 등록 (POST) + 거부 수정(PUT)
    path('discharge_info', discharge_info, name='discharge_info'),
    
    # ------------- 중상 --------------
    # 첫페이지(GET)
    path('collector_first_page', collector_first_page, name='collector_first_page'), 
    # 수거 (PUT)
    path('collector_pickup', collector_pickup, name='collector_pickup'),
    # 수정 or 거부 (PUT)
    path('collector_update_or_reject_oil_info', collector_update_or_reject_oil_info, name='collector_update_or_reject_oil_info'),
    # 식당선택 후 해당 식당 폐식용유 수거 수정 거부 여부 선택 페이지 (GET)
    path('collector_watch_po_oil_status_page/<str:po_hash>', collector_watch_po_oil_status_page, name='collector_watch_po_oil_status_page'), 

    # ------------- 좌상 --------------
    # 수거 (PUT)
    path('com_pickup', com_pickup, name='com_pickup'),
    # 중상 수거 내역 확인 페이지(GET)
    path('com_watch_collector_pickup_lists/<str:collector_hash>', com_watch_collector_pickup_lists, name='com_watch_collector_pickup_lists'), 
    

    
    # ------------- 좌상 + 중상 --------------
    # 중상 좌상 수거 후 자신 수거 내역 페이지(GET)
    path('collector_com_pickup_page', collector_com_pickup_page, name='collector_com_pickup_page'), 
  
  
  
   
]
