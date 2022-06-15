from django.urls import reverse

from django.http import HttpResponseRedirect
from rest_framework.decorators import api_view
from rest_framework import status #응답코드용 
from rest_framework.response import Response
from django.conf import settings
import json
import boto3
import hashlib
# from boto3 import client
from logging import basicConfig, getLogger, INFO
from time import sleep
from qldb.ledger import *
from botocore.exceptions import ClientError
from pyqldb.driver.qldb_driver import QldbDriver
import uuid

from amazon.ion.simple_types import IonPyBool, IonPyBytes, IonPyDecimal, IonPyDict, IonPyFloat, IonPyInt, IonPyList, \
    IonPyNull, IonPySymbol, IonPyText, IonPyTimestamp
from amazon.ion.simpleion import dumps, loads

from recycleledger_backend.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from django.contrib.auth import get_user_model

from users.serializers import UserSerializer


logger = getLogger(__name__)
basicConfig(level=INFO)
IonValue = (IonPyBool, IonPyBytes, IonPyDecimal, IonPyDict, IonPyFloat, IonPyInt, IonPyList, IonPyNull, IonPySymbol,
            IonPyText, IonPyTimestamp)

ledger_name=QLDB.LEDGER_NAME

access_key=getattr(settings,'AWS_ACCESS_KEY_ID')
secret_access_key=getattr(settings,'AWS_SECRET_ACCESS_KEY')
region_name=getattr(settings,'AWS_REGION')

session=boto3.session.Session(aws_access_key_id=access_key, 
                              aws_secret_access_key=secret_access_key, 
                              region_name=region_name)

qldb_client = session.client(
    'qldb'
    )

qldb_driver = QldbDriver(
    ledger_name=ledger_name, 
    boto3_session=session
    )

LEDGER_CREATION_POLL_PERIOD_SEC = 10
ACTIVE_STATE = "ACTIVE"


def create_qldb_ledger(name):

    logger.info("Let's create the ledger named: {}...".format(name))
    result = qldb_client.create_ledger(Name=name, PermissionsMode='ALLOW_ALL')
    logger.info('Success. Ledger state: {}.'.format(result.get('State')))
    return result


def wait_for_active(name):
 
    logger.info('Waiting for ledger to become active...')
    while True:
        result = qldb_client.describe_ledger(Name=name)
        if result.get('State') == ACTIVE_STATE:
            logger.info('Success. Ledger is active and ready to use.')
            return result
        logger.info('The ledger is still creating. Please wait...')
        sleep(LEDGER_CREATION_POLL_PERIOD_SEC)

@api_view(['POST'])
def create_ledger(request):
    
    try:
        create_qldb_ledger(ledger_name)
        wait_for_active(ledger_name)
    except Exception as e:
        logger.exception('Unable to create the ledger!')
        raise e
   
    return Response(status=status.HTTP_201_CREATED)


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

def create_qldb_table(driver, table_name):
    
    logger.info("Creating the '{}' table...".format(table_name))
    statement = 'CREATE TABLE {}'.format(table_name)
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement))
    logger.info('{} table created successfully.'.format(table_name))
    # print(len(list(cursor)))
    return len(list(cursor))

@api_view(['POST'])
def create_table(request):
    try: 
        create_qldb_table(qldb_driver, QLDB.TRACKING_TABLE_NAME)
        create_qldb_table(qldb_driver, QLDB.IMAGE_TABLE_NAME)
        create_qldb_table(qldb_driver, QLDB.PO_TABLE_NAME)

        logger.info('Tables created successfully.')
    except Exception as e:
        logger.exception('Errors creating tables.')
        raise e
    return Response(status=status.HTTP_201_CREATED)
    

def create_table_index(driver, table_name, index_attribute):
    
    logger.info("Creating index on '{}'...".format(index_attribute))
    statement = 'CREATE INDEX on {} ({})'.format(table_name, index_attribute)
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement))
    return len(list(cursor))    
    
@api_view(['POST'])
def create_index(request):
    logger.info('Creating indexes on all tables...')
    try:
        # 트래킹 테이블 구성
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.TRACKING_ID_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.STATUS_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.CAN_INFO_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.IMAGE_ID_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.PO_ID_INDEX_NAME)

        # 이미지 테이블 구성
        create_table_index(qldb_driver, QLDB.IMAGE_TABLE_NAME, QLDB.TRACKING_ID_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.IMAGE_TABLE_NAME, QLDB.IMAGE_URL_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.IMAGE_TABLE_NAME, QLDB.IMAGE_ID_INDEX_NAME)

        # 식당 테이블 구성 
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.PO_ID_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.PO_INFO_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.OPEN_STATUS_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.TRACKING_ID_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.PO_TABLE_NAME, QLDB.DISCHARGE_DATE_INDEX_NAME)

        logger.info('Indexes created successfully.')
    except Exception as e:
        logger.exception('Unable to create indexes.')
        raise e
    return Response(status=status.HTTP_201_CREATED)

def convert_object_to_ion(py_object):
    ion_object = loads(dumps(py_object))
    # print(ion_object)
    # print(type(ion_object))
    return ion_object

def get_document_ids_from_dml_results(result):
    ret_val = list(map(lambda x: x.get('documentId'), result))
    return ret_val

def insert_documents(driver, table_name, documents):
    try:
        logger.info('Inserting some documents in the {} table...'.format(table_name))
        statement = 'INSERT INTO {} ?'.format(table_name)
        # print(statement)
        cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement,
                                                                               convert_object_to_ion(documents)))
        logger.info('Documents inserted successfully!')
        list_of_document_ids = get_document_ids_from_dml_results(cursor)
        return list_of_document_ids
    except Exception as e:
        logger.info('Error inserting document!')
        raise e    

def get_num_for_PO_id(PO_id): # PO_id 존재여부 확인 함수 있으면 True 없으면 False
    try:
        query = "SELECT COUNT(*) as num_PO FROM PO WHERE PO_id = ?"
        # group by가 없음 
        cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query, PO_id))
        if next(cursor)['num_PO']>0:
            logger.info('PO value exist')
            return True
        else:
            logger.info('No PO value')  
            return False 
             
    except Exception as e:
        logger.exception('Error getting "count" for PO_id.')
        raise e

def update_po_document(driver,PO_body): #트래킹 아이디 변경, 배출일 수정, 식당 정보 수정 -> 같은 집이 새로운 식용유 내둬서 트래킹id 매칭이 바뀌는 행위 
    try:
        query = "UPDATE PO SET Tracking_id = ?, Discharge_date=?, PO_info=?  Where PO_id = ?"
        cursor = driver.execute_lambda(lambda executor: executor.execute_statement(query, PO_body['Tracking_id'],PO_body['Discharge_date'],PO_body['PO_info'],PO_body['PO_id']))
        logger.info('Documents updated successfully!')
        list_of_document_ids = get_document_ids_from_dml_results(cursor)
        return list_of_document_ids

    except Exception as e:
        logger.info('Error updating document!')
        raise e   

@api_view(['POST']) #PO가 있는경우는 update -> 요청은 update인데 실제 역할은 같은 집에서 새로운 식용유 내놓아서 바뀐정보를 담는것
def insert_first_info(request):
    body=json.loads(request.body)
    # print(body)
    PO_pk=request.user.phone_num
    POtohash=hashlib.sha256(PO_pk.encode()).hexdigest()
    body["Tracking"]["PO_id"]=POtohash
    body["Tracking"]["Status"]["From"]=POtohash
    body["PO"]["PO_id"]=POtohash
    # print(POtohash)
    # print(hashlib.sha256(me_PO.phone_num.encode()).hexdigest())
    insert_documents(qldb_driver, QLDB.TRACKING_TABLE_NAME, body['Tracking'])
    if get_num_for_PO_id(body['PO']['PO_id']):
        update_po_document(qldb_driver,body['PO']) #이부분이 PO 테이블 업데이트(트랜잭션 추가)
    else:
        insert_documents(qldb_driver, QLDB.PO_TABLE_NAME, body['PO'])
    insert_documents(qldb_driver, QLDB.IMAGE_TABLE_NAME, body['Image'])
    
    cursor=select_for_PO(PO_pk)
    return Response(cursor,status=status.HTTP_201_CREATED)

def modify_status(body,nowuser_pk): #from to type 변경 함수
    try:
        pickquery="SELECT Status['To'] as who From Tracking where Tracking_id=?"
        cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(pickquery,body['Tracking_id'] ))
        frombyto=next(cursor)
        usertohash=hashlib.sha256(nowuser_pk.encode()).hexdigest()
        print(frombyto["who"])
        try:
            if frombyto["who"] == "": # 식당 -> 중상, From 변경 X
                if body['Status']['Type']=="수거":
                    query="UPDATE Tracking set Status['Type'] =?, Status['To']=? where Tracking_id=?"
                    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        usertohash,
                                                        body['Tracking_id']))    
                elif body['Status']['Type']=="거부":
                    query="UPDATE Tracking set Status['Type'] =? where Tracking_id=?"
                    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        body['Tracking_id']))    
            else: # 중상 -> 좌상
                if body['Status']['Type']=="수거":
                    query="UPDATE Tracking set Status['Type'] =?, Status['From']=?, Status['To']=? where Tracking_id=?"
                    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        frombyto["who"],
                                                        usertohash,
                                                        body['Tracking_id']))
                elif body['Status']['Type']=="거부":
                    query="UPDATE Tracking set Status['Type'] =? where Tracking_id=?"
                    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        body['Tracking_id']))  
            
        except Exception as e:
            logger.exception('Error updating Tracking.')
            raise e 
    except Exception as e:
        logger.exception('Error selecting Tracking.')
        raise e 
    
# 수거, 중상 & 좌상
@api_view(['PUT']) 
def pickup(request): # Status.Type, Status.From, Status.To 변경, 중상이 가져감
    # body에 tracking_id랑 state는 필수
    body=json.loads(request.body)
    modify_status(body,request.user.phone_num)
    cursor=select_pickup_for_Collector_Com_pk(request.user.phone_num) #내가 수거한 목록
    return Response(cursor,status=status.HTTP_201_CREATED)
'''
    엑세스 토큰 헤더
    {
       "Status":{
            "Type" : "수거"
        },
        "Tracking_id": "12l3kj5h345lkjg654"
    }
'''

#수정
# @api_view(['GET']):
@api_view(['PUT'])
def update_info(request):
    return Response(status=status.HTTP_201_CREATED)

#거부, 중상 & 좌상
@api_view(['PUT'])
def reject(request):
    body=json.loads(request.body) #tracking_id만 넘어오면될듯 거부해야하니까
    modify_status(body,request.user.phone_num)
    cursor=select_PO_for_Collector() #거절하고 다른 등록중 식당 정보
    
    return Response(cursor,status=status.HTTP_201_CREATED)
'''
    엑세스 토큰 헤더
    {
       "Status":{
            "Type" : "거부"
        },
        "Tracking_id": "12l3kj5h345lkjg654"
    }
'''
def select_for_PO(PO_pk):
    POtohash=hashlib.sha256(PO_pk.encode()).hexdigest()
    query="SELECT data, metadata.txTime as discharge_time FROM _ql_committed_Tracking where data.PO_id=?;"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query,POtohash))
    return cursor

@api_view(['GET']) #식당이 자신이 올린 식용유 최종 상태 열람
def PO_first_page(request): 
    cursor=select_for_PO(request.user.phone_num)
    return Response(cursor)

def select_PO_for_Collector():
    
    query="SELECT * from Tracking where Status['Type']='등록';"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query))
    return cursor

@api_view(['GET'])    #중상이 "등록" 상태의 식당 열람
def Collector_first_page(request):
    cursor=select_PO_for_Collector()
    return Response(cursor)

def select_pickup_for_Collector_Com_pk(Collector_Com_pk):
    print(Collector_Com_pk)
    Collectortohash=hashlib.sha256(Collector_Com_pk.encode()).hexdigest()
    print(type(Collectortohash))
    query="SELECT data, metadata.txTime as occurTime from history(Tracking) where data.Status['To'] = ?"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query,Collectortohash))
    return cursor

@api_view(['GET']) #중상,좌상이 자신의 픽업 기록 열람 
def Collector_Com_pickup_page(request):
    
    cursor=select_pickup_for_Collector_Com_pk(request.user.phone_num)
    return Response(cursor)

# @api_view(['GET']) 

# #redirect 연습
# @api_view(['GET'])
# def check(request):
#     print('first')
#     return HttpResponseRedirect(reverse("qldb:check2"))

# @api_view(['GET'])
# def check2(request):
#     # User=get_user_model() #커스텀 유저 가져옴 
#     serializer=UserSerializer(request.user)
#     return Response(serializer.data)