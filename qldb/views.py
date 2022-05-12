from rest_framework.decorators import api_view
from rest_framework import status #응답코드용 
from rest_framework.response import Response
from django.conf import settings
import boto3
# from boto3 import client
from logging import basicConfig, getLogger, INFO
from time import sleep
from qldb.ledger import *
from botocore.exceptions import ClientError
from pyqldb.driver.qldb_driver import QldbDriver

logger = getLogger(__name__)
basicConfig(level=INFO)

ledger_name=Constants.LEDGER_NAME

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
        create_qldb_table(qldb_driver, Constants.DRIVERS_LICENSE_TABLE_NAME)
        create_qldb_table(qldb_driver, Constants.PERSON_TABLE_NAME)
        create_qldb_table(qldb_driver, Constants.VEHICLE_TABLE_NAME)
        create_qldb_table(qldb_driver, Constants.VEHICLE_REGISTRATION_TABLE_NAME)
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
        create_table_index(qldb_driver, Constants.PERSON_TABLE_NAME, Constants.GOV_ID_INDEX_NAME)
        create_table_index(qldb_driver, Constants.VEHICLE_TABLE_NAME, Constants.VEHICLE_VIN_INDEX_NAME)
        create_table_index(qldb_driver, Constants.VEHICLE_REGISTRATION_TABLE_NAME, Constants.LICENSE_PLATE_NUMBER_INDEX_NAME)
        create_table_index(qldb_driver, Constants.VEHICLE_REGISTRATION_TABLE_NAME, Constants.VEHICLE_VIN_INDEX_NAME)
        create_table_index(qldb_driver, Constants.DRIVERS_LICENSE_TABLE_NAME, Constants.PERSON_ID_INDEX_NAME)
        create_table_index(qldb_driver, Constants.DRIVERS_LICENSE_TABLE_NAME, Constants.LICENSE_NUMBER_INDEX_NAME)
        logger.info('Indexes created successfully.')
    except Exception as e:
        logger.exception('Unable to create indexes.')
        raise e
    return Response(status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
def ck(request):
    
    for table in qldb_driver.list_tables():
        print(table)
    return Response(status=status.HTTP_201_CREATED)