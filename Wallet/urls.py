from django.urls import path
from .views import WalletDetailView, WalletOperationView, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('wallets/<uuid:wallet_uuid>/', WalletDetailView.as_view(), name='wallet-detail'),
    path('wallets/<uuid:wallet_uuid>/operation/', WalletOperationView.as_view(), name='wallet-operation'),
]
