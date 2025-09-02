from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Sum
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from .serializers import (
    WithdrawalCompletionSerializer, WithdrawalListSerializer, AdminWithdrawalActionSerializer,
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer, TaskSerializer,
    CurrentTaskSerializer, ProductSerializer, DepositSerializer, WithdrawalSerializer,
    InvitationSerializer, TermsSerializer, PortfolioSerializer, SupportTicketSerializer,
    TransactionHistorySerializer, EnhancedTransactionHistorySerializer, CampaignSerializer
)
from .models import User, Task, Product, Deposit, Withdrawal, Invitation, TermsAndConditions, UserProfile, Portfolio, SupportTicket, Campaign
from django.utils import timezone
from datetime import timedelta
import random
import string
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user).data
        return Response({
            'message': 'Registration successful! You have received a $50 bonus.',
            'user': user_data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    return Response({
        'message': 'Registration failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        user_data = UserSerializer(user).data
        return Response({
            'message': 'Login successful',
            'user': user_data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)
    return Response({
        'message': 'Login failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data.get('refresh_token')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': 'Logout failed', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user_data = UserSerializer(request.user).data
    return Response({'user': user_data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user
    data = request.data
    user_profile, created = UserProfile.objects.get_or_create(user=user)
    email = data.get('email')
    if email and email != user.email:
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already in use'}, status=status.HTTP_400_BAD_REQUEST)
        user.email = email
    full_name = data.get('full_name')
    if full_name is not None:
        user.full_name = full_name
    phone_number = data.get('phone_number')
    if phone_number is not None:
        user.phone_number = phone_number
    withdrawal_password = data.get('withdrawal_password')
    if withdrawal_password is not None:
        if not withdrawal_password.isdigit() or len(withdrawal_password) != 4:
            return Response({'error': 'Withdrawal PIN must be a 4-digit number'}, status=status.HTTP_400_BAD_REQUEST)
        user.withdrawal_password = withdrawal_password
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    if new_password:
        if not current_password or not authenticate(username=user.username, password=current_password):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
    if 'email_notifications' in data:
        user.email_notifications = data['email_notifications']
    if 'sms_notifications' in data:
        user.sms_notifications = data['sms_notifications']
    if 'twofa_enabled' in data:
        user.twofa_enabled = data['twofa_enabled']
    profile_picture = request.FILES.get('profile_picture')
    if profile_picture:
        file_path = os.path.join(settings.MEDIA_ROOT, 'profile_pictures', f'{user.username}_{profile_picture.name}')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in profile_picture.chunks():
                destination.write(chunk)
        user.profile_picture = f'/media/profile_pictures/{user.username}_{profile_picture.name}'
    profile_data = data.get('profile', {})
    if profile_data:
        if 'avatar' in profile_data:
            user_profile.avatar = profile_data['avatar']
        if 'bio' in profile_data:
            user_profile.bio = profile_data['bio']
        if 'location' in profile_data:
            user_profile.location = profile_data['location']
        if 'website' in profile_data:
            user_profile.website = profile_data['website']
    bio = data.get('bio')
    if bio is not None:
        user_profile.bio = bio
    location = data.get('location')
    if location is not None:
        user_profile.location = location
    website = data.get('website')
    if website is not None:
        user_profile.website = website
    avatar = data.get('avatar')
    if avatar is not None:
        user_profile.avatar = avatar
    try:
        user.save()
        user_profile.save()
        return Response({
            'message': 'Profile updated successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_data(request):
    user = request.user
    total_earnings = Task.objects.filter(user=user, status='completed').aggregate(total=Sum('earnings'))['total'] or 0
    total_tasks = Task.objects.filter(user=user).count()
    team_members = Invitation.objects.filter(referrer=user).count()
    user_data = UserSerializer(user).data
    return Response({
        'user': user_data,
        'total_earnings': total_earnings,
        'total_tasks': total_tasks,
        'team_members': team_members
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tasks(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_task(request):
    user = request.user
    current_set = user.current_set
    if not current_set:
        return Response({'task': None}, status=status.HTTP_200_OK)
    task = Task.objects.filter(user=user, set_number=current_set, status='pending').order_by('task_number').first()
    if not task:
        task = Task.objects.filter(user=user, set_number=current_set, status='in-progress').order_by('task_number').first()
    if not task:
        return Response({'task': None}, status=status.HTTP_200_OK)
    serializer = CurrentTaskSerializer(task)
    return Response({'task': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_products(request):
    products = list(Product.objects.all())
    if len(products) < 4:
        return Response({'error': 'Not enough products available'}, status=status.HTTP_400_BAD_REQUEST)
    selected_products = random.sample(products, 4)
    serializer = ProductSerializer(selected_products, many=True)
    return Response({'products': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task_set(request):
    user = request.user
    if user.balance < 100:
        return Response({'error': 'Minimum balance of 100 USDT required'}, status=status.HTTP_400_BAD_REQUEST)
    if Task.objects.filter(user=user, status='pending').exists():
        return Response({'error': 'Complete existing tasks before starting a new set'}, status=status.HTTP_400_BAD_REQUEST)
    user.current_set += 1
    user.tasks_completed = 0
    user.tasks_reset_required = False
    user.save()
    task_type = 'combined' if user.balance > 500 else 'normal'
    earnings_rate = {'VIP 0': 0.005, 'VIP 1': 0.005, 'VIP 2': 0.01, 'VIP 3': 0.015, 'VIP 4': 0.02}
    earnings = user.balance * earnings_rate.get(user.vip_level, 0.005) * (5 if task_type == 'combined' else 1)
    products = random.sample(list(Product.objects.all()), min(4 if task_type == 'combined' else 1, Product.objects.count()))
    task = Task.objects.create(
        user=user,
        task_type=task_type,
        set_number=user.current_set,
        task_number=1,
        earnings=earnings,
        status='pending'
    )
    task.products.set(products)
    return Response({
        'message': 'Task set started',
        'task_type': task_type
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task(request):
    user = request.user
    task_id = request.data.get('task_id')
    try:
        task = Task.objects.get(id=task_id, user=user, status='pending')
        if (timezone.now() - task.created_at).total_seconds() > 2 * 3600:
            task.merchant_complaint = True
            task.save()
            return Response({'error': 'Task expired (2-hour limit)'}, status=status.HTTP_400_BAD_REQUEST)
        task.status = 'in-progress'
        task.save()
        return Response({
            'message': 'Task started',
            'task_type': task.task_type
        }, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_task(request):
    user = request.user
    task_id = request.data.get('task_id')
    try:
        task = Task.objects.get(id=task_id, user=user, status='in-progress')
        if (timezone.now() - task.created_at).total_seconds() > 2 * 3600:
            task.merchant_complaint = True
            task.save()
            return Response({'error': 'Task expired (2-hour limit)'}, status=status.HTTP_400_BAD_REQUEST)
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        user.balance += task.earnings
        user.tasks_completed += 1
        user.can_invite = user.tasks_completed >= 40
        user.tasks_reset_required = user.tasks_completed >= 40
        user.save()
        if user.tasks_completed < 40:
            task_type = 'combined' if user.balance > 500 else 'normal'
            earnings_rate = {'VIP 0': 0.005, 'VIP 1': 0.005, 'VIP 2': 0.01, 'VIP 3': 0.015, 'VIP 4': 0.02}
            earnings = user.balance * earnings_rate.get(user.vip_level, 0.005) * (5 if task_type == 'combined' else 1)
            products = random.sample(list(Product.objects.all()), min(4 if task_type == 'combined' else 1, Product.objects.count()))
            new_task = Task.objects.create(
                user=user,
                task_type=task_type,
                set_number=user.current_set,
                task_number=task.task_number + 1,
                earnings=earnings,
                status='pending'
            )
            new_task.products.set(products)
        return Response({
            'message': 'Task completed successfully',
            'current_task': user.tasks_completed,
            'earnings': task.earnings
        }, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_account(request):
    user = request.user
    if Task.objects.filter(user=user, status__in=['pending', 'in-progress']).exists():
        return Response({'error': 'Complete all tasks before resetting'}, status=status.HTTP_400_BAD_REQUEST)
    if Withdrawal.objects.filter(user=user, status='pending').exists():
        return Response({'error': 'Complete all withdrawals before resetting'}, status=status.HTTP_400_BAD_REQUEST)
    user.balance = 50.00
    user.current_set = 0
    user.tasks_completed = 0
    user.can_invite = False
    user.tasks_reset_required = False
    Task.objects.filter(user=user).delete()
    user.save()
    return Response({'message': 'Account reset successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_friend(request):
    if Task.objects.filter(user=request.user, status__in=['pending', 'in-progress']).exists():
        return Response({'error': 'Complete all tasks before inviting'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = InvitationSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        invitation = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_code(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        code = ''.join(random.choices(string.digits, k=6))
        verification_codes[email] = {'code': code, 'expires': timezone.now() + timedelta(minutes=10)}
        send_mail(
            'Denew PIN Reset Code',
            f'Your verification code is {code}. It expires in 10 minutes.',
            'from@denew.com',
            [email],
            fail_silently=False,
        )
        return Response({'message': 'Verification code sent'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_code(request):
    email = request.data.get('email')
    code = request.data.get('code')
    if email not in verification_codes:
        return Response({'error': 'No verification code sent for this email'}, status=status.HTTP_400_BAD_REQUEST)
    stored = verification_codes[email]
    if timezone.now() > stored['expires']:
        del verification_codes[email]
        return Response({'error': 'Code expired'}, status=status.HTTP_400_BAD_REQUEST)
    if stored['code'] != code:
        return Response({'error': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Code verified'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_pin(request):
    email = request.data.get('email')
    pin = request.data.get('pin')
    if email not in verification_codes:
        return Response({'error': 'Verification code not validated'}, status=status.HTTP_400_BAD_REQUEST)
    if not pin or not pin.isdigit() or len(pin) != 4:
        return Response({'error': 'PIN must be a 4-digit number'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
        user.withdrawal_password = pin
        user.save()
        del verification_codes[email]
        return Response({'message': 'PIN reset successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_withdrawal_pin(request):
    pin = request.data.get('pin')
    if not pin or not pin.isdigit() or len(pin) != 4:
        return Response({'error': 'PIN must be a 4-digit number'}, status=status.HTTP_400_BAD_REQUEST)
    request.user.withdrawal_password = pin
    request.user.save()
    return Response({'message': 'Withdrawal PIN set successfully'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_deposit(request):
    serializer = DepositSerializer(data=request.data)
    if serializer.is_valid():
        deposit = serializer.save(user=request.user)
        request.user.balance += deposit.amount
        request.user.save()
        referrer = User.objects.filter(invitations_sent__referee_email=request.user.email, invitations_sent__status='accepted').first()
        if referrer:
            referrer.balance += deposit.amount * 0.1
            referrer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_withdrawal(request):
    user = request.user
    if Task.objects.filter(user=user, status__in=['pending', 'in-progress']).exists():
        return Response({'error': 'Complete all tasks before withdrawing'}, status=status.HTTP_400_BAD_REQUEST)
    pin = request.data.get('withdrawal_password')
    if user.withdrawal_password != pin:
        return Response({'error': 'Invalid withdrawal PIN'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = WithdrawalSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        if user.balance < serializer.validated_data['amount']:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal = serializer.save(user=user)
        user.balance -= withdrawal.amount
        user.save()
        return Response({
            'message': 'Withdrawal request submitted successfully',
            'withdrawal': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_invitations(request):
    invitations = Invitation.objects.filter(referrer=request.user).order_by('-created_at')
    serializer = InvitationSerializer(invitations, many=True)
    team_size = invitations.count()
    active_members = 0
    referral_earnings = 0
    for invitation in invitations:
        try:
            referee = User.objects.get(email=invitation.referee_email)
            if referee.last_login and (timezone.now() - referee.last_login).days <= 30:
                active_members += 1
            deposits = Deposit.objects.filter(user=referee, status='confirmed').aggregate(total=Sum('amount'))['total'] or 0
            referral_earnings += deposits * 0.1
        except User.DoesNotExist:
            continue
    return Response({
        'invitations': serializer.data,
        'team_size': team_size,
        'active_members': active_members,
        'referral_earnings': round(referral_earnings, 2)
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_withdrawals(request):
    if request.user.is_staff:
        withdrawals = Withdrawal.objects.all().order_by('-created_at')
    else:
        withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-created_at')
    serializer = WithdrawalListSerializer(withdrawals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_withdrawal_details(request, withdrawal_id):
    try:
        if request.user.is_staff:
            withdrawal = Withdrawal.objects.get(id=withdrawal_id)
        else:
            withdrawal = Withdrawal.objects.get(id=withdrawal_id, user=request.user)
        serializer = WithdrawalListSerializer(withdrawal)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Withdrawal.DoesNotExist:
        return Response({'error': 'Withdrawal not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_withdrawal(request, withdrawal_id):
    try:
        withdrawal = Withdrawal.objects.get(id=withdrawal_id)
        if withdrawal.status != 'pending':
            return Response({
                'error': f'Cannot modify withdrawal with status: {withdrawal.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        action = request.data.get('action', 'approve')
        admin_notes = request.data.get('admin_notes', '')
        if action == 'approve':
            withdrawal.status = 'completed'
            withdrawal.processed_at = timezone.now()
            message = 'Withdrawal approved successfully'
        elif action == 'reject':
            withdrawal.status = 'rejected'
            withdrawal.processed_at = timezone.now()
            withdrawal.user.balance += withdrawal.amount
            withdrawal.user.save()
            message = 'Withdrawal rejected and amount refunded'
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        withdrawal.save()
        serializer = WithdrawalListSerializer(withdrawal)
        return Response({
            'message': message,
            'withdrawal': serializer.data
        }, status=status.HTTP_200_OK)
    except Withdrawal.DoesNotExist:
        return Response({'error': 'Withdrawal not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_complete_withdrawals(request):
    withdrawal_ids = request.data.get('withdrawal_ids', [])
    action = request.data.get('action', 'approve')
    if not withdrawal_ids:
        return Response({'error': 'No withdrawal IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        withdrawals = Withdrawal.objects.filter(id__in=withdrawal_ids, status='pending')
        if not withdrawals.exists():
            return Response({'error': 'No pending withdrawals found'}, status=status.HTTP_404_NOT_FOUND)
        updated_count = 0
        for withdrawal in withdrawals:
            if action == 'approve':
                withdrawal.status = 'completed'
                withdrawal.processed_at = timezone.now()
            elif action == 'reject':
                withdrawal.status = 'rejected'
                withdrawal.processed_at = timezone.now()
                withdrawal.user.balance += withdrawal.amount
                withdrawal.user.save()
            withdrawal.save()
            updated_count += 1
        return Response({
            'message': f'{updated_count} withdrawals {action}d successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_enhanced_transaction_history(request):
    user = request.user
    deposits = Deposit.objects.filter(user=user).order_by('-created_at')
    withdrawals = Withdrawal.objects.filter(user=user).order_by('-created_at')
    total_deposits = deposits.filter(status='confirmed').aggregate(total=Sum('amount'))['total'] or 0
    total_withdrawals = withdrawals.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    pending_withdrawals = withdrawals.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0
    data = {
        'deposits': deposits,
        'withdrawals': withdrawals,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'pending_withdrawals': pending_withdrawals
    }
    serializer = EnhancedTransactionHistorySerializer(data)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_terms(request):
    try:
        terms = TermsAndConditions.objects.latest('created_at')
        return Response(TermsSerializer(terms).data, status=status.HTTP_200_OK)
    except TermsAndConditions.DoesNotExist:
        return Response({'error': 'Terms not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio(request):
    portfolio = Portfolio.objects.get_or_create(user=request.user)[0]
    serializer = PortfolioSerializer(portfolio)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_portfolio(request):
    portfolio = Portfolio.objects.get_or_create(user=request.user)[0]
    serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transaction_history(request):
    deposits = Deposit.objects.filter(user=request.user).order_by('-created_at')
    withdrawals = Withdrawal.objects.filter(user=request.user).order_by('-created_at')
    serializer = TransactionHistorySerializer({'deposits': deposits, 'withdrawals': withdrawals}, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_support_ticket(request):
    serializer = SupportTicketSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_balance(request):
    return Response({'balance': request.user.balance}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vip_level(request):
    return Response({'vip_level': request.user.vip_level}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_campaigns(request):
    campaigns = Campaign.objects.filter(is_active=True, end_date__gte=timezone.now()).order_by('-created_at')
    serializer = CampaignSerializer(campaigns, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)