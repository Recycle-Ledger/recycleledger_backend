from qldb.services.qldb_setting import *
from qldb.services.select_data import *

def convert_object_to_ion(py_object):
    ion_object = loads(dumps(py_object))
    # print(ion_object)
    # print(type(ion_object))
    return ion_object


# ---------------------- 식당용 폐식용유 정보 삽입 함수 ------------

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
    