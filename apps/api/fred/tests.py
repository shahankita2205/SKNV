from uuid import uuid4

from django.db import connections
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

# Create your tests here.
from core.models import User as CoreUser
from fred.models import Logs, Office, Officetype, Users
from fred.serializers import FredOfficeSerializer


def _ensure_fred_tables(models):
    connection = connections["fred"]
    existing = set(connection.introspection.table_names())
    with connection.schema_editor() as schema_editor:
        for model in models:
            table = model._meta.db_table
            if table in existing:
                continue
            schema_editor.create_model(model)
            existing.add(table)


class FredOfficeViewTest(APITestCase):
    databases = {"default", "fred", "mysknv"}

    @classmethod
    def setUpTestData(cls):
        _ensure_fred_tables([Users, Officetype, Office])
        cls.admin_core = CoreUser.objects.create_user(
            email="office-admin@example.com",
            password="password",
        )
        cls.admin_fred = Users.objects.create(
            email="office-admin@example.com",
            first_name="Office",
            last_name="Admin",
            role="admin",
            status="active",
            created=timezone.now(),
        )
        cls.officeType = Officetype.objects.create(type="test")
        now = timezone.now()
        cls.office = Office.objects.create(
            id=1,
            addressid=1,
            name="Test Office",
            created=now,
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
            modified=now,
            synced=now,
            dtcstates="",
            suppresspairings=True,
            officetypeid=cls.officeType,
            officeagreementtypeid=None,
            note="",
        )

    def setUp(self):
        self.client.force_authenticate(user=self.admin_core)

    def test_get_fred_offices(self):
        response = self.client.get("/api/fred/v1/offices/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Office.objects.count(), 1)

    def test_get_fred_office_listview(self):  # new
        response = self.client.get("/api/fred/v1/offices/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Office.objects.count(), 1)
        self.assertContains(response, self.office)

    def test_api_detailview(self):  # new
        response = self.client.get(
            f"/api/fred/v1/offices/{self.office.id}/",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Office.objects.count(), 1)
        self.assertContains(response, "Test Office")


class FredUserViewTest(APITestCase):
    databases = {"default", "fred", "mysknv"}

    @classmethod
    def setUpTestData(cls):
        _ensure_fred_tables([Officetype, Office, Users, Logs])
        cls.admin_core = CoreUser.objects.create_user(
            email="admin@example.com",
            password="password",
        )
        cls.admin_fred = Users.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            role="admin",
            status="active",
            created=timezone.now(),
        )

    def setUp(self):
        self.client.force_authenticate(user=self.admin_core)

    def _create_fred_user(self, **overrides):
        email = overrides.pop("email", f"user-{uuid4().hex[:8]}@example.com")
        data = {
            "email": email,
            "first_name": "Test",
            "last_name": "User",
            "role": "manager",
            "status": "active",
            "created": timezone.now(),
        }
        data.update(overrides)
        return Users.objects.create(**data)

    def test_users_list(self):
        user = self._create_fred_user()
        response = self.client.get("/api/fred/v1/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item["id"] == user.id for item in response.data))

    def test_users_detail(self):
        user = self._create_fred_user()
        response = self.client.get(f"/api/fred/v1/users/{user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], user.id)

    def test_users_add(self):
        payload = {
            "email": "newuser@example.com",
            "pass": "secret123",
            "first_name": "New",
            "last_name": "User",
            "role": "manager",
            "status": "active",
        }
        response = self.client.post("/api/fred/v1/users/add/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = Users.objects.get(id=response.data["id"])
        self.assertEqual(new_user.email, payload["email"])
        self.assertEqual(len(new_user.pass_field), 64)

    def test_users_update(self):
        user = self._create_fred_user(pass_field="oldhash")
        payload = {
            "status": "inactive",
            "pharmacylist": True,
            "cslist": True,
        }
        response = self.client.put(
            f"/api/fred/v1/users/{user.id}/",
            payload,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.status, "inactive")
        self.assertTrue(user.pharmacylist)
        self.assertTrue(user.cslist)
        self.assertNotEqual(user.pass_field, "oldhash")

    def test_users_delete(self):
        user = self._create_fred_user()
        response = self.client.delete(f"/api/fred/v1/users/{user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Users.objects.filter(id=user.id).exists())

    def test_users_logs(self):
        user = self._create_fred_user()
        Logs.objects.create(
            userid=str(user.id),
            recordid=str(user.id),
            recordtype="user",
            msg="by user",
            type="app",
            created=timezone.now(),
        )
        Logs.objects.create(
            userid="999",
            recordid=str(user.id),
            recordtype="user",
            msg="about user",
            type="app",
            created=timezone.now(),
        )
        response = self.client.get(f"/api/fred/v1/users/logs/{user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("byUser", response.data)
        self.assertIn("aboutUser", response.data)
        self.assertGreaterEqual(len(response.data["byUser"]), 1)
        self.assertGreaterEqual(len(response.data["aboutUser"]), 1)

    def test_users_customer_service_list(self):
        self._create_fred_user(
            role="customer-service", status="active"
        )
        self._create_fred_user(
            role="customer-service-manager", status="active"
        )
        response = self.client.get("/api/fred/v1/users/customer-service/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("customerService", response.data)
        self.assertIn("customerServiceManager", response.data)

    def test_users_sales_lists(self):
        active_sales = self._create_fred_user(role="sales", status="active")
        self._create_fred_user(role="sales", status="inactive")
        response = self.client.get("/api/fred/v1/users/sales/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item["id"] == active_sales.id for item in response.data))

        response = self.client.get("/api/fred/v1/users/salesActive/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item["id"] == active_sales.id for item in response.data))
        self.assertFalse(
            any(item["status"] == "inactive" for item in response.data)
        )

    def test_users_sales_manager_assign(self):
        sales_user = self._create_fred_user(role="sales", status="active")
        manager_user = self._create_fred_user(role="sales-manager", status="active")
        response = self.client.post(
            "/api/fred/v1/users/salesmanager/",
            {"sales": sales_user.id, "manager": manager_user.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["error"], False)
        sales_user.refresh_from_db()
        self.assertEqual(sales_user.managerid, manager_user.id)

    def test_users_pharmacist_list(self):
        self._create_fred_user(role="pharmacist", status="active")
        response = self.client.get("/api/fred/v1/users/pharmacist/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("pharmacist", response.data)
        self.assertIn("admin", response.data)

    def test_users_pharmacylist_and_cslist(self):
        pharmacy_user = self._create_fred_user(pharmacylist=True)
        cs_user = self._create_fred_user(cslist=True)

        response = self.client.get("/api/fred/v1/users/pharmacylist/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item["id"] == pharmacy_user.id for item in response.data))

        response = self.client.get("/api/fred/v1/users/cslist/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item["id"] == cs_user.id for item in response.data))

    def test_users_sales_performance(self):
        self._create_fred_user(role="sales", status="active")
        response = self.client.get("/api/fred/v1/users/salesPerformance/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
