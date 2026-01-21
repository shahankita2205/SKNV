from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from mysknv.models import (
    Office,
    Officeipaduser,
    Officepatient,
    Officepermission,
    Officephysician,
    Officephysicianexclusion,
)
from mysknv.serializers import (
    MySKNVOfficeSerializer,
    MySKNVOfficeIpaduserSerializer,
    MySKNVOfficePatientSerializer,
    MySKNVOfficePermissionSerializer,
    MySKNVOfficePhysicianSerializer,
    MySKNVOfficePhysicianExclusionSerializer,
    OfficeMergeRequestSerializer,
    OfficeMergeService,
)


# Office views
class OfficeView(generics.ListCreateAPIView):
    queryset = Office.objects.all().using("mysknv")
    serializer_class = MySKNVOfficeSerializer

    def get_queryset(self):
        return Office.objects.exclude(status="DELETED").using("mysknv")


class OfficeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Office.objects.all().using("mysknv")
    serializer_class = MySKNVOfficeSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = "DELETED"
        instance.save(using="mysknv")
        return Response(status=status.HTTP_204_NO_CONTENT)


# Officeipaduser views
class OfficeipaduserView(generics.ListCreateAPIView):
    queryset = Officeipaduser.objects.all().using("mysknv")
    serializer_class = MySKNVOfficeIpaduserSerializer


class OfficeipaduserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officeipaduser.objects.all().using("mysknv")
    serializer_class = MySKNVOfficeIpaduserSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        office_id = self.kwargs.get("officeId")
        user_id = self.kwargs.get("userId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, officeId=office_id, userId=user_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Officepatient views
class OfficepatientView(generics.ListCreateAPIView):
    queryset = Officepatient.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePatientSerializer


class OfficepatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officepatient.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePatientSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        office_id = self.kwargs.get("officeId")
        patient_id = self.kwargs.get("patientId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, officeId=office_id, patientId=patient_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Officepermission views
class OfficePermissionView(generics.ListCreateAPIView):
    queryset = Officepermission.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePermissionSerializer


class OfficePermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officepermission.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePermissionSerializer


# Officephysician views
class OfficephysicianView(generics.ListCreateAPIView):
    queryset = Officephysician.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePhysicianSerializer


class OfficephysicianDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officephysician.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePhysicianSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        office_id = self.kwargs.get("officeId")
        physician_id = self.kwargs.get("physicianId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, officeId=office_id, physicianId=physician_id)
        self.check_object_permissions(self.request, obj)
        return obj


# Officephysicianexclusion views
class OfficephysicianexclusionView(generics.ListCreateAPIView):
    queryset = Officephysicianexclusion.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePhysicianExclusionSerializer


class OfficephysicianexclusionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Officephysicianexclusion.objects.all().using("mysknv")
    serializer_class = MySKNVOfficePhysicianExclusionSerializer

    lookup_field = None
    lookup_url_kwarg = None

    def get_object(self):
        office_id = self.kwargs.get("officeId")
        physician_id = self.kwargs.get("physicianId")
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, officeId=office_id, physicianId=physician_id)
        self.check_object_permissions(self.request, obj)
        return obj


class OfficeMergeView(APIView):
    """
    Merge two office records.

    POST /office/merge/
    {
        "from_office_id": 123,
        "to_office_id": 456
    }

    This will:
    1. Move all related records from office 123 to office 456
    2. Skip any records that would create duplicates
    3. Soft-delete office 123 (status = "DELETED")
    4. Log the merge action to activityLog
    """

    def post(self, request):
        serializer = OfficeMergeRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        from_office_id = serializer.validated_data["from_office_id"]
        to_office_id = serializer.validated_data["to_office_id"]

        # Get user ID from request if authenticated
        user_id = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = request.user.id

        try:
            merge_service = OfficeMergeService(
                from_office_id=from_office_id,
                to_office_id=to_office_id,
                user_id=user_id,
            )
            result = merge_service.merge()

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Merge failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
