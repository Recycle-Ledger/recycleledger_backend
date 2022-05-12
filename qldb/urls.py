from django.urls import path
from .views import *
app_name="qldb"

urlpatterns = [
    path('create_ledger', create_qldb_ledger, name='create_ledger'),
    path('create_driver', create_qldb_driver, name='create_driver'),
    path('create_table', create_qldb_table, name='create_table'),
    path('ck', ck, name='ck'),
]
