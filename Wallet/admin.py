from django.contrib import admin
from .models import Wallet, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('label', 'id', 'balance')
    readonly_fields = ('id',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'operation_type', 'amount', 'timestamp')
    list_filter = ('wallet', 'operation_type', 'timestamp')
    search_fields = ('wallet__label', 'operation_type')
    readonly_fields = ('timestamp',)
