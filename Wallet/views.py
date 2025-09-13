from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .models import Wallet, Transaction
from .serializers import WalletSerializer, OperationSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'wallet_detail': 'GET /api/v1/wallets/<wallet_uuid>/',
        'wallet_operation': 'POST /api/v1/wallets/<wallet_uuid>/operation/',
    })


class WalletDetailView(APIView):
    def get(self, request, wallet_uuid):
        wallet = get_object_or_404(Wallet, pk=wallet_uuid)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)


class WalletOperationView(APIView):
    def post(self, request, wallet_uuid):
        serializer = OperationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        operation_type = validated_data['operation_type']
        amount = validated_data['amount']

        with transaction.atomic():
            wallet = get_object_or_404(Wallet.objects.select_for_update(), pk=wallet_uuid)

            if operation_type == 'WITHDRAW' and wallet.balance < amount:
                return Response({'error': 'Insufficient funds.'}, status=status.HTTP_400_BAD_REQUEST)

            wallet.balance += amount if operation_type == 'DEPOSIT' else -amount
            wallet.save()

            Transaction.objects.create(wallet=wallet, operation_type=operation_type, amount=amount)

        wallet_serializer = WalletSerializer(wallet)
        return Response(wallet_serializer.data, status=status.HTTP_200_OK)
