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

from amazon.ion.simple_types import IonPyBool, IonPyBytes, IonPyDecimal, IonPyDict, IonPyFloat, IonPyInt, IonPyList, \
    IonPyNull, IonPySymbol, IonPyText, IonPyTimestamp
from amazon.ion.simpleion import dumps, loads

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
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.DRAINDATE_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.PO_NAME_INDEX_NAME)
        # create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.ADDRESS_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.COLLECTOR_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.QTY_INDEX_NAME)
        create_table_index(qldb_driver, QLDB.TRACKING_TABLE_NAME, QLDB.KG_INDEX_NAME)
        # 이미지 테이블 구성 
        create_table_index(qldb_driver, QLDB.IMAGE_TABLE_NAME, QLDB.IMAGE_HASH_INDEX_NAME)
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
    # print(body['track'])
    # print(body['image'])
    try:    
        insert_documents(qldb_driver, QLDB.TRACKING_TABLE_NAME, body['track'])
        insert_documents(qldb_driver, QLDB.IMAGE_TABLE_NAME, body['image'])
        logger.info('Documents inserted successfully!')
    except Exception as e:
        logger.exception('Error inserting or updating documents.')
        raise e
    return Response(status=status.HTTP_201_CREATED)

# 아래와 같이 전달해주면됨
# {
#     "track":{
#         "DrainDate": "1234598760",
#         "POName": "맘스터치",
#         "Collector": "김명준",
#         "QTY": "2",
#         "KG": "1",
#         "ValidFromDate": "datetime(2022, 5, 26)",
#         "ValidToDate": "datetime(2023, 9, 25)"
#     },
#     "image":{
#         "ImageHash":"123442",
#         "ValidFromDate": "datetime(2022, 5, 26)",
#         "ValidToDate": "datetime(2023, 9, 25)"
#     }
# }