from math import ceil
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized

from taxi.models import Driver, Car, Manufacturer
from taxi.views import ManufacturerListView, CarListView, DriverListView


class PublicTestView(TestCase):
    def test_login_required(self):
        response = self.client.get(reverse("taxi:car-list"))
        self.assertNotEqual(response.status_code, 200)


class PrivateTestView(TestCase):
    def setUp(self) -> None:
        self.user_test = Driver.objects.create(
            username="test_username", password="test_password"
        )
        self.client.force_login(self.user_test)

    def test_login_required(self):
        response = self.client.get(reverse("taxi:car-list"))
        self.assertEqual(response.status_code, 200)

    def test_num_visits(self):
        num_visits = 14
        for _ in range(num_visits):
            self.client.get("")
        response = self.client.get("")
        self.assertEqual(response.context["num_visits"], num_visits + 1)


class TestCarView(TestCase):

    def setUp(self) -> None:
        self.user_test = Driver.objects.create(
            username="test_username", password="test_password"
        )
        self.client.force_login(self.user_test)
        self.num_of_car = 22
        manufacturer = Manufacturer.objects.create(
            name="test_name", country="test_country"
        )
        for i in range(self.num_of_car):
            Car.objects.create(model=f"test_model {i}", manufacturer=manufacturer, picture_url="Test")
        self.car_view = CarListView()

    def test_car_pagination(self):
        number_of_content = self.num_of_car % self.car_view.paginate_by
        if number_of_content == 0:
            number_of_content = self.car_view.paginate_by
        last_page = ceil(self.num_of_car / self.car_view.paginate_by)
        response = self.client.get(reverse("taxi:car-list") + f"?page={last_page}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(response.context["is_paginated"], True)
        self.assertEqual(len(response.context["car_list"]), number_of_content)

    def test_car_detail_view_assign_delete(self):
        self.client.get(reverse("taxi:toggle-car-assign", kwargs={"pk": 1}))
        self.assertTrue(self.user_test in Driver.objects.filter(cars__id=1))
        self.client.get(reverse("taxi:toggle-car-assign", kwargs={"pk": 1}))
        self.assertFalse(self.user_test in Driver.objects.filter(cars__id=1))

    @parameterized.expand(
        [
            (
                    "search_test_model",
                    "test_model",
            ),
            (
                    "search_test_model 0",
                    "test_model 0",
            ),
            (
                    "search_test_model 1",
                    "test_model 1",
            ),
            (
                    "search_test_model 6",
                    "test_model 6",
            ),
        ]
    )
    def test_car_search(self, name: str, search_str: str):
        response = self.client.get(reverse("taxi:car-list") + f"?search_edit={search_str}")
        number_on_page = min(
            Car.objects.filter(model__icontains=search_str).count(),
            self.car_view.paginate_by
        )
        self.assertEqual(len(response.context["car_list"]), number_on_page)


class TestManufacturerListView(TestCase):
    def setUp(self) -> None:
        self.num_of_manufacturers = 23
        for i in range(self.num_of_manufacturers):
            Manufacturer.objects.create(name=f"test_name{i}", country=f"test_country{i}", picture_url="Test")
        self.manufacturer_view = ManufacturerListView()
        self.user_test = Driver.objects.create(
            username="test_username", password="test_password"
        )
        self.client.force_login(self.user_test)

    def test_manufacturer_pagination(self):
        number_of_content = self.num_of_manufacturers % self.manufacturer_view.paginate_by
        if number_of_content == 0:
            number_of_content = self.manufacturer_view.paginate_by
        last_page = ceil(self.num_of_manufacturers / self.manufacturer_view.paginate_by)
        response = self.client.get(reverse("taxi:manufacturer-list") + f"?page={last_page}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(response.context["is_paginated"], True)
        self.assertEqual(len(response.context["manufacturer_list"]), number_of_content)

    @parameterized.expand(
        [
            (
                    "search_test_name",
                    "test_name",
            ),
            (
                    "search_test_name0",
                    "test_name0",
            ),
            (
                    "search_test_name1",
                    "test_name1",
            ),
            (
                    "search_test_name5",
                    "test_name5",
            ),
        ]
    )
    def test_manufacturer_search(self, name: str, search_str: str):
        response = self.client.get(reverse("taxi:manufacturer-list") + f"?search_edit={search_str}")
        number_on_page = min(
            Manufacturer.objects.filter(name__icontains=search_str).count(),
            self.manufacturer_view.paginate_by
        )
        self.assertEqual(len(response.context["manufacturer_list"]), number_on_page)


class TestDriverListView(TestCase):
    def setUp(self) -> None:
        self.num_of_drivers = 26
        for i in range(self.num_of_drivers):
            Driver.objects.create(
                username=f"test_name{i}",
                password=f"test_password{i}",
                license_number="TST" + f"{12345 + i}",
                picture_url="Test"
            )
        self.user_test = Driver.objects.create(
            username="test_username", password="test_password", picture_url="Test"
        )
        self.driver_view = DriverListView()
        self.client.force_login(self.user_test)

    def test_driver_pagination(self):
        number_of_content = (self.num_of_drivers + 1) % self.driver_view.paginate_by
        if number_of_content == 0:
            number_of_content = self.driver_view.paginate_by
        last_page = ceil((self.num_of_drivers + 1) / self.driver_view.paginate_by)
        response = self.client.get(reverse("taxi:driver-list") + f"?page={last_page}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertEqual(response.context["is_paginated"], True)
        self.assertEqual(len(response.context["driver_list"]), number_of_content)

    @parameterized.expand(
        [
            (
                    "search_6",
                    "6",
            ),
            (
                    "search_46",
                    "46",
            ),
            (
                    "search_56",
                    "56",
            ),
            (
                    "search_123",
                    "123",
            ),
        ]
    )
    def test_driver_search(self, name: str, search_str: str):
        response = self.client.get(reverse("taxi:driver-list") + f"?search_edit={search_str}")
        number_of_content = min(
            Driver.objects.filter(username__icontains=search_str).count(),
            self.driver_view.paginate_by
        )
        self.assertEqual(len(response.context["driver_list"]), number_of_content)
