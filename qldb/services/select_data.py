from qldb.services.qldb_setting import *
import hashlib

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
