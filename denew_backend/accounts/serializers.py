from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from decimal import Decimal
from rest_framework_simplejwt.tokens import RefreshToken  # Added import
from .models import Task, Deposit, Withdrawal, Invitation, TermsAndConditions, UserProfile, Portfolio, SupportTicket, Product, Campaign

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'location', 'website', 'created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    referral_code = serializers.CharField(required=False, allow_blank=True)
    withdrawal_password = serializers.CharField(write_only=True, min_length=4, max_length=4, required=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'full_name', 'phone_number', 'referral_code', 'withdrawal_password']

    def validate_withdrawal_password(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Withdrawal PIN must be a 4-digit number")
        return value

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists'})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': 'Username already exists'})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            referral_code=validated_data.get('referral_code', ''),
            withdrawal_password=validated_data.get('withdrawal_password', ''),
            balance=Decimal('10.00')  # $10 bonus
        )
        UserProfile.objects.create(user=user)
        return user

    def to_representation(self, instance):
        # Include user data and tokens in the response
        representation = UserSerializer(instance).data
        tokens = RefreshToken.for_user(instance)
        representation['tokens'] = {
            'access': str(tokens.access_token),
            'refresh': str(tokens)
        }
        return representationfrom 


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone_number', 'balance', 'vip_level',
                 'referral_code', 'date_joined', 'last_login', 'email_notifications',
                 'sms_notifications', 'twofa_enabled', 'profile_picture', 'is_verified',
                 'profile', 'withdrawal_password']

    def update(self, instance, validated_data):
        withdrawal_password = validated_data.pop('withdrawal_password', None)
        if withdrawal_password is not None:
            instance.withdrawal_password = withdrawal_password
        return super().update(instance, validated_data)

class UserProfileUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    full_name = serializers.CharField(max_length=255, required=False)
    phone_number = serializers.CharField(max_length=20, required=False)
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, min_length=6, required=False)
    email_notifications = serializers.BooleanField(required=False)
    sms_notifications = serializers.BooleanField(required=False)
    twofa_enabled = serializers.BooleanField(required=False)
    withdrawal_password = serializers.CharField(max_length=4, required=False)

    def validate_email(self, value):
        user = self.context['request'].user
        if value != user.email and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already in use')
        return value

    def validate(self, data):
        if 'new_password' in data and 'current_password' not in data:
            raise serializers.ValidationError({'current_password': 'Current password is required when setting new password'})
        withdrawal_password = data.get('withdrawal_password')
        if withdrawal_password and (not withdrawal_password.isdigit() or len(withdrawal_password) != 4):
            raise serializers.ValidationError({'withdrawal_password': 'Withdrawal PIN must be a 4-digit number'})
        return data

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'icon', 'price', 'is_combined']

class TaskSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Task
        fields = ['id', 'task_type', 'set_number', 'task_number', 'earnings', 'status', 'products']

class CurrentTaskSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Task
        fields = ['id', 'task_type', 'set_number', 'task_number', 'earnings', 'status', 'products', 'created_at', 'completed_at']

class DepositSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Deposit
        fields = ['amount', 'payment_method', 'wallet_address', 'status', 'created_at']

    def validate_amount(self, value):
        if value < 10:
            raise serializers.ValidationError('Minimum deposit is 10 USDT')
        return value

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)

class WithdrawalSerializer(serializers.ModelSerializer):
    withdrawal_password = serializers.CharField(write_only=True)

    class Meta:
        model = Withdrawal
        fields = ['amount', 'payment_method', 'wallet_address', 'withdrawal_password', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        if not user.withdrawal_password:
            raise serializers.ValidationError('Withdrawal PIN not set')
        if data['withdrawal_password'] != user.withdrawal_password:
            raise serializers.ValidationError('Incorrect withdrawal PIN')
        if data['amount'] < 10:
            raise serializers.ValidationError('Minimum withdrawal is 10 USDT')
        return data

    def create(self, validated_data):
        validated_data.pop('withdrawal_password')
        return Withdrawal.objects.create(**validated_data)

class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['referrer', 'referee_email', 'referee_name', 'status', 'created_at']
        read_only_fields = ['referrer', 'status']

    def validate_referee_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered')
        return value

    def create(self, validated_data):
        validated_data['referrer'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)

class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = ['content', 'created_at']

class WithdrawalCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['id', 'user', 'amount', 'payment_method', 'wallet_address', 'status', 'created_at', 'processed_at']
        read_only_fields = ['user', 'amount', 'payment_method', 'wallet_address', 'created_at']

    def update(self, instance, validated_data):
        if validated_data.get('status') in ['completed', 'rejected']:
            instance.processed_at = timezone.now()
        return super().update(instance, validated_data)

class WithdrawalListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Withdrawal
        fields = ['id', 'username', 'user_email', 'amount', 'payment_method', 
                 'wallet_address', 'status', 'created_at', 'processed_at']

class AdminWithdrawalActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    admin_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_action(self, value):
        if value not in ['approve', 'reject']:
            raise serializers.ValidationError('Action must be approve or reject')
        return value

class EnhancedTransactionHistorySerializer(serializers.Serializer):
    deposits = DepositSerializer(many=True, read_only=True)
    withdrawals = WithdrawalListSerializer(many=True, read_only=True)
    total_deposits = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_withdrawals = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    pending_withdrawals = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    def create(self, validated_data):
        raise NotImplementedError("TransactionHistorySerializer is read-only")

    def update(self, instance, validated_data):
        raise NotImplementedError("TransactionHistorySerializer is read-only")

class TransactionHistorySerializer(serializers.Serializer):
    deposits = DepositSerializer(many=True)
    withdrawals = WithdrawalSerializer(many=True)

    def create(self, validated_data):
        raise NotImplementedError("TransactionHistorySerializer is read-only")

    def update(self, instance, validated_data):
        raise NotImplementedError("TransactionHistorySerializer is read-only")

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = ['assets', 'total_value', 'updated_at']

class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['subject', 'message', 'status', 'created_at']

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ['title', 'start_date', 'end_date', 'details', 'terms', 'created_at']