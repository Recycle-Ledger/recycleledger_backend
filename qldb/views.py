from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework import status #응답코드용 
from rest_framework.response import Response
import json

#해시
import hashlib

#모델 호출
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model

#모듈 호출
from qldb.services.qldb_setting import *
from qldb.services.insert_data import *
from qldb.services.update_data import *
from qldb.services.select_data import *

# ---------------------- qldb 기본세팅 --------------------------
@api_view(['POST'])
def create_ledger(request):
    
    try:
        create_qldb_ledger(ledger_name)
        wait_for_active(ledger_name)
    except Exception as e:
        logger.exception('Unable to create the ledger!')
        raise e
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def create_table(request):
    try: 
        create_qldb_table(qldb_driver, QLDB.TRACKING_TABLE_NAME)
        create_qldb_table(qldb_driver, QLDB.PO_TABLE_NAME)
        logger.info('Tables created successfully.')
    except Exception as e:
        logger.exception('Errors creating tables.')
        raise e
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def create_index(request):
    logger.info('Creating indexes on all tables...')
    try:
        # 트래킹 테이블 구성
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.QR_ID_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.STATUS_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.CAN_KG_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.STATUS_CHANGE_TIME_INDEX_NAME)

        # 식당 테이블 구성 
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.QR_ID_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.PO_ID_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.PO_INFO_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.OPEN_STATUS_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.DISCHARGE_DATE_INDEX_NAME)

        logger.info('Indexes created successfully.')
    except Exception as e:
        logger.exception('Unable to create indexes.')
        raise e
    return Response(status=status.HTTP_201_CREATED)


# ---------------------- 식당 폐식용유 등록 -> 등록 후 po_first_page로 redirect --------------------------

@api_view(['POST']) #PO가 있는경우는 update -> 요청은 update인데 실제 역할은 같은 집에서 새로운 식용유 내놓아서 바뀐정보를 담는것
def discharge_info(request):
    body=json.loads(request.body)
    nowuser=request.user
    if nowuser.job=='식당':
        po_pk=nowuser.phone_num
    elif nowuser.job =='직원':
        po_pk=nowuser.User.phone_num
        
    #QR정보 기입
    insert_documents(qldb_driver, QLDB.TRACKING_TABLE_NAME, body['Tracking'])
    potohash=hashlib.sha256(po_pk.encode()).hexdigest()
    for po_body in body['PO']:
        po_body['PO_id']=potohash
        po_body['Status']['From']=potohash
        if get_num_for_PO_id(po_body['PO_id']):
            update_po_document(qldb_driver,po_body) 
        else:
            insert_documents(qldb_driver, QLDB.PO_TABLE_NAME, po_body)
    
    return HttpResponseRedirect(reverse("qldb:po_first_page"))

# ---------------------- 중상 폐식용유 수거 -> 수거 후 자신이 이때까지 수거 해온 폐식용유 데이터로 redirect --------------------------

@api_view(['PUT']) 
def collector_pickup(request): 
    
    body=json.loads(request.body)
    nowuser_pk=request.user.phone_num
    potohash=hashlib.sha256(body['PO_id'].encode()).hexdigest()
    pickquery="SELECT QR_id, Can_kg from Tracking where PO_id=? and Status['To']='' and Status['Type'] in ('등록','수정') "
    trackings = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(pickquery,potohash))
    for tracking in trackings:
        body['Tracking']=tracking #tracking안에는 QR_id랑 Can_kg가 들어있음
        collector_modify_status(body,nowuser_pk)
  
    return HttpResponseRedirect(reverse("qldb:collector_com_pickup_page"))

# ---------------------- 중상 폐식용유 정보 수정 or 거부 --------------------------

@api_view(['PUT'])
def collector_update_or_reject_oil_info(request):
    body=json.loads(request.body)
    nowuser_pk=request.user.phone_num
    
    for tracking in body['Tracking']:
        collector_modify_status(tracking,nowuser_pk)
    potohash=hashlib.sha256(body['PO_id'].encode()).hexdigest()
    
    return HttpResponseRedirect(reverse("qldb:collector_watch_po_oil_status_page",potohash))
   


# ---------------------- 좌상 폐식용유 수거 -> 수거 후 자신이 이때까지 수거 해온 폐식용유 데이터로 redirect --------------------------

@api_view(['PUT']) #좌상이 중상꺼 다 모아서 처리
def com_pickup(request):
    body=json.loads(request.body) 
    nowuser_pk=request.user.phone_num
    
    # collectortohash=hashlib.sha256(body['Collector_id'].encode()).hexdigest()
    # trackings=select_collector_pickup_lists(collectortohash)
    # 이부분은 com_watch_collector_pickup_lists 이부분에서 넘겨받음
    
    for tracking in body['Trackings']:
        body['Tracking']=tracking
        com_modify_status(body,nowuser_pk)
    
    User=get_user_model()
    collector=get_object_or_404(User,phone_num=body['Collector_id']) 
    collector.profile.total_QTY=0
    collector.profile.total_KG=0
    collector.save()
    
    return HttpResponseRedirect(reverse("qldb:collector_com_pickup_page"))




# ---------------------- 식당 첫페이지 - 자신이 올린 폐식용유의 현재까지의 상태 --------------------------

@api_view(['GET']) 
def po_first_page(request): 
    cursor=select_for_po(request.user.phone_num)
    return Response(cursor,status=status.HTTP_200_OK)

# ---------------------- 중상 첫페이지 - 등록 or 수정 상태의 오일을 가진 식당 정보 --------------------------
@api_view(['GET'])
def collector_first_page(request):
    cursor=select_po_for_collector()
    return Response(cursor,status=status.HTTP_200_OK)
    

# ---------------------- 중상이 식당 선택 후 페이지 - 해당식당에 대한 "등록" or "수정" 상태의 폐식용유 중상 열람  --------------------------

@api_view(['GET'])   
def collector_watch_po_oil_status_page(request,po_hash):
    # get url에서 param 암호화해야함
    cursor=select_po_oil_status_for_collector(po_hash)
    return Response(cursor,status=status.HTTP_200_OK)

# ---------------------- 중상 + 좌상 현재까지 자신들의 수거 목록 리스트 -> 수거 후에 이 페이지로 넘어감   --------------------------

@api_view(['GET']) 
def collector_com_pickup_page(request):
    cursor=select_pickup_for_collector_com_pk(request.user.phone_num)
    return Response(cursor,status=status.HTTP_200_OK)
    

# ---------------------- 좌상이 중상 수거 내역 확인 페이지 --------------------------
@api_view(['GET'])
def com_watch_collector_pickup_lists(request,collector_hash):
    
    trackings=select_collector_pickup_lists(collector_hash)
    
    return Response(trackings,status=status.HTTP_200_OK)


# 테이블 수 체크
# @api_view(['POST'])
# def create_qldb_driver(request):
#     try:
#         logger.info('Listing table names ')
#         for table in qldb_driver.list_tables():
#             logger.info(table)
#     except ClientError as ce:
#         logger.exception('Unable to list tables.')
#         raise ce
#     return Response(status=status.HTTP_201_CREATED)


# #redirect 연습
# @api_view(['GET'])
# def check(request):
#     print('first')
#     return HttpResponseRedirect(reverse("qldb:check2"))



# select t.QR_id, t.Status, t.Can_kg, t.Status_change_time, p.data.PO_id, p.data.PO_info, p.data.Open_status, p.data.Discharge_date  from Tracking as t join history(PO) as p on t.QR_id = p.data.QR_id;
# 최종상태의 qr에 대한 po 조인값

# select t.data.QR_id, t.data.Status, t.data.Can_kg, t.data.Status_change_time, p.data.PO_id, p.data.PO_info, p.data.Open_status, p.data.Discharge_date  from history(Tracking) as t join history(PO) as p on t.data.QR_id = p.data.QR_id;
# QR_id에 대한 Tracking history를 볼때 po 조인값