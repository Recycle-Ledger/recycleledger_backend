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

    #QR정보 기입
    insert_documents(qldb_driver, QLDB.TRACKING_TABLE_NAME, body['Tracking'])
    
    po_pk=request.user.phone_num
    potohash=hashlib.sha256(po_pk.encode()).hexdigest()
    body["PO"]["PO_id"]=potohash
    
    if get_num_for_PO_id(body['PO']['PO_id']):
        update_po_document(qldb_driver,body['PO']) #이부분이 PO 테이블 업데이트(트랜잭션 추가)
    else:
        insert_documents(qldb_driver, QLDB.PO_TABLE_NAME, body['PO'])
    insert_documents(qldb_driver, QLDB.IMAGE_TABLE_NAME, body['Image'])
    
    return HttpResponseRedirect(reverse("qldb:po_first_page"))

# ---------------------- 중상 폐식용유 수거 -> 수거 후 collector_com_pickup_page로 redirect --------------------------

@api_view(['PUT']) 
def collector_pickup(request): # Status.Type, Status.From, Status.To 변경, 중상이 가져감
    # body에 tracking_id랑 state는 필수
    body=json.loads(request.body)
    # print(body)
    collector_modify_status(body,request.user.phone_num)
  
    return HttpResponseRedirect(reverse("qldb:collector_com_pickup_page"))

# ---------------------- 중상 폐식용유 거부 --------------------------

@api_view(['PUT'])
def collector_reject(request):
    body=json.loads(request.body) #tracking_id만 넘어오면될듯 거부해야하니까
    collector_modify_status(body,request.user.phone_num)
    cursor=select_po_for_collector() #거절하고 다른 등록중 식당 정보
    
    return Response(cursor,status=status.HTTP_201_CREATED)

# ---------------------- 좌상 폐식용유 수거 --------------------------

@api_view(['PUT']) #좌상이 중상꺼 다 모아서 처리
def com_pickup(request):
    body=json.loads(request.body) #중상 pk인 핸드폰 번호 넘어옴
    com_modify_status(body,request.user.phone_num)
    
    User=get_user_model()
    collector=get_object_or_404(User,phone_num=body['Collector_phone_num']) 
    collector.profile.total_QTY=0
    collector.profile.total_KG=0
    collector.save()
    
    return HttpResponseRedirect(reverse("qldb:collector_com_pickup_page"))

# ---------------------- 좌상 폐식용유 거부 --------------------------

@api_view(['PUT'])
def com_reject(request):
    body=json.loads(request.body)
    com_modify_status(body,request.user.phone_num)
    return Response(status=status.HTTP_201_CREATED)

# ---------------------- 폐식용유 정보 수정 --------------------------

@api_view(['PUT'])
def update_info(request):
    
    return Response(status=status.HTTP_201_CREATED)


# ---------------------- 식당 첫페이지 - 자신이 올린 폐식용유의 현재까지의 상태 --------------------------

@api_view(['GET']) 
def po_first_page(request): 
    cursor=select_for_po(request.user.phone_num)
    return Response(cursor,status=status.HTTP_200_OK)

# ---------------------- 중상 첫페이지 - "등록" 상태의 식당 리스트 중상 열람  --------------------------

@api_view(['GET'])   
def collector_first_page(request):
    cursor=select_po_for_collector()
 
    return Response(cursor,status=status.HTTP_200_OK)

# ---------------------- 중상 + 좌상 현재까지 자신들의 수거 목록 리스트 -> 수거 후에 이 페이지로 넘어감   --------------------------

@api_view(['GET']) 
def collector_com_pickup_page(request):
    cursor=select_pickup_for_collector_com_pk(request.user.phone_num)
    return Response(cursor,status=status.HTTP_200_OK)
    

# ---------------------- 좌상이 중상 수거 내역 확인 페이지 --------------------------
@api_view(['GET'])
def collector_com_QTY_KG_info(request,collector_pk):
    User=get_user_model()
    collector=get_object_or_404(User,phone_num=collector_pk)
    print(collector.profile.total_KG)
    print(collector.profile.total_QTY)
    return Response(status=status.HTTP_200_OK)


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

