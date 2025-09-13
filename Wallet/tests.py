from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Wallet


class WalletAPITests(APITestCase):
    def setUp(self):
        self.wallet = Wallet.objects.create(label="Test Wallet", balance=Decimal("100.00"))
        self.get_url = reverse('wallet-detail', kwargs={'wallet_uuid': self.wallet.id})
        self.operation_url = reverse('wallet-operation', kwargs={'wallet_uuid': self.wallet.id})

    def test_get_wallet_balance(self):
        response = self.client.get(self.get_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.wallet.id))
        self.assertEqual(Decimal(response.data['balance']), self.wallet.balance)

    def test_deposit_to_wallet(self):
        data = {"operation_type": "DEPOSIT", "amount": "50.50"}
        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("150.50"))
        self.assertEqual(Decimal(response.data['balance']), self.wallet.balance)

    def test_withdraw_from_wallet(self):
        data = {"operation_type": "WITHDRAW", "amount": "30.00"}
        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("70.00"))

    def test_withdraw_insufficient_funds(self):
        data = {"operation_type": "WITHDRAW", "amount": "200.00"}
        response = self.client.post(self.operation_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Insufficient funds.')
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("100.00"))

    def test_invalid_operation_type(self):
        data = {"operation_type": "INVALID_OP", "amount": "10.00"}
        response = self.client.post(self.operation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_amount(self):
        data = {"operation_type": "DEPOSIT", "amount": "-10.00"}
        response = self.client.post(self.operation_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
