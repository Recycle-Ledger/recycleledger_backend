from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status #응답코드용 

# Create your views here.

@api_view(['POST'])
def check(request):
    if request.method=='POST':
        print('hi')
        return Response()
    