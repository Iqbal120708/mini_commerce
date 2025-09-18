from concurrent.futures import ThreadPoolExecutor

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from .models import Cart, Product

User = get_user_model()


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.user = User.objects.create_user(
            username="admin", email="admin@gmail.com", password="password123"
        )

        call_command("create_data_product")

    def login(self):
        login = self.client.login(email="admin@gmail.com", password="password123")


# Create your tests here.
class TestAddToCart(BaseTestCase):
    def test_success(self):
        self.login()

        res = self.client.post(reverse("add_to_cart"), data={"product_id": 1})

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("product_list"))
        self.assertEqual(Cart.objects.all().count(), 1)
        self.assertIn(
            "Produk berhasil ditambahkan ke keranjang!", [str(m) for m in msgs]
        )

    def test_add_to_cart_invalid_product_id(self):
        """Gagal tambah produk karena product_id tidak dikirim"""

        self.login()

        res = self.client.post(reverse("add_to_cart"), data={})

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("product_list"))
        self.assertEqual(Cart.objects.all().count(), 0)
        self.assertIn("Produk tidak valid.", [str(m) for m in msgs])

    def test_add_to_cart_product_not_found(self):
        """Gagal tambah produk karena produk tidak ada di database"""

        self.login()

        res = self.client.post(reverse("add_to_cart"), data={"product_id": 100})

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("product_list"))
        self.assertEqual(Cart.objects.all().count(), 0)
        self.assertIn("Produk tidak ditemukan.", [str(m) for m in msgs])

    def test_add_to_cart_cart_limit_reached(self):
        """Gagal tambah produk karena keranjang sudah penuh"""

        self.login()

        for i in range(1, 11):
            res_loop = self.client.post(reverse("add_to_cart"), data={"product_id": i})

        res = self.client.post(reverse("add_to_cart"), data={"product_id": 11})

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("product_list"))
        self.assertEqual(Cart.objects.all().count(), 10)
        self.assertIn(
            (
                "Keranjang Anda sudah mencapai batas maksimum 10 produk. "
                "Hapus beberapa item sebelum menambahkan produk baru."
            ),
            [str(m) for m in msgs],
        )

    def test_add_to_cart_validation_error(self):
        """Gagal tambah produk karena terjadi ValidationError pada Cart"""

        # Error stock product kurang
        product = Product.objects.get(id=1)
        product.stock = 0
        product.save()

        self.login()

        res = self.client.post(reverse("add_to_cart"), data={"product_id": 1})

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("product_list"))
        self.assertEqual(Cart.objects.all().count(), 0)
        self.assertIn(
            f"Produk '{product.name}' ini sudah habis stoknya.", [str(m) for m in msgs]
        )

    def test_add_to_cart_product_already_in_cart(self):
        """Tidak menambah produk baru, karena produk sudah ada di keranjang"""

        self.login()

        res1 = self.client.post(reverse("add_to_cart"), data={"product_id": 1})
        res2 = self.client.post(reverse("add_to_cart"), data={"product_id": 1})

        msgs = list(get_messages(res2.wsgi_request))

        self.assertEqual(res2.status_code, 302)
        self.assertRedirects(res2, reverse("product_list"))
        self.assertEqual(Cart.objects.all().count(), 1)
        self.assertIn(f"Produk sudah ada di keranjang.", [str(m) for m in msgs])


class TestCartList(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.product = Product.objects.get(id=1)
        cls.cart = Cart.objects.create(product=cls.product, user=cls.user)

        cls.user2 = User.objects.create_user(
            username="user", email="user@gmail.com", password="password123"
        )
        cls.cart2 = Cart.objects.create(product=cls.product, user=cls.user2)

    def test_cart_list_no_items_selected(self):
        """Gagal checkout karena tidak ada item yang dipilih"""

        self.login()

        res = self.client.post(
            reverse("cart_list"), data={"selected[]": [], "qty_1": 1}
        )

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("cart_list"))
        self.assertIn("Tidak ada item yang dipilih", [str(m) for m in msgs])

    def test_cart_list_invalid_cart_id(self):
        """Gagal checkout karena item keranjang tidak ditemukan"""

        self.login()

        res = self.client.post(
            reverse("cart_list"), data={"selected[]": [10], "qty_10": 1}
        )

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("cart_list"))
        self.assertIn("Item keranjang tidak ditemukan", [str(m) for m in msgs])

    def test_cart_list_quantity_less_than_one(self):
        """Gagal checkout karena jumlah pembelian kurang dari 1"""

        self.login()

        res = self.client.post(
            reverse("cart_list"), data={"selected[]": [1], "qty_1": 0}
        )

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("cart_list"))
        self.assertIn(
            "Jumlah pembelian Sambal Matah Bali minimal 1", [str(m) for m in msgs]
        )

    def test_cart_list_invalid_quantity_input(self):
        """Gagal checkout karena jumlah pembelian tidak valid"""

        self.login()

        res = self.client.post(
            reverse("cart_list"), data={"selected[]": [1], "qty_1": "test"}
        )

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("cart_list"))
        self.assertIn(
            "Jumlah pembelian Sambal Matah Bali tidak valid", [str(m) for m in msgs]
        )

    def test_cart_list_stock_not_enough(self):
        """Gagal checkout karena stok produk tidak mencukupi"""

        self.login()

        res = self.client.post(
            reverse("cart_list"), data={"selected[]": [1], "qty_1": 100}
        )

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("cart_list"))
        self.assertIn("Stok Sambal Matah Bali tidak mencukupi", [str(m) for m in msgs])

    # def test_cart_list_stock_update_error(self):
    #     """Gagal checkout karena terjadi error saat update stok produk"""

    #     res = self.client.post(reverse("cart_list"), data={"selected[]":[1], "qty_1":"test"})

    #     msgs = list(get_messages(res.wsgi_request))

    #     self.assertEqual(res.status_code, 302)
    #     self.assertRedirects(res, reverse("cart_list"))
    #     self.assertIn("Stok untuk Sambal Matah Bali tidak mencukupi" ,[str(m) for m in msgs])

    def test_cart_list_success_order(self):
        """Berhasil checkout dengan data valid"""

        self.login()

        res = self.client.post(
            reverse("cart_list"), data={"selected[]": [1], "qty_1": 1}
        )

        msgs = list(get_messages(res.wsgi_request))

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, reverse("cart_list"))
        self.assertIn("Pesanan berhasil diproses", [str(m) for m in msgs])

    # def test_race_condition(self):
    #     """
    #     Simulasi 2 user checkout barengan → stok tidak boleh minus
    #     """

    #     self.product.stock = 5
    #     self.product.save()

    #     def do_checkout(user, cart_id):
    #         client = Client()
    #         client.force_login(user)
    #         return self.client.post(
    #             reverse("cart_list"),
    #             data={f"selected[]": [cart_id], f"qty_{cart_id}": 3},
    #         )

    #     # Jalankan 2 request "paralel"
    #     with ThreadPoolExecutor(max_workers=2) as executor:
    #         res1 = executor.submit(do_checkout, self.user, self.cart.id)
    #         res2 = executor.submit(do_checkout, self.user2, self.cart2.id)

    #     r1 = res1.result()
    #     r2 = res2.result()

    #     # Refresh stok produk dari DB
    #     self.product.refresh_from_db()
    #     print(self.product.stock)

    #     # Pastikan stok tidak minus
    #     self.assertGreaterEqual(self.product.stock, 0)

    #     # Pastikan salah satu gagal
    #     msgs1 = [str(m) for m in r1.wsgi_request._messages]
    #     msgs2 = [str(m) for m in r2.wsgi_request._messages]

    #     self.assertTrue(
    #         "Stok Produk A tidak mencukupi" in msgs1
    #         or "Stok Produk A tidak mencukupi" in msgs2
    #     )
