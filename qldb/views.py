# from django.shortcuts import render
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status #응답코드용 

# from pyqldb.config.retry_config import RetryConfig
# from pyqldb.driver.qldb_driver import QldbDriver


# from logging import basicConfig, getLogger, INFO
# from time import sleep

# from boto3 import client



# class Constants:
#     """
#     Constant values used throughout this tutorial.
#     """
#     LEDGER_NAME = "vehicle-registration"

#     VEHICLE_REGISTRATION_TABLE_NAME = "VehicleRegistration"
#     VEHICLE_TABLE_NAME = "Vehicle"
#     PERSON_TABLE_NAME = "Person"
#     DRIVERS_LICENSE_TABLE_NAME = "DriversLicense"

#     LICENSE_NUMBER_INDEX_NAME = "LicenseNumber"
#     GOV_ID_INDEX_NAME = "GovId"
#     VEHICLE_VIN_INDEX_NAME = "VIN"
#     LICENSE_PLATE_NUMBER_INDEX_NAME = "LicensePlateNumber"
#     PERSON_ID_INDEX_NAME = "PersonId"

#     # JOURNAL_EXPORT_S3_BUCKET_NAME_PREFIX = "qldb-tutorial-journal-export"
#     # USER_TABLES = "information_schema.user_tables"
#     # S3_BUCKET_ARN_TEMPLATE = "arn:aws:s3:::"
#     # LEDGER_NAME_WITH_TAGS = "tags"

#     # RETRY_LIMIT = 4

# def create_ledger(name,logger,qldb_client):
#     logger.info("Let's create the ledger named: {}...".format(name))
#     result = qldb_client.create_ledger(Name=name, PermissionsMode='ALLOW_ALL')
#     logger.info('Success. Ledger state: {}.'.format(result.get('State')))
#     return result


# def wait_for_active(name,logger,qldb_client,sec,active_state):
#     logger.info('Waiting for ledger to become active...')
#     while True:
#         result = qldb_client.describe_ledger(Name=name)
#         if result.get('State') == active_state:
#             logger.info('Success. Ledger is active and ready to use.')
#             return result
#         logger.info('The ledger is still creating. Please wait...')
#         sleep(sec)

# def main(ledger_name=Constants.LEDGER_NAME):
    
#     logger = getLogger(__name__)
#     basicConfig(level=INFO)
#     qldb_client = client('qldb',region_name='ap-northeast-2')

#     LEDGER_CREATION_POLL_PERIOD_SEC = 10
#     ACTIVE_STATE = "ACTIVE"
    
#     try:
#         create_ledger(ledger_name,logger,qldb_client)
#         wait_for_active(ledger_name,logger,qldb_client,LEDGER_CREATION_POLL_PERIOD_SEC,ACTIVE_STATE)
#     except Exception as e:
#         logger.exception('Unable to create the ledger!')
#         raise e
# @api_view(["GET"])
# def qldbck(request):
#     # main()
#     pass
