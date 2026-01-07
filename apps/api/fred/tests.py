from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Create your tests here.
from fred.models import Office, Officetype
from fred.serializers import FredOfficeSerializer


class FredOfficeViewTest(APITestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls):
        cls.officeType = Officetype.objects.create(type="test")
        cls.office = Office.objects.create(
            id=1,
            addressid=1,
            name="Test Office",
            created="2024-02-03 21:32:00",
            locationid=1,
            sales="[1]",
            altaddress="",
            users="",
            logo="",
            dhenabled=True,
            allowmsgconsult=True,
            allowvideoconsult=True,
            allowmsgfreeform=True,
            videoconsultfee=4900,
            msgconsultfee=4900,
            displayname="Test office",
            netsuiteid=1261,
            allowchatconsult=True,
            chatconsultfee=4900,
            email="rcook+test@sknv.com",
            acct="12345678",
            route="12345678",
            officeemail="rcook+test@sknv.com",
            primaryemail="rcook+test@sknv.com",
            delivermode="delivers",
            suppresssknvmessaging=True,
            suppressrefills=True,
            inofficedispense=True,
            allownewpatientreqconsult=True,
            officeslug="test-office",
            vendorid="1261",
            modified="2024-02-03 21:32:00",
            synced="2024-02-03 21:32:00",
            dtcstates="",
            suppresspairings=True,
            officetypeid=1,
            officeagreementtypeid="",
            note="",
        )

    def test_get_fred_offices(self):
        url = reverse("office-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Office.objects.count(), 1)

    def test_get_fred_office_listview(self):  # new
        response = self.client.get(reverse("office-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Office.objects.count(), 1)
        self.assertContains(response, self.office)

    def test_api_detailview(self):  # new
        response = self.client.get(
            reverse("FredOfficeDetailView", kwargs={"pk": self.office.id}),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Office.objects.count(), 1)
        self.assertContains(response, "Test Office")