from qldb.services.qldb_setting import *
import hashlib

# ---------- 해당 PO_id 존재여부 확인 함수, 있으면 True 없으면 False -------
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
    
# ----------- 결과값에 대한 documentId 리스트로 반환 --------
def get_document_ids_from_dml_results(result):
    ret_val = list(map(lambda x: x.get('documentId'), result))
    return ret_val

# ------------

def select_po_for_collector():
    
    query="SELECT * from Tracking where Status['Type']='등록';"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query))
    return cursor

def select_for_po(po_pk):
    potohash=hashlib.sha256(po_pk.encode()).hexdigest()
    query="SELECT data, metadata.txTime as discharge_time FROM _ql_committed_Tracking where data.PO_id=?;"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query,potohash))
    return cursor

#중상 좌상 수거 목록
def select_pickup_for_collector_com_pk(collector_com_pk):
    # print(Collector_Com_pk)
    collectortohash=hashlib.sha256(collector_com_pk.encode()).hexdigest()
    # print(type(Collectortohash))
    query="SELECT data, metadata.txTime as occurTime from history(Tracking) where data.Status['To'] = ?"
    cursor = qldb_driver.execute_lambda(lambda executor: executor.execute_statement(query,collectortohash))
    return cursor
