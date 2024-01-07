from telnetlib import STATUS
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# from django.views import View
from old_data_reqapi.services.old_data_service import OldDataService
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
import json
from rest_framework.viewsets import ModelViewSet
from json import JSONEncoder


#calls call_old_data method from service

class OperationalDataController(ModelViewSet):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def operational_data_details(self, request, *args, **kwargs):
        try:
            if request.method =='GET':
                service=OldDataService()
                data = request.GET
                card_data_api_response = service.call_operational_data(data)
                response=json.dumps(card_data_api_response)
                return HttpResponse(response)    
        except Exception as error:
            return HttpResponse({error}, status = 500)



 