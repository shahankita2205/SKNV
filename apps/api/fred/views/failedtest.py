
# app/views/failedtext.py
from rest_framework.views import APIView
from rest_framework.response import Response
from fred.serializers.textsent import TextSentService

class FailedTextPCDeliversView(APIView):
    def get(self, request):
        service = TextSentService()
        data = service.get_not_delivered_pc_delivers()
        return Response(data)



class FailedTextNoPatientView(APIView):
    def get(self, request):
        service = TextSentService()
        data = service.get_not_delivered_no_patient()
        return Response(list(data))

