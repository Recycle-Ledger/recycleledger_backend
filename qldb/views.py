from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status #응답코드용 
from rest_framework.response import Response
from django.conf import settings
import json
import boto3
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
    return ion_object

def get_document_ids_from_dml_results(result):
    ret_val = list(map(lambda x: x.get('documentId'), result))
    return ret_val

def insert_documents(driver, table_name, documents):
    logger.info('Inserting some documents in the {} table...'.format(table_name))
    statement = 'INSERT INTO {} ?'.format(table_name)
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement,
                                                                               convert_object_to_ion(documents)))
    list_of_document_ids = get_document_ids_from_dml_results(cursor)

    return list_of_document_ids

@api_view(['POST'])
def insert_first_info(request):
    body=json.loads(request.body)
    
    try:    
        insert_documents(qldb_driver, QLDB.TRACKING_TABLE_NAME, body['Tracking'])
        insert_documents(qldb_driver, QLDB.IMAGE_TABLE_NAME, body['Image'])
        insert_documents(qldb_driver, QLDB.PO_TABLE_NAME, body['PO'])

        logger.info('Documents inserted successfully!')
    except Exception as e:
        logger.exception('Error inserting or updating documents.')
        raise e
    return Response(status=status.HTTP_201_CREATED)

def find_person_from_document_id(transaction_executor, document_id):
    query = 'SELECT p.* FROM Person AS p BY pid WHERE pid = ?'
    cursor = transaction_executor.execute_statement(query, document_id)
    return next(cursor)

def find_primary_owner_for_vehicle(driver, POName):
    logger.info('Finding primary owner for vehicle with VIN: {}.'.format(POName))
    query = "SELECT Owners.PrimaryOwner.PersonId FROM VehicleRegistration AS v WHERE v.VIN = ?"
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(query, convert_object_to_ion(POName)))
    try:
        return driver.execute_lambda(lambda executor: find_person_from_document_id(executor,
                                                                                   next(cursor).get('POName')))
    except StopIteration:
        logger.error('No primary owner registered for this vehicle.')
        return None


def get_document_ids(transaction_executor, table_name, field, value):
    query = "SELECT id FROM {} AS t BY id WHERE t.{} = ?".format(table_name, field)
    cursor = transaction_executor.execute_statement(query, convert_object_to_ion(value))
    return list(map(lambda table: table.get('id'), cursor))

def print_result(cursor):
    result_counter = 0
    for row in cursor:
        # Each row would be in Ion format.
        logger.info(dumps(row, binary=False, indent='  ', omit_version_marker=True))
        result_counter += 1
    return result_counter

def update_vehicle_registration(driver, vin, document_id):
    logger.info('Updating the primary owner for vehicle with Vin: {}...'.format(vin))
    statement = "UPDATE VehicleRegistration AS r SET r.Owners.PrimaryOwner.PersonId = ? WHERE r.VIN = ?"
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement, document_id,
                                                                               convert_object_to_ion(vin)))
    try:
        print_result(cursor)
        logger.info('Successfully transferred vehicle with VIN: {} to new owner.'.format(vin))
    except StopIteration:
        raise RuntimeError('Unable to transfer vehicle, could not find registration.')

def validate_and_update_registration(driver, POName, current_owner, new_owner):
    primary_owner = find_primary_owner_for_vehicle(driver, POName)
    if primary_owner is None or primary_owner['POName'] != current_owner:
        raise RuntimeError('Incorrect primary owner identified for vehicle, unable to transfer.')

    document_ids = driver.execute_lambda(lambda executor: get_document_ids(executor, QLDB.TRACKING_TABLE_NAME,
                                                                           'POName', new_owner))
    update_vehicle_registration(driver, POName, document_ids[0])

@api_view(['POST'])
def update_ledger(request):

    #json 데이터가 여러개가 들어올 경우 코드를 수정해야함
    #일단 한가지 json데이터가 들어오는 경우만 생각해서 짰음
    #ex)update_body.VEHICLE[0]['VIN'] -> 여러개중에서 첫번째 중 'VIN'을 고르는것

    # 새로 업데이트 되는 데이터가 어떤것이 되어야하는가 
    update_body=json.loads(request.body)
    
    DrainDate = update_body.DrainDate['DrainDate']
    POName = update_body.POName['POName']
    Collector = update_body.Collector['Collector']
    QTY = update_body.QTY['QTY']
    KG = update_body.KG['KG']
    ValidFromDate = update_body.ValidFromDate['ValidFromDate']
    ValidToDate = update_body.ValidToDate['ValidToDate']

    try:
        
        validate_and_update_registration(qldb_driver, POName, previous_owner, new_owner)
    except Exception as e:
        logger.exception('Error updating VehicleRegistration.')
        raise e

# 아래와 같이 전달해주면됨
# {
#     "Tracking":{
#         "Can_info": {
#             "QTY" : 3,
#             "KG" : 5
#         },
#         "Image_id": "fha84hfl8oh2i4hfl1123",
#         "PO_id": "1il2u3h4li1hu23li4h",
#         "Status":{
#             "Type" : "등록",
#             "From" : "식당",
#             "To" : "중상"
#         },
#         "Tracking_id": "12l3kj5h345lkjg654"
#     },
#     "Image":{
#         "Image_id":"fha84hfl8oh2i4hfl1123",
#         "Image_url": "https://www.google.com",
#         "Tracking_id": "12l3kj5h345lkjg654"
#     },
#     "PO":{
#         "Discharge_date":"datetime(2022, 5, 26)",
#         "Open_status": "영업중",
#         "PO_id": "1il2u3h4li1hu23li4h",
#         "PO_info": {
#             "주소" : "서울특별시 서초구 효령로 266 태원빌딩 4층",
#             "상호명" : "버거킹 서초점"
#         },
#         "Tracking_id": "12l3kj5h345lkjg654"
#     }
# }


# Delete 구현하기
