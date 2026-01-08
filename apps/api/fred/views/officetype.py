from rest_framework.views import APIView
from rest_framework.response import Response

from ..models.office import Officetype
from ..serializers.officetype import OfficeTypeSerializer


class OfficeTypeListView(APIView):
    def get(self, request):
        office_types = Officetype.objects.using("fred").order_by("-id")
        serializer = OfficeTypeSerializer(office_types, many=True)
        return Response(serializer.data)
