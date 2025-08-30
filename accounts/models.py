from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vip_level = models.CharField(max_length=50, default='VIP 1')
    referral_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    withdrawal_password = models.CharField(max_length=4, blank=True)
    wallet_address = models.CharField(max_length=100, blank=True, null=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    twofa_enabled = models.BooleanField(default=False)
    profile_picture = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.username.upper() + str(timezone.now().timestamp())[-4:]
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    task_type = models.CharField(max_length=50, choices=[('normal', 'Normal'), ('combined', 'Combined')])
    earnings = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Task {self.id} by {self.user.username}"

class Deposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposits')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[('usdt', 'USDT')], default='usdt')
    wallet_address = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Deposit {self.id} by {self.user.username} - {self.amount} {self.payment_method.upper()}"

class Withdrawal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=42)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Withdrawal {self.id} by {self.user.username} - {self.amount} {self.payment_method.upper()}"

class Invitation(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals')
    referee_email = models.EmailField()
    referee_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Invitation from {self.referrer.username} to {self.referee_email}"

    class Meta:
        unique_together = ('referrer', 'referee_email')

class TermsAndConditions(models.Model):
    content = models.TextField()
    version = models.CharField(max_length=10, default='1.0')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Terms v{self.version}"

    class Meta:
        ordering = ['-created_at']

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
    assets = models.TextField(blank=True)  # JSON or comma-separated list of assets
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Portfolio for {self.user.username}"

class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=100)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket {self.id} by {self.user.username} - {self.subject}"

    class Meta:
        ordering = ['-created_at']