from rest_framework.decorators import api_view
from rest_framework import status #응답코드용 
from rest_framework.response import Response
from django.conf import settings
import boto3
# from boto3 import client
from logging import basicConfig, getLogger, INFO
from time import sleep

from botocore.exceptions import ClientError
from pyqldb.driver.qldb_driver import QldbDriver


logger = getLogger(__name__)
basicConfig(level=INFO)

access_key=getattr(settings,'AWS_ACCESS_KEY_ID')
secret_access_key=getattr(settings,'AWS_SECRET_ACCESS_KEY')
region_name=getattr(settings,'AWS_REGION')
endpoint_url=getattr(settings,'AWS_ENDPOINT_URL')
session=boto3.session.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_access_key, region_name=region_name)

class Constants:
    """
    Constant values used throughout this tutorial.
    """
    LEDGER_NAME = "vehicle-registration"

    VEHICLE_REGISTRATION_TABLE_NAME = "VehicleRegistration"
    VEHICLE_TABLE_NAME = "Vehicle"
    PERSON_TABLE_NAME = "Person"
    DRIVERS_LICENSE_TABLE_NAME = "DriversLicense"

    LICENSE_NUMBER_INDEX_NAME = "LicenseNumber"
    GOV_ID_INDEX_NAME = "GovId"
    VEHICLE_VIN_INDEX_NAME = "VIN"
    LICENSE_PLATE_NUMBER_INDEX_NAME = "LicensePlateNumber"
    PERSON_ID_INDEX_NAME = "PersonId"

    # JOURNAL_EXPORT_S3_BUCKET_NAME_PREFIX = "qldb-tutorial-journal-export"
    # USER_TABLES = "information_schema.user_tables"
    # S3_BUCKET_ARN_TEMPLATE = "arn:aws:s3:::"
    # LEDGER_NAME_WITH_TAGS = "tags"

    # RETRY_LIMIT = 4
ledger_name=Constants.LEDGER_NAME

qldb_client = session.client(
    'qldb',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_access_key,
    region_name=region_name
    )

qldb_driver = QldbDriver(ledger_name=ledger_name, region_name=region_name, endpoint_url=endpoint_url, 
                        boto3_session=session)

LEDGER_CREATION_POLL_PERIOD_SEC = 10
ACTIVE_STATE = "ACTIVE"


def create_ledger(name):

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


def create_table(driver, table_name):
    
    logger.info("Creating the '{}' table...".format(table_name))
    statement = 'CREATE TABLE {}'.format(table_name)
    cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement))
    logger.info('{} table created successfully.'.format(table_name))
    print(len(list(cursor)))
    return len(list(cursor))

@api_view(['POST'])
def create_qldb_ledger(request):
    
    try:
        create_ledger(ledger_name)
        wait_for_active(ledger_name)
    except Exception as e:
        logger.exception('Unable to create the ledger!')
        raise e
   
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def create_qldb_driver(request):
    try:
        logger.info('Listing table names ')
        for table in qldb_driver.list_tables():
            logger.info(table)
    except ClientError as ce:
        logger.exception('Unable to list tables.')
        raise ce
    return Response(status=status.HTTP_201_CREATED)

@api_view(['POST'])
def create_qldb_table(request):
    try:
        
        create_table(qldb_driver, Constants.DRIVERS_LICENSE_TABLE_NAME)
        create_table(qldb_driver, Constants.PERSON_TABLE_NAME)
        create_table(qldb_driver, Constants.VEHICLE_TABLE_NAME)
        create_table(qldb_driver, Constants.VEHICLE_REGISTRATION_TABLE_NAME)
        logger.info('Tables created successfully.')
    except Exception as e:
        logger.exception('Errors creating tables.')
        raise e

    return Response(status=status.HTTP_201_CREATED)
    
@api_view(['POST'])
def ck(request):
    
    for table in qldb_driver.list_tables():
        print(table)
    return Response(status=status.HTTP_201_CREATED)