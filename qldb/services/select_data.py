from qldb.services.qldb_setting import *
import hashlib

# ---------- 식당 시점 : 해당 PO_id 존재여부 확인 함수, 있으면 True 없으면 False -------
def get_num_for_PO_id(po_id): 
    try:
        query = "SELECT COUNT(*) as num_PO FROM PO WHERE PO_id = ?"
        # group by가 없음 
        cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query, po_id))
        if next(cursor)['num_PO']>0:
            logger.info('PO value exist')
            return True
        else:
            logger.info('No PO value')  
            return False 
             
    except Exception as e:
        logger.exception('Error getting "count" for PO_id.')
        raise e
    
# ----------- 식당 시점 : 결과값에 대한 documentId 리스트로 반환 -------- 안중요함 이부분은 
def get_document_ids_from_dml_results(result):
    ret_val = list(map(lambda x: x.get('documentId'), result))
    return ret_val

# ----------- 식당 시점 : 식당 첫페이지, 해당 식당이 내어둔 폐식용유의 최종 상태 확인 ----------
def select_for_po(po_pk):
    potohash=hashlib.sha256(po_pk.encode()).hexdigest()
    query="SELECT t as tracking_info, p.data.Discharge_date from Tracking as t join history(PO) as p on t.QR_id = p.data.QR_id where t.PO_id=?"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query,potohash))
    return cursor



# ----------- 중상시점: 첫페이지, 등록, 수정 상태의 오일을 가지고 있는 식당 리스트 반환 -----
def select_po_for_collector():
    
    query="SELECT * from PO"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query))
    return cursor

# ------------ 중상시점 : 선택된 식당의 등록, 수정 상태의 폐식용유 상태 리스트 반환 -------
def select_po_oil_status_for_collector(potohash):
    
    query="SELECT * from Tracking where Status['Type'] in ('등록','수정') where PO_id=?"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query,potohash))
    return cursor



# ------- 중상 좌상 시점 : 지금 까지 수거 목록 페이지 -----------
def select_pickup_for_collector_com_pk(collector_com_pk):
   
    collectortohash=hashlib.sha256(collector_com_pk.encode()).hexdigest()
    query="SELECT  t.data as Tracking, p.data as PO from history(Tracking) as t join history(PO) as p on t.data.QR_id = p.data.QR_id where t.data.Status['To']=?"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query,collectortohash))
    return cursor

# ------- 좌상 시점 : 수거해올 중상이 지금 까지 수한 수거 목록 리스트 페이지 --------
def select_collector_pickup_lists(collectortohash):
    pickquery="SELECT QR_id, Can_kg, Status['To'], Status['Type'], Status['From'], Status_change_time, PO_id from Tracking where Status['To']=? and Status['Type']='수거' "
    trackings = qldb_driver.execute_lambda(lambda executor: executor.execute_statement
                                                (pickquery,
                                                collectortohash))
    return trackings