import json
import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import InventoryProducts, OtherPettyCosts, PettyCosts

MEDIA_ROOT = tempfile.mkdtemp()


def tearDownModule():
    shutil.rmtree(MEDIA_ROOT, ignore_errors=True)


def image_file(name="photo.png"):
    buffer = BytesIO()
    Image.new("RGB", (4, 4), "red").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def create_product(name="Lipstick", price="450.00"):
    return InventoryProducts.objects.create(
        product_name=name,
        description=f"{name} description",
        home_image=image_file(),
        buying_price=Decimal("300.00"),
        selling_price=Decimal(price),
        unit_amount=10,
        unit_type="pieces",
    )


def create_employee(id_number="12345678", **extra_fields):
    return get_user_model().objects.create_user(
        id_number,
        password="a-strong-pass-123",
        first_name="Mercy",
        middle_name="W",
        surname="Njeri",
        phone_number="0700000000",
        **extra_fields,
    )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CartTests(TestCase):
    def setUp(self):
        self.lipstick = create_product("Lipstick", "450.00")
        self.perfume = create_product("Perfume", "1200.00")

    def update(self, client, product, action):
        return client.post(
            reverse("update-cart"),
            json.dumps({"product_id": product.pk, "action": action}),
            content_type="application/json",
        )

    def test_adding_twice_increments_one_line(self):
        self.update(self.client, self.lipstick, "add")
        response = self.update(self.client, self.lipstick, "add")

        self.assertEqual(
            response.json(),
            {"quantity": 2, "line_total": "900.00", "cart_total": "900.00", "cart_count": 2},
        )

    def test_each_visitor_has_their_own_cart(self):
        other_visitor = Client()
        self.update(self.client, self.lipstick, "add")
        self.update(other_visitor, self.perfume, "add")

        mine = self.client.get(reverse("cart")).context["cart"]
        theirs = other_visitor.get(reverse("cart")).context["cart"]

        self.assertNotEqual(mine.pk, theirs.pk)
        self.assertEqual([line.product for line in mine.ordered_products.all()], [self.lipstick])
        self.assertEqual([line.product for line in theirs.ordered_products.all()], [self.perfume])

    def test_subtract_lowers_quantity_then_removes_the_line(self):
        self.update(self.client, self.lipstick, "add")
        self.update(self.client, self.lipstick, "add")

        self.assertEqual(self.update(self.client, self.lipstick, "subtract").json()["quantity"], 1)
        response = self.update(self.client, self.lipstick, "subtract")

        self.assertEqual(response.json()["quantity"], 0)
        self.assertEqual(response.json()["cart_count"], 0)

    def test_remove_drops_the_whole_line(self):
        self.update(self.client, self.lipstick, "add")
        self.update(self.client, self.lipstick, "add")
        self.update(self.client, self.perfume, "add")

        response = self.update(self.client, self.lipstick, "remove")

        self.assertEqual(response.json()["cart_total"], "1200.00")

    def test_cart_count_is_shown_in_the_header(self):
        self.update(self.client, self.lipstick, "add")

        response = self.client.get(reverse("home"))

        self.assertContains(response, '<span class="badge" data-cart-count>1</span>', html=True)

    def test_unknown_product_or_action_is_rejected(self):
        for payload in [{"product_id": 999, "action": "add"}, {"product_id": 1, "action": "x"}]:
            with self.subTest(payload=payload):
                response = self.client.post(
                    reverse("update-cart"), json.dumps(payload), content_type="application/json"
                )
                self.assertEqual(response.status_code, 400)

    def test_cart_updates_require_a_csrf_token(self):
        client = Client(enforce_csrf_checks=True)

        self.assertEqual(self.update(client, self.lipstick, "add").status_code, 403)


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CatalogueTests(TestCase):
    def test_search_matches_name_and_description(self):
        lipstick = create_product("Lipstick")
        create_product("Perfume")

        response = self.client.get(reverse("home"), {"q": "lipstick desc"})

        self.assertEqual(list(response.context["products"]), [lipstick])

    def test_product_detail_shows_the_product(self):
        product = create_product("Hair oil")

        self.assertContains(
            self.client.get(reverse("product-detail", args=[product.pk])), "Hair oil"
        )

    def test_employees_without_permission_cannot_add_products(self):
        self.client.force_login(create_employee())

        self.assertEqual(self.client.get(reverse("create-product")).status_code, 403)

    def test_admin_can_add_a_product_with_a_gallery(self):
        self.client.force_login(create_employee(is_staff=True, is_superuser=True))

        response = self.client.post(
            reverse("create-product"),
            {
                "product_name": "Face cream",
                "description": "Moisturising",
                "home_image": image_file("main.png"),
                "buying_price": "500",
                "selling_price": "800",
                "unit_amount": "5",
                "unit_type": "jars",
                "gallery": [image_file("one.png"), image_file("two.png")],
            },
        )

        product = InventoryProducts.objects.get()
        self.assertRedirects(response, reverse("product-detail", args=[product.pk]))
        self.assertEqual(product.moreimages.count(), 2)


class PettyCostsTests(TestCase):
    url = reverse("petty-costs")

    def setUp(self):
        self.employee = create_employee()
        self.client.force_login(self.employee)

    def record(self, **overrides):
        data = {"activity": "Deliveries", "transport_cost": "200", "lunch_cost": "150"}
        data.update({"airtime_cost": "50", **overrides})
        return self.client.post(self.url, data)

    def test_requires_login(self):
        self.client.logout()

        self.assertRedirects(self.client.get(self.url), f"{reverse('login')}?next={self.url}")

    def test_recording_an_expense_with_an_other_cost(self):
        self.record(others="Packaging", expense="80")

        entry = PettyCosts.objects.get()
        self.assertEqual(entry.employee, self.employee)
        self.assertEqual(entry.other_costs.get().expense, Decimal("80.00"))

    def test_other_cost_is_optional(self):
        self.record()

        self.assertEqual(PettyCosts.objects.count(), 1)
        self.assertFalse(OtherPettyCosts.objects.exists())

    def test_other_amount_needs_a_description(self):
        response = self.record(expense="80")

        self.assertTrue(response.context["form"].has_error("others"))
        self.assertFalse(PettyCosts.objects.exists())

    def test_totals_cover_only_the_employees_own_expenses(self):
        self.record(others="Packaging", expense="80")
        self.record(transport_cost="100")
        PettyCosts.objects.create(employee=create_employee("87654321"), activity="Not mine")

        totals = self.client.get(self.url).context["totals"]

        self.assertEqual(totals["transport"], Decimal("300.00"))
        self.assertEqual(totals["lunch"], Decimal("300.00"))
        self.assertEqual(totals["other"], Decimal("80.00"))


class LoginTests(TestCase):
    def test_staff_log_in_with_their_id_number(self):
        create_employee("12345678")

        response = self.client.post(
            reverse("login"), {"username": "12345678", "password": "a-strong-pass-123"}
        )

        self.assertRedirects(response, reverse("home"))
