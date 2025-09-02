from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    vip_level = models.CharField(
        max_length=50,
        choices=[('VIP 0', 'VIP 0'), ('VIP 1', 'VIP 1'), ('VIP 2', 'VIP 2'), ('VIP 3', 'VIP 3'), ('VIP 4', 'VIP 4')],
        default='VIP 0'
    )
    can_invite = models.BooleanField(default=False)
    current_set = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    tasks_reset_required = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    twofa_enabled = models.BooleanField(default=False)
    profile_picture = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    withdrawal_password = models.CharField(max_length=4, blank=True)

    class Meta:
        db_table = 'accounts_user'

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_userprofile'

class Product(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_combined = models.BooleanField(default=False)

    class Meta:
        db_table = 'accounts_product'

class Campaign(models.Model):
    title = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    details = models.TextField()
    terms = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_campaign'
        ordering = ['-created_at']

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('in-progress', 'In Progress'), ('completed', 'Completed')],
        default='pending'
    )
    task_type = models.CharField(
        max_length=50,
        choices=[('normal', 'Normal'), ('combined', 'Combined')],
        default='normal'
    )
    merchant_complaint = models.BooleanField(default=False)
    set_number = models.IntegerField(default=1)
    task_number = models.IntegerField(default=1)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    products = models.ManyToManyField(Product, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'accounts_task'
        unique_together = ('user', 'set_number', 'task_number')

class Invitation(models.Model):
    referrer = models.ForeignKey(User, related_name='invitations_sent', on_delete=models.CASCADE)
    referee_email = models.EmailField()
    referee_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_invitation'

class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='usdt')
    wallet_address = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_deposit'

class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='usdt')
    wallet_address = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('rejected', 'Rejected')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'accounts_withdrawal'

class TermsAndConditions(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_terms'

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assets = models.JSONField(default=dict)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_portfolio'

class SupportTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('open', 'Open'), ('in-progress', 'In Progress'), ('closed', 'Closed')],
        default='open'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'accounts_supportticket'