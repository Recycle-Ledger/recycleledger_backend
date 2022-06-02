class QLDB:
    
    LEDGER_NAME = "recycleleger-qldb"
    
    # 트래킹 테이블
    TRACKING_TABLE_NAME = "Tracking"
    IMAGE_TABLE_NAME = "Image"
    PO_TABLE_NAME = "PO" #식당
    
    TRACKING_ID_INDEX_NAME = "Tracking_id" # 트래킹 트랜잭션 id 
    STATUS_INDEX_NAME = "Status" # type,from,to
    CAN_INFO_INDEX_NAME = "Can_info" # 폐식용유 캔 INFO
    IMAGE_ID_INDEX_NAME = "Image_id" # 이미지 해시값
    PO_ID_INDEX_NAME = "PO_id" # 배출 식당 id
    IMAGE_URL_INDEX_NAME = "Image_url" # 이미지 url

    OPEN_STATUS_INDEX_NAME = "Open_status" # 영업 여부
    PO_INFO_INDEX_NAME = "PO_info" # 식당 정보
    DISCHARGE_DATE_INDEX_NAME = "Discharge_date" # 배출 일

    # JOURNAL_EXPORT_S3_BUCKET_NAME_PREFIX = "qldb-tutorial-journal-export"
    # USER_TABLES = "information_schema.user_tables"
    # S3_BUCKET_ARN_TEMPLATE = "arn:aws:s3:::"
    # LEDGER_NAME_WITH_TAGS = "tags"

    # RETRY_LIMIT = 4
