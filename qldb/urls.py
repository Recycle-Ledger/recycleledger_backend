from django.urls import path
from .views import *
app_name="qldb"

urlpatterns = [
    path('create_ledger', create_ledger, name='create_ledger'),
    # path('create_driver', create_qldb_driver, name='create_driver'),
    path('create_table', create_table, name='create_table'),
    path('create_index', create_index, name='create_index'),
    path('insert_first_info', insert_first_info, name='insert_first_info'),
    
]
