from qldb.services.qldb_setting import *
from qldb.services.select_data import *
import hashlib
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


# ---------------------- 이미 있는 식당이 새로운 폐식용유 낼때 -------------
def update_po_document(po_body): 
    try:
        query = "UPDATE PO SET QR_id=?, PO_info=?, Open_status = ?, Discharge_date=?  Where PO_id = ?"
        cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query, 
                                                                                   po_body['QR_id'],
                                                                                   po_body['PO_info'],
                                                                                   po_body['Open_status'],
                                                                                   po_body['Discharge_date'],
                                                                                   po_body['PO_id']))
        logger.info('Documents updated successfully!')
        list_of_document_ids = get_document_ids_from_dml_results(cursor)
        return list_of_document_ids

    except Exception as e:
        logger.info('Error updating document!')
        raise e   
# ---------------------- 식당용 거부 상태 수정 수행 함수 ------------
def update_tracking_documnet(tracking_body):
    try:
        query = "UPDATE Tracking SET PO_id=?, Status_change_time=?, Can_kg = ?, Status=?  Where QR_id = ?"
        cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query, 
                                                                                   tracking_body['PO_id'],
                                                                                   tracking_body['Status_change_time'],
                                                                                   tracking_body['Can_kg'],
                                                                                   tracking_body['Status'],
                                                                                   tracking_body['QR_id']))
        logger.info('Documents updated successfully!')
        list_of_document_ids = get_document_ids_from_dml_results(cursor)
        return list_of_document_ids
    except Exception as e:
        logger.info('Error updating document!')
        raise e 
# ---------------------- 중상용 수거 수정 거부 수행 함수 ------------
def collector_modify_status(body,nowuser_pk): 
    try: 
        try:
            if body['Status']['Type']=="수거":
                collectortohash=hashlib.sha256(nowuser_pk.encode()).hexdigest()
                
                query="UPDATE Tracking set Status['Type'] =?, Status['To']=?, Status_change_time=? where QR_id=?"
                cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'], #수거
                                                        collectortohash,
                                                        body['Status_change_time'],
                                                        body['Tracking']['QR_id']))    
                User=get_user_model()
                collector=get_object_or_404(User,phone_num=nowuser_pk)
                collector.profile.total_KG  = collector.profile.total_KG + body['Tracking']['Can_kg']
                collector.save()
                
                
            elif body['Status']['Type']=="수정":
                query="UPDATE Tracking set Status['Type'] =?, Can_kg=?, Status_change_time=? where QR_id=?"
                cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'], #수정
                                                        body['Can_kg'],
                                                        body['Status_change_time'],
                                                        body['QR_id']))    
             
            
            elif body['Status']['Type']=="거부":
                query="UPDATE Tracking set Status['Type'] =? where QR_id=?"
                cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        body['QR_id']))   
        except Exception as e:
            logger.exception('Error updating Tracking.')
            raise e 
    except Exception as e:
        logger.exception('Error selecting Tracking.')
        raise e 

# ---------------------- 좌상용 수거 수행 함수 ------------
def com_modify_status(body,nowuser_pk):   
    try:
        
        try:
            if body['Status']['Type']=="수거":        
                
                comtohash=hashlib.sha256(nowuser_pk.encode()).hexdigest()

                query ="UPDATE Tracking set Status['Type'] =?, Status['From']=?, Status['To']=? where QR_id=?"
                cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        body['Tracking']['Status']['To'],
                                                        comtohash,
                                                        body['Tracking']['QR_id']))
                User=get_user_model()
                com=get_object_or_404(User,phone_num=nowuser_pk)
                com.profile.total_KG  = com.profile.total_KG + body['Tracking']['Can_kg']
                com.save()


        except Exception as e:
            logger.exception('Error updating Tracking.')
            raise e 
    except Exception as e:
        logger.exception('Error selecting Tracking.')
        raise e 

