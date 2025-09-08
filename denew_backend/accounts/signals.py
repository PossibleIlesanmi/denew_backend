# Create this file: accounts/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import transaction
from decimal import Decimal
from .models import User, Deposit

@receiver(post_save, sender=User)
def give_signup_bonus(sender, instance, created, **kwargs):
    """
    Give one-time $10 signup bonus to new users.
    Only triggers on user creation and if bonus hasn't been received yet.
    """
    if created and not getattr(instance, 'signup_bonus_received', False):
        with transaction.atomic():
            instance.balance += Decimal('10.00')
            instance.signup_bonus_received = True
            instance.save(update_fields=['balance', 'signup_bonus_received'])

@receiver(pre_save, sender=Deposit)
def track_deposit_status_change(sender, instance, **kwargs):
    """
    Track if deposit status is changing from non-confirmed to confirmed.
    We use pre_save to capture the old status before it's updated.
    """
    if instance.pk:  # Only for existing deposits (updates)
        try:
            old_instance = Deposit.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Deposit.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Deposit)
def update_user_balance_on_deposit(sender, instance, created, **kwargs):
    """
    Update user balance when:
    1. New deposit is created with status='confirmed'
    2. Existing deposit status changes from non-confirmed to 'confirmed'
    
    This prevents double-adding balance on repeated saves.
    """
    if instance.status != 'confirmed':
        return  # Only process confirmed deposits

    should_add_balance = False
    
    if created:
        # New deposit created as confirmed
        should_add_balance = True
    else:
        # Existing deposit - check if status just changed to confirmed
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != 'confirmed':
            should_add_balance = True
    
    if should_add_balance:
        with transaction.atomic():
            user = instance.user
            user.balance += instance.amount
            user.save(update_fields=['balance'])