from qldb.services.qldb_setting import *
from qldb.services.select_data import *
import hashlib
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404


# ----------------------
def update_po_document(driver,po_body): 
    try:
        query = "UPDATE PO SET QR_id=?, PO_info=?, Open_status = ?, Discharge_date=?  Where PO_id = ?"
        cursor = driver.execute_lambda(lambda executor: executor.execute_statement(query, 
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

# ----------------------
def collector_modify_status(body,nowuser_pk): #중상용 from to type 변경 함수
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
                                                        body['Tracking']['QR_id']))    
             
            
            elif body['Status']['Type']=="거부":
                query="UPDATE Tracking set Status['Type'] =? where QR_id=?"
                cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        body['Tracking']['QR_id']))   
        except Exception as e:
            logger.exception('Error updating Tracking.')
            raise e 
    except Exception as e:
        logger.exception('Error selecting Tracking.')
        raise e 
    
def com_modify_status(body,nowuser_pk): #좌상용 from to type 변경 함수    
    try:
        collectortohash=hashlib.sha256(body['Collector_phone_num'].encode()).hexdigest()
        comtohash=hashlib.sha256(nowuser_pk.encode()).hexdigest()
        query="SELECT Tracking_id,  Can_info['QTY'] as QTY, Can_info['KG'] as KG from Tracking where Status['To']=? and Status['Type']='수거' "
        cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                (query,
                                                collectortohash))
        User=get_user_model()
        com=get_object_or_404(User,phone_num=nowuser_pk)
        
        try:
            if body['Status']['Type']=="수거": # 중상 폰번호로 to가 중상인거 select해서 찾고 for 돌면서 update        
                for trackinginfo in cursor:
                    
                    query ="UPDATE Tracking set Status['Type'] =?, Status['From']=?, Status['To']=? where Tracking_id=?"
                    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        collectortohash,
                                                        comtohash,
                                                        trackinginfo['Tracking_id']))
                    com.profile.total_QTY = com.profile.total_QTY + trackinginfo['QTY']
                    com.profile.total_KG  = com.profile.total_KG + trackinginfo['KG']
                    com.save()

            elif body['Status']['Type']=="거부":
                for tracking_id in cursor:
                    
                    query="UPDATE Tracking set Status['Type'] =? where Tracking_id=?"
                    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                        (query,
                                                        body['Status']['Type'],
                                                        tracking_id['Tracking_id'])) 

        except Exception as e:
            logger.exception('Error updating Tracking.')
            raise e 
    except Exception as e:
        logger.exception('Error selecting Tracking.')
        raise e 

