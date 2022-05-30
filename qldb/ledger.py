class QLDB:
    
    LEDGER_NAME = "recycleleger-qldb"
    
    # 트래킹 테이블
    TRACKING_TABLE_NAME = "Tracking"
    # 칼럼명
    DRAINDATE_INDEX_NAME = "DrainDate" # 식당 배출날짜
    PO_NAME_INDEX_NAME = "POName" #식당 상호명
    # ADDRESS_INDEX_NAME = "Address" #식당 주소
    COLLECTOR_INDEX_NAME = "Collector" # 중상, 좌상 콜렉터
    QTY_INDEX_NAME = "QTY" # 식당, 중상 캔 개수
    KG_INDEX_NAME = "KG" # 식당 중상 캔 무게
    
    # 이미지 테이블
    IMAGE_TABLE_NAME = "Image"
    # 칼럼명
    IMAGE_HASH_INDEX_NAME = "ImageHash"
    
    
 

    # JOURNAL_EXPORT_S3_BUCKET_NAME_PREFIX = "qldb-tutorial-journal-export"
    # USER_TABLES = "information_schema.user_tables"
    # S3_BUCKET_ARN_TEMPLATE = "arn:aws:s3:::"
    # LEDGER_NAME_WITH_TAGS = "tags"

    # RETRY_LIMIT = 4
