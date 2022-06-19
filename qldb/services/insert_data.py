from qldb.services.qldb_setting import *

def convert_object_to_ion(py_object):
    ion_object = loads(dumps(py_object))
    # print(ion_object)
    # print(type(ion_object))
    return ion_object

def get_document_ids_from_dml_results(result):
    ret_val = list(map(lambda x: x.get('documentId'), result))
    return ret_val

def insert_documents(driver, table_name, documents):
    try:
        logger.info('Inserting some documents in the {} table...'.format(table_name))
        statement = 'INSERT INTO {} ?'.format(table_name)
        # print(statement)
        cursor = driver.execute_lambda(lambda executor: executor.execute_statement(statement,
                                                                               convert_object_to_ion(documents)))
        logger.info('Documents inserted successfully!')
        list_of_document_ids = get_document_ids_from_dml_results(cursor)
        return list_of_document_ids
    except Exception as e:
        logger.info('Error inserting document!')
        raise e    
    
def get_num_for_PO_id(po_id): # PO_id 존재여부 확인 함수 있으면 True 없으면 False
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


def update_po_document(driver,po_body): #트래킹 아이디 변경, 배출일 수정, 식당 정보 수정 -> 같은 집이 새로운 식용유 내둬서 트래킹id 매칭이 바뀌는 행위 
    try:
        query = "UPDATE PO SET Tracking_id = ?, Discharge_date=?, PO_info=?  Where PO_id = ?"
        cursor = driver.execute_lambda(lambda executor: executor.execute_statement(query, 
                                                                                   po_body['Tracking_id'],
                                                                                   po_body['Discharge_date'],
                                                                                   po_body['PO_info'],
                                                                                   po_body['PO_id']))
        logger.info('Documents updated successfully!')
        list_of_document_ids = get_document_ids_from_dml_results(cursor)
        return list_of_document_ids

    except Exception as e:
        logger.info('Error updating document!')
        raise e   
