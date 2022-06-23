class QLDB:
    
    LEDGER_NAME = "recycleleger-test"
    
    # 트래킹 테이블
    TRACKING_TABLE_NAME = "Tracking"
    #칼럼
    QR_ID_INDEX_NAME = "QR_id" # QR코드 고유 id 
    STATUS_INDEX_NAME = "Status" # type,from,to
    CAN_KG_INDEX_NAME = "Can_kg" # 폐식용유 캔 kg
    STATUS_CHANGE_TIME_INDEX_NAME = "Status_change_time" #status type에 따라 변경되는 시간
    PO_ID_INDEX_NAME = "PO_id" #식당 해시

 
    # 식당 테이블
    PO_TABLE_NAME = "PO" 
    #칼럼    
    QR_ID_INDEX_NAME = "QR_id" # QR코드 고유 id 
    PO_ID_INDEX_NAME = "PO_id" #식당 해시
    PO_INFO_INDEX_NAME = "PO_info" # 식당 정보
    OPEN_STATUS_INDEX_NAME = "Open_status" # 영업 여부
    DISCHARGE_DATE_INDEX_NAME = "Discharge_date" # 배출 일시
    
    
    # JOURNAL_EXPORT_S3_BUCKET_NAME_PREFIX = "qldb-tutorial-journal-export"
    # USER_TABLES = "information_schema.user_tables"
    # S3_BUCKET_ARN_TEMPLATE = "arn:aws:s3:::"
    # LEDGER_NAME_WITH_TAGS = "tags"

    # RETRY_LIMIT = 4
